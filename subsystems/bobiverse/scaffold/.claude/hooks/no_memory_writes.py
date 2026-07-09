#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys

try:
    from screen_reach import screen_disabled_here
except ImportError:
    # The reach helper is a sibling stock hook that vaudeville-hook contributes
    # into the shared hooks dir. If it is absent, the screen cannot be told it is
    # switched off, so it enforces.
    def screen_disabled_here(screen_name: str, cwd: str | None) -> bool:
        return False


# This guard is the memory-writes screen; reach can switch it off per Component.
SCREEN_NAME = "memory-writes"

_PATH_KEYS = {
    "Write": "file_path",
    "Edit": "file_path",
    "MultiEdit": "file_path",
    "NotebookEdit": "notebook_path",
}

_CLAUDE_MD = os.path.realpath(os.path.expanduser("~/.claude/CLAUDE.md"))
_HOST_MD = os.path.realpath(os.path.expanduser("~/.vaudeville/host.md"))
_CLAUDE_PROJECTS = os.path.realpath(os.path.expanduser("~/.claude/projects"))

_MEMORY_REASON = (
    "This priming path is closed to AI writes. Doctrine lives in "
    "~/.vaudeville/. If the fact you are recording is already there, "
    "you do not need to write it. If it is not, surface the candidate "
    "in chat as a doctrine-revision proposal; revisions are submitted as PRs "
    "to vaudeville-config."
)

_HOST_REASON = (
    "~/.vaudeville/host.md is operator-owned. AI never writes to it. "
    "If a host-specific fact would belong there, surface the candidate "
    "in chat for the operator to add by hand."
)


def _classify(path: str) -> str | None:
    resolved = os.path.realpath(os.path.expanduser(path))
    if resolved == _CLAUDE_MD:
        return _MEMORY_REASON
    if resolved == _HOST_MD:
        return _HOST_REASON
    if resolved == _CLAUDE_PROJECTS or resolved.startswith(_CLAUDE_PROJECTS + os.sep):
        rest = resolved[len(_CLAUDE_PROJECTS) + 1 :]
        parts = rest.split(os.sep)
        # parts[0] is the project slug; guard the memory/ subdir and the top-level MEMORY.md.
        if len(parts) >= 2 and (
            parts[1] == "memory" or (len(parts) == 2 and parts[1] == "MEMORY.md")
        ):
            return _MEMORY_REASON
    return None


def main() -> int:
    payload = json.load(sys.stdin)
    if screen_disabled_here(SCREEN_NAME, payload.get("cwd")):
        return 0
    tool_name = payload.get("tool_name")
    path_key = _PATH_KEYS.get(tool_name)
    if path_key is None:
        return 0
    path = (payload.get("tool_input") or {}).get(path_key)
    if not isinstance(path, str):
        return 0
    reason = _classify(path)
    if reason is None:
        return 0
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        },
        sys.stdout,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
