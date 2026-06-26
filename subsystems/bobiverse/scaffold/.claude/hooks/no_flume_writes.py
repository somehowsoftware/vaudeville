#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys

# The file-mutating tools whose target path is guarded. Bash redirection
# (`echo > ~/flume/x`) is deliberately not covered: parsing arbitrary shell for
# write effects is fragile, and mutagen self-heals the gap at the next reconciliation.
_PATH_KEYS = {
    "Write": "file_path",
    "Edit": "file_path",
    "MultiEdit": "file_path",
    "NotebookEdit": "notebook_path",
}

_FLUME_ROOT = os.path.realpath(os.path.expanduser("~/flume"))

_REASON = (
    "Writes under ~/flume are disabled at the Vaudeville level; this "
    "is project policy, not a per-turn refusal. ~/flume is a one-way "
    "inbound channel from David's trust boundary; mutagen mirrors it "
    "with deletion permission, so anything written here gets nuked at "
    "the next reconciliation. There is no return path. For an "
    "agent-to-David handoff, use a different mechanism: a commit + PR "
    "for code, a comment on a YouTrack Assignment or PR, or a path under "
    "the repo or /tmp that you tell David about."
)


def _is_under_flume(path: str) -> bool:
    resolved = os.path.realpath(os.path.expanduser(path))
    return resolved == _FLUME_ROOT or resolved.startswith(_FLUME_ROOT + os.sep)


def main() -> int:
    payload = json.load(sys.stdin)
    tool_name = payload.get("tool_name")
    path_key = _PATH_KEYS.get(tool_name)
    if path_key is None:
        return 0
    path = (payload.get("tool_input") or {}).get(path_key)
    if not isinstance(path, str) or not _is_under_flume(path):
        return 0
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": _REASON,
            }
        },
        sys.stdout,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
