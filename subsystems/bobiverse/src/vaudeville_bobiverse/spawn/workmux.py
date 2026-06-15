"""Allocate the working surface a Bob runs on: the ``workmux add`` invocation.

``workmux_invocation`` builds the whole call as a value — argv plus the cwd the
fork resolves against — from a ``SeededClone``. Taking the witness rather than a
bare session id is what makes seed-before-fork structural: there is no way to
name the ``--fork`` target except through a clone the Foundation was seeded into.
``run_workmux`` is the dumb shell that performs the decided invocation; its only
patchable surface is the subprocess syscall.
"""

from __future__ import annotations

import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from vaudeville_bobiverse.spawn.agent import agent_command
from vaudeville_bobiverse.spawn.seed import SeededClone

WORKMUX_MISSING_EXIT = 127


def workmux_add_argv(
    worktree: str, launcher_path: Path, foundation_session: str, agent: str
) -> list[str]:
    return [
        "workmux",
        "add",
        worktree,
        "--base",
        "main",
        "--name",
        worktree,
        "--prompt-file",
        str(launcher_path),
        "--background",
        f"--fork={foundation_session}",
        "--agent",
        agent,
    ]


@dataclass(frozen=True)
class WorkmuxInvocation:
    argv: list[str]
    cwd: Path


def workmux_invocation(
    seeded: SeededClone,
    worktree: str,
    launcher_path: Path,
    propagated_environment: Sequence[tuple[str, str]],
) -> WorkmuxInvocation:
    agent = agent_command(propagated_environment, worktree)
    argv = workmux_add_argv(worktree, launcher_path, seeded.foundation_session, agent)
    return WorkmuxInvocation(argv=argv, cwd=seeded.clone)


def run_workmux(invocation: WorkmuxInvocation) -> None:
    try:
        result = subprocess.run(invocation.argv, cwd=invocation.cwd, check=False)
    except FileNotFoundError:
        print(
            "Error: `workmux` not found on PATH. `vv spawn` requires it for worktree creation.",
            file=sys.stderr,
        )
        sys.exit(WORKMUX_MISSING_EXIT)
    if result.returncode != 0:
        sys.exit(result.returncode)
