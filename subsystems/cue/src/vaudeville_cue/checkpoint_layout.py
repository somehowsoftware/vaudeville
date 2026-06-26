from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

_SCRATCH_DIRNAME = ".scratch"


@dataclass(frozen=True)
class CheckpointLayout:
    digest: Path
    carryover: Path
    resume_brief: Path
    drive_log: Path


def checkpoint_layout(worktree_root: Path) -> CheckpointLayout:
    scratch = worktree_root / _SCRATCH_DIRNAME
    return CheckpointLayout(
        digest=scratch / "digest.json",
        carryover=scratch / "carryover.md",
        resume_brief=scratch / "resume-brief.md",
        drive_log=scratch / "checkpoint-drive.log",
    )
