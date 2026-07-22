# The headroom screen reads the stay file; this module writes it. The two never share a
# process — the screen is a flat stdlib-only hook script, this runs under `vv` — so neither
# side can import the other's copy of the filename or JSON schema, and the file is the whole
# contract between them. tests/test_stay.py drives both halves against one worktree and is
# what fails when either drifts.

from __future__ import annotations

import json
from pathlib import Path

# The environment variable Claude Code publishes its session id in.
SESSION_ID_ENV = "CLAUDE_CODE_SESSION_ID"

_SCRATCH = ".scratch"
_STAY_FILE = "headroom-stay.json"


class StayRefused(ValueError):
    pass


def stay_path_in(worktree: Path) -> Path:
    return worktree / _SCRATCH / _STAY_FILE


def record_stay(reason: str, *, stay_path: Path, session_id: str | None) -> str:
    if not session_id:
        raise StayRefused(
            f"${SESSION_ID_ENV} is unset, so there is no session to bind this stay to, and "
            "a stay bound to no session suppresses nothing. Nothing was written. Record the "
            "stay from inside the Claude Code session whose soft rungs it is meant to hold."
        )
    if not reason.strip():
        raise StayRefused(
            "a stay needs a reason: it is the justification the screen reads each tick, and "
            "what you will read when you come back to ask whether it still holds. Nothing "
            "was written."
        )
    # Never read before overwriting: the running session owns this file outright, and reading
    # a predecessor's stay first would trap the write behind the harness's read-before-write rule.
    stay_path.parent.mkdir(parents=True, exist_ok=True)
    stay_path.write_text(json.dumps({"reason": reason, "session_id": session_id}, indent=2) + "\n")
    return (
        f"Stay recorded at {stay_path}.\n"
        "The gentle and active rungs stand down for the rest of this session. The "
        "aggressive and emergency rungs still fire: they are the backstop, and no stay "
        "moves them.\n"
        f"Holding for: {reason}"
    )
