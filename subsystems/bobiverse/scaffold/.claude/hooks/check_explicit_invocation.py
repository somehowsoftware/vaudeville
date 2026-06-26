#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

PROTECTED_SKILLS = frozenset({"closeout", "onward"})

# `vv teardown` / `vv-bob teardown` as a command word, anywhere in a (possibly
# compound) command string. `\b` on the left so an absolute-path invocation
# (`/usr/bin/vv teardown`) still matches; `\s+` tolerates extra spacing; `teardown\b`
# so other `vv` subcommands do not trip the guard. Deliberately recall-biased: it
# accepts false positives (the string sitting in a heredoc or a grep; a re-word
# costs little) to avoid the false negative that is the self-closeout recurring. It
# does not chase evasion (a `vv teardown` buried in a script or base64 blob escapes);
# per the trust posture, the modal failure is an honest mistake, not an adversary.
_VV_TEARDOWN_RE = re.compile(r"\bvv(?:-bob)?\s+teardown\b")


def _skill_refusal(skill: str) -> str:
    return (
        f"/{skill} requires explicit invocation. David's most recent typed "
        f"message does not contain the literal `/{skill}` outside of "
        "backticks. Do not infer it from synonyms or backticked references. "
        f"Stop and ask David to type `/{skill}` himself."
    )


_TEARDOWN_REFUSAL = (
    "vv teardown tears down THIS worktree: it archives the working tree and runs "
    "`workmux remove --force`, ending the current Bob. It is not housekeeping and "
    "not a tracker operation. David's most recent typed message contains no "
    "literal `/closeout` or `/onward` outside of backticks, so this teardown is "
    "unauthorised. To end this Bob, ask David to type `/closeout` himself. If you "
    "meant to transition an Assignment's state without ending this session, the "
    "verb you want is `vv resolve`, `vv return`, or `vv unclaim`; teardown is "
    "the wrong one; surface that to David."
)


# CommonMark code spans use a run of N backticks as opener and the same run
# length as closer; runs of any other length inside the span are literal. One
# generalised pattern subsumes both inline spans and fenced blocks: the opener
# length is captured and matched verbatim by the closer.
_CODE_RE = re.compile(r"(`+).*?\1", re.DOTALL)


def _strip_code(text: str) -> str:
    return _CODE_RE.sub("", text)


def _last_typed_text(transcript_path: Path) -> str:
    if not transcript_path.exists():
        return ""
    last = ""
    with transcript_path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if entry.get("type") != "user" or entry.get("isMeta"):
                continue
            origin = entry.get("origin") or {}
            if origin.get("kind") == "task-notification":
                continue
            content = entry.get("message", {}).get("content")
            if isinstance(content, str):
                last = content
            elif isinstance(content, list):
                texts = [
                    block.get("text", "")
                    for block in content
                    if isinstance(block, dict) and block.get("type") == "text"
                ]
                if texts:
                    last = "\n".join(texts)
    return last


def _typed_consent_text(transcript_path: Path) -> str:
    # Both guards gate on the same signal: David's most recent typed message must
    # carry a literal `/closeout` or `/onward` outside backticks. David discusses
    # these skills by name in inline code spans, so a backticked reference denotes the
    # skill, not an invocation; strip code spans first, and only an unbackticked
    # literal then counts as consent.
    return _strip_code(_last_typed_text(transcript_path))


def _guard_skill(tool_input: dict[str, object], transcript_path: Path) -> int:
    skill = tool_input.get("skill")
    if not isinstance(skill, str) or skill not in PROTECTED_SKILLS:
        return 0
    if f"/{skill}" in _typed_consent_text(transcript_path):
        return 0
    sys.stderr.write(_skill_refusal(skill) + "\n")
    return 2


def _guard_teardown_command(tool_input: dict[str, object], transcript_path: Path) -> int:
    # `vv teardown` archives this worktree and runs `workmux remove --force`, ending
    # the current Bob; a Bob reaching for it as housekeeping self-closes by mistake.
    # The transition atoms `/closeout` chains before it (vv resolve/return/unclaim)
    # only touch the tracker, so they go unguarded; teardown is the irreversible step.
    command = tool_input.get("command")
    if not isinstance(command, str) or not _VV_TEARDOWN_RE.search(command):
        return 0
    consent = _typed_consent_text(transcript_path)
    if any(f"/{skill}" in consent for skill in PROTECTED_SKILLS):
        return 0
    sys.stderr.write(_TEARDOWN_REFUSAL + "\n")
    return 2


def main() -> int:
    payload = json.load(sys.stdin)
    tool_name = payload.get("tool_name")
    tool_input = payload.get("tool_input") or {}
    transcript_path = Path(payload.get("transcript_path") or "")
    if tool_name == "Bash":
        return _guard_teardown_command(tool_input, transcript_path)
    return _guard_skill(tool_input, transcript_path)


if __name__ == "__main__":
    sys.exit(main())
