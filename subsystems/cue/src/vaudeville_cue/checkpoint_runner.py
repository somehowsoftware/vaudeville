from __future__ import annotations

import os
import subprocess
from pathlib import Path

from vaudeville_cue.checkpoint_plan import CheckpointPlan


def run_plan(plan: CheckpointPlan) -> None:
    for path, content in plan.writes:
        path.parent.mkdir(parents=True, exist_ok=True)
        _write_atomically(path, content)
    # Popen dups the fd into the child, so the parent's copy closes safely after spawn.
    with plan.drive_log.open("ab") as log:
        # start_new_session detaches the drive into its own session: it sends the /clear
        # that wipes this conversation, so it must outlive the process that launched it.
        subprocess.Popen(  # noqa: S603
            list(plan.launch),
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=log,
            start_new_session=True,
            env=os.environ.copy(),
        )


def _write_atomically(path: Path, content: str) -> None:
    # Write to a sibling temp then rename: a checkpoint killed mid-write leaves the
    # temp, never a half-written artifact, so the next checkpoint's read of the
    # durable Digest store sees the prior complete value rather than corruption.
    temp = path.with_name(f"{path.name}.tmp")
    temp.write_text(content, encoding="utf-8")
    temp.replace(path)
