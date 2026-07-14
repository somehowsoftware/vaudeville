from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from vaudeville_cue import claude_config, claude_projects
from vaudeville_cue.checkpoint_layout import CheckpointLayout, checkpoint_layout
from vaudeville_cue.checkpoint_plan import (
    CHECKPOINT_REFUSED_EXIT,
    SESSION_ID_ENV,
    TRANSCRIPT_UNRESOLVED,
    CheckpointRefusal,
    plan_checkpoint,
)
from vaudeville_cue.checkpoint_runner import run_plan
from vaudeville_cue.digest import Section, accumulate, render
from vaudeville_cue.digest_store import deserialize_sections
from vaudeville_cue.operator_turns import operator_turns, unconfirmed_queued_messages
from vaudeville_cue.transcript import (
    messages_from_transcript_lines,
    queue_operations_from_transcript_lines,
)


def deployed_skills(skills_root: Path) -> set[str]:
    if not skills_root.is_dir():
        return set()
    return {child.name for child in skills_root.iterdir() if (child / "SKILL.md").is_file()}


def digest_sections(
    transcript_dir: Path, session_id: str | None, *, prior_store: Path
) -> tuple[Section, ...] | None:
    if not session_id:
        return None
    transcript = transcript_dir / f"{session_id}.jsonl"
    if not transcript.is_file():
        return None
    # A JSONL transcript is newline-delimited; split on "\n" rather than splitlines(),
    # which also breaks on U+2028/U+0085 etc. that a JSON string value may carry; an
    # over-split would desync every line locator the resumed Bob is told to follow.
    lines = transcript.read_text(encoding="utf-8").split("\n")
    turns = operator_turns(messages_from_transcript_lines(lines))
    remnants = unconfirmed_queued_messages(queue_operations_from_transcript_lines(lines), turns)
    return accumulate(
        _prior_sections(prior_store), Section(str(transcript), tuple(turns), tuple(remnants))
    )


def _prior_sections(prior_store: Path) -> tuple[Section, ...]:
    # The durable store is data we wrote, but reading it is still an I/O boundary: a
    # store left half-written by a killed checkpoint, or hand-edited, is corrupt input.
    # Refuse cleanly before the irreversible clear rather than abort with a traceback,
    # and never silently treat it as empty; that would drop the earlier sessions' turns.
    if not prior_store.is_file():
        return ()
    try:
        return deserialize_sections(prior_store.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as corrupt:
        print(
            f"Error: the Digest store at {prior_store} is corrupt and cannot be read "
            f"({corrupt}); a checkpoint cannot safely accumulate onto it. Investigate or "
            f"remove {prior_store}, then retry.",
            file=sys.stderr,
        )
        sys.exit(CHECKPOINT_REFUSED_EXIT)


def run_digest() -> None:
    _worktree, layout, transcript_dir = _checkpoint_locations()
    sections = digest_sections(
        transcript_dir, os.environ.get(SESSION_ID_ENV), prior_store=layout.digest
    )
    if sections is None:
        print(f"Error: {TRANSCRIPT_UNRESOLVED}", file=sys.stderr)
        sys.exit(CHECKPOINT_REFUSED_EXIT)
    print(render(sections), end="")


def run_checkpoint(continuation: str | None, worktree_name: str | None, carryover: str) -> None:
    worktree_root, layout, transcript_dir = _checkpoint_locations()
    outcome = plan_checkpoint(
        continuation,
        carryover,
        digest_sections(transcript_dir, os.environ.get(SESSION_ID_ENV), prior_store=layout.digest),
        deployed_skills=deployed_skills(claude_config.skills_root()),
        layout=layout,
        pane=worktree_name or worktree_root.name,
    )
    if isinstance(outcome, CheckpointRefusal):
        print(f"Error: {outcome.message}", file=sys.stderr)
        sys.exit(outcome.exit_code)
    run_plan(outcome)


def _checkpoint_locations() -> tuple[Path, CheckpointLayout, Path]:
    worktree_root = _worktree_root()
    return (
        worktree_root,
        checkpoint_layout(worktree_root),
        claude_projects.project_directory(
            worktree_root, projects_root=claude_projects.projects_root()
        ),
    )


def _worktree_root() -> Path:
    toplevel = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False,
    )
    if toplevel.returncode != 0:
        print(
            "Error: this command must run inside the Bob's worktree "
            f"({toplevel.stderr.strip() or 'git rev-parse failed'}).",
            file=sys.stderr,
        )
        sys.exit(CHECKPOINT_REFUSED_EXIT)
    # Claude Code names a session's project directory from the realpath-resolved
    # cwd, and that directory name is what gets encoded into the transcript slug. A
    # root reached through a symlink (e.g. macOS routing $TMPDIR via /var ->
    # /private/var) would otherwise encode a slug the session was never written
    # under. Resolve to match, in parity with prime's own guard.
    return Path(toplevel.stdout.strip()).resolve()
