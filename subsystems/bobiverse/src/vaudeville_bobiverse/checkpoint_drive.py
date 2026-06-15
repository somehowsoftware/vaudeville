"""The drive across a Checkpoint's /clear: clear the pane, then inject the Resume Brief.

The checkpoint runner launches this module detached (its own session, output to
a log) because the /clear it sends wipes the very conversation that asked for
it — the drive must outlive that wipe, the same reason teardown detaches from
the pane it kills. A genuine /clear starts a fresh Claude session, which lands
as a new .jsonl in the worktree's transcript directory; the Brief is injected
only once that cleared session has appeared, and never on timeout — abort
rather than inject into a session that never cleared.

Every location arrives as an argument computed by `vv checkpoint`; the drive
derives nothing. `CHECKPOINT_CLEAR_TIMEOUT` and `CHECKPOINT_CLEAR_POLL_INTERVAL`
(seconds) tune the wait.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

_CLEAR_TIMEOUT_ENV = "CHECKPOINT_CLEAR_TIMEOUT"
_POLL_INTERVAL_ENV = "CHECKPOINT_CLEAR_POLL_INTERVAL"


def session_transcripts(transcript_dir: Path) -> frozenset[str]:
    return frozenset(spine.name for spine in transcript_dir.glob("*.jsonl"))


def cleared_session_appeared(before: frozenset[str], now: frozenset[str]) -> bool:
    return bool(now - before)


def drive(
    pane: str, transcript_dir: Path, brief: Path, *, timeout: float, poll_interval: float
) -> None:
    before = session_transcripts(transcript_dir)
    subprocess.run(["workmux", "send", pane, "/clear"], check=True)  # noqa: S603, S607
    deadline = time.monotonic() + timeout
    while not cleared_session_appeared(before, session_transcripts(transcript_dir)):
        if time.monotonic() >= deadline:
            sys.exit(
                f"Error: the cleared session never appeared in {transcript_dir} "
                f"within {timeout}s; not resuming '{pane}'."
            )
        time.sleep(poll_interval)
    subprocess.run(["workmux", "send", pane, "--file", str(brief)], check=True)  # noqa: S603, S607


def main(argv: list[str]) -> None:
    pane, transcript_dir, brief = argv
    drive(
        pane,
        Path(transcript_dir),
        Path(brief),
        timeout=float(os.environ.get(_CLEAR_TIMEOUT_ENV, "300")),
        poll_interval=float(os.environ.get(_POLL_INTERVAL_ENV, "2")),
    )


if __name__ == "__main__":
    main(sys.argv[1:])
