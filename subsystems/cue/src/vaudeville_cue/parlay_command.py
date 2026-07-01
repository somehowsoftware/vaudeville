from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import NoReturn

from vaudeville_cue.parlay_github import GithubError, current_repo

# The plumbing every parlay command runs on entry: which repo it acts on, where its ledger lives,
# and how it bails. Resolving the repo and the worktree are preconditions — a command that cannot
# establish them fails loudly rather than guessing.

_SCRATCH_DIRNAME = ".scratch"


def resolved_repo(repo: str | None) -> str:
    try:
        return repo or current_repo()
    except GithubError as failure:
        fail(failure)


def scratch_root() -> Path:
    toplevel = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False
    )
    if toplevel.returncode != 0:
        fail(
            "parlay must run inside the Bob's worktree "
            f"({toplevel.stderr.strip() or 'git rev-parse failed'})."
        )
    return Path(toplevel.stdout.strip()) / _SCRATCH_DIRNAME


def fail(error: object) -> NoReturn:
    print(f"Error: {error}", file=sys.stderr)
    sys.exit(1)


def yesno(flag: bool) -> str:
    return "yes" if flag else "no"
