from __future__ import annotations

import tempfile
import uuid
from pathlib import Path

from vaudeville_bobiverse import claude_projects
from vaudeville_bobiverse.data_dir import data_dir
from vaudeville_bobiverse.spawn import clearing, standup, trust
from vaudeville_bobiverse.spawn.refusal import Refusal, refuse, refuse_or_clear

ADHOC_NOTE = (
    "You are a Bob, forked ad-hoc into this Component with no Assignment. "
    "Nothing in the backlog drives this session and no Brief frames it; the "
    "operator forked you directly to work something out in conversation.\n\n"
    "Do not start work or guess at a task. Wait for the operator's first "
    "instruction, then act on it. When the work is finished, tear down with "
    "`/closeout none`.\n"
)


def adhoc_worktree_name(prefix: str, suffix: str) -> str:
    return f"{prefix.lower()}-adhoc-{suffix}"


def write_adhoc_note() -> Path:
    # The ad-hoc note is the bob's launch turn, the Brief's stand-in for an
    # Assignment-less Bob. It belongs to no working tree, so it is written to a tempfile a
    # `git clean` of the clone can never reach.
    with tempfile.NamedTemporaryFile("w", prefix="bob-adhoc-", suffix=".md", delete=False) as note:
        note.write(ADHOC_NOTE)
        return Path(note.name)


def fork_adhoc_bob(
    prefix: str,
    *,
    data_files_root: Path,
    projects_root: Path,
    claude_config_file: Path,
) -> None:
    # No preflight here: preflight weighs an Assignment, and an ad-hoc Bob has none.
    outcome = refuse_or_clear(clearing.SPAWN_CLEARANCES, clearing.Clearing(prefix, data_files_root))
    if isinstance(outcome, Refusal):
        refuse(outcome)
    ready = outcome.cleared()
    standup.stand_up_session(
        ready.foundation_session,
        target=ready.target,
        worktree=adhoc_worktree_name(prefix, uuid.uuid4().hex[:6]),
        prompt_file=write_adhoc_note(),
        config_file=claude_config_file,
        projects_root=projects_root,
        data_files_root=data_files_root,
    )


def bob(prefix: str) -> None:
    # The single composition root for bob: `vv bob` and `vaudeville bob` both
    # enter here, resolving the host's real locations in one place the way
    # spawn's composition root does.
    fork_adhoc_bob(
        prefix,
        data_files_root=data_dir(),
        projects_root=claude_projects.projects_root(),
        claude_config_file=trust.claude_config_file(),
    )
