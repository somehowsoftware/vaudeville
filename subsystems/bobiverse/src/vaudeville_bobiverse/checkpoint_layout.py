"""Where a checkpoint's artifacts live: the one place their locations exist.

The Digest store, the Carryover, and the Resume Brief are anchored at the worktree
root — never the invoking shell's cwd — under the gitignored `.scratch/`. Every
writer and reader is handed this value; a second derivation of these paths
anywhere else is how a Bob gets stranded reading where nothing was written. The
Digest is the durable store the next checkpoint accumulates onto (JSON, not the
rendered text — see digest.py), hence `.json`.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

_SCRATCH_DIRNAME = ".scratch"


@dataclass(frozen=True)
class CheckpointLayout:
    digest: Path
    carryover: Path
    resume_brief: Path


def checkpoint_layout(worktree_root: Path) -> CheckpointLayout:
    scratch = worktree_root / _SCRATCH_DIRNAME
    return CheckpointLayout(
        digest=scratch / "digest.json",
        carryover=scratch / "carryover.md",
        resume_brief=scratch / "resume-brief.md",
    )
