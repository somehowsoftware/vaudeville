from __future__ import annotations

import sys
import tempfile
import uuid
from pathlib import Path

from vaudeville_bobiverse import claude_projects, foundation, refresh
from vaudeville_bobiverse.data_dir import data_dir
from vaudeville_bobiverse.managed_clones import managed_clones
from vaudeville_bobiverse.spawn import standup, target_repo, trust
from vaudeville_bobiverse.spawn.decision import SpawnRefusal, spawn_decision

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
    clones: list[Path],
) -> None:
    # Spawn without the backlog: no preflight gate and no Brief, because no
    # Assignment drives this Bob. Foundation readiness is still the law, so reuse
    # spawn's decision rather than re-inline the refusal.
    target = target_repo.target_repo_for_prefix(prefix)
    decided = spawn_decision(prefix, foundation.lookup(prefix, data_files_root=data_files_root))
    if isinstance(decided, SpawnRefusal):
        print(decided.message, file=sys.stderr)
        sys.exit(decided.exit_code)
    refresh.refresh_clones(clones)
    standup.stand_up_session(
        decided.foundation_session,
        target=target,
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
        clones=managed_clones(),
    )
