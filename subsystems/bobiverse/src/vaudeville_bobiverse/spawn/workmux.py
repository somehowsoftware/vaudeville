from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

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
        "origin/main",
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
    # `workmux add`'s first-run wizard reads the terminal and blocks; a spawn launched
    # from a terminal would hand it down and hang. Every wizard gate early-returns when
    # stdin is not a tty, and this invocation reads stdin for nothing else, so the call
    # is non-interactive by construction: a closed stdin the runner only forwards.
    stdin: int = subprocess.DEVNULL


def workmux_invocation(
    seeded: SeededClone,
    worktree: str,
    launcher_path: Path,
    agent_script: Path,
) -> WorkmuxInvocation:
    argv = workmux_add_argv(worktree, launcher_path, seeded.foundation_session, str(agent_script))
    return WorkmuxInvocation(argv=argv, cwd=seeded.clone)


def run_workmux(invocation: WorkmuxInvocation) -> None:
    try:
        result = subprocess.run(
            invocation.argv, cwd=invocation.cwd, check=False, stdin=invocation.stdin
        )
    except FileNotFoundError:
        print(
            "Error: `workmux` not found on PATH. `vv spawn` requires it for worktree creation.",
            file=sys.stderr,
        )
        sys.exit(WORKMUX_MISSING_EXIT)
    if result.returncode != 0:
        sys.exit(result.returncode)
