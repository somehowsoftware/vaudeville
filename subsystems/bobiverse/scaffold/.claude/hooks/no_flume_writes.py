#!/usr/bin/env python3
"""PreToolUse hook: refuse writes under ~/flume.

`~/flume` is a one-way inbound channel from David's trust boundary into
the sandbox. Mutagen mirrors it with deletion permission — anything in
the sandbox copy that isn't on David's side at the next reconciliation
gets nuked. There is no return path; writes here vanish on the next
reconciliation cycle, often silently. A memory entry recording the rule
is only as reliable as the next agent's recall — a harness-enforced
deny makes the refusal structural and re-teaches the rule at the moment
of attempt via `permissionDecisionReason`.

Covers the file-mutating tools (Write, Edit, MultiEdit, NotebookEdit).
Bash redirection (`echo > ~/flume/x`) is out of scope: parsing
arbitrary shell commands for write effects is fragile, and mutagen
self-heals the gap at the next reconciliation regardless.

Pass-through on unmatched tools or paths outside ~/flume: exit 0 with
no output.
"""

from __future__ import annotations

import json
import os
import sys

_PATH_KEYS = {
    "Write": "file_path",
    "Edit": "file_path",
    "MultiEdit": "file_path",
    "NotebookEdit": "notebook_path",
}

_FLUME_ROOT = os.path.realpath(os.path.expanduser("~/flume"))

_REASON = (
    "Writes under ~/flume are disabled at the Vaudeville level — this "
    "is project policy, not a per-turn refusal. ~/flume is a one-way "
    "inbound channel from David's trust boundary; mutagen mirrors it "
    "with deletion permission, so anything written here gets nuked at "
    "the next reconciliation. There is no return path. For an "
    "agent-to-David handoff, use a different mechanism: a commit + PR "
    "for code, a comment on a YouTrack Premise or PR, or a path under "
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
