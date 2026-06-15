#!/usr/bin/env python3
"""PreToolUse hook: refuse pane-destroying teardown unless David authorised it.

Two surfaces reach the same destructive action — archiving the worktree and
`workmux remove --force`, which ends the Bob whose pane runs it:

- The **front door**: the `/closeout` and `/onward` skills, invoked through the
  Skill tool. A spawning agent that paraphrases verbs like "obsolete the
  premise", "close it out", or "saturate the graph" into one of these
  invocations destroys a live conversation without authorisation.
- The **back door**: a raw `vv teardown` (or `vv-bob teardown`) run through the
  Bash tool. `vv teardown` archives and removes the *current* worktree and kills
  its pane, so a Bob that reaches for it believing it to be a harmless
  housekeeping command self-closes by mistake. That self-closeout is what this
  guard's Bash branch exists to prevent. The transition atoms `/closeout` chains
  before it (`vv resolve`, `vv return`, `vv unclaim`) only touch the tracker and
  are not guarded here; teardown is the irreversible step.

Both surfaces are gated by the same consent signal: David's most recent typed
message must contain a literal `/closeout` or `/onward` outside of backticks.
Backtick-stripping matters because David discusses these skills in chat by name
(inline code spans); those references denote the skill, not an invocation, so
only an unbackticked literal counts as consent. The front-door skills both call
`vv teardown` themselves, so a typed `/closeout` or `/onward` authorises the
underlying verb too — the legitimate teardown path passes cleanly.

The Bash detection is deliberately recall-biased: it matches `vv teardown`
anywhere in a (possibly compound) command, accepting false positives (the string
sitting in a heredoc or a grep) because a false positive costs a re-word while a
false negative is the self-closeout recurring. It does *not* chase evasion — a
`vv teardown` buried inside a bash script or a base64 blob escapes, and the
constellation depends on session-restore for that case. Per the trust posture,
the modal failure is an honest mistake, not an adversary.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

PROTECTED_SKILLS = frozenset({"closeout", "onward"})

# `vv teardown` / `vv-bob teardown` as a command word, anywhere in the command
# string. `\b` on the left so an absolute-path invocation (`/usr/bin/vv
# teardown`) still matches; `\s+` tolerates extra spacing; `teardown\b` so other
# `vv` subcommands do not trip the guard.
_VV_TEARDOWN_RE = re.compile(r"\bvv(?:-bob)?\s+teardown\b")


def _skill_refusal(skill: str) -> str:
    return (
        f"/{skill} requires explicit invocation. David's most recent typed "
        f"message does not contain the literal `/{skill}` outside of "
        "backticks. Do not infer it from synonyms or backticked references. "
        f"Stop and ask David to type `/{skill}` himself."
    )


_TEARDOWN_REFUSAL = (
    "vv teardown tears down THIS worktree — it archives the working tree and runs "
    "`workmux remove --force`, ending the current Bob. It is not housekeeping and "
    "not a tracker operation. David's most recent typed message contains no "
    "literal `/closeout` or `/onward` outside of backticks, so this teardown is "
    "unauthorised. To end this Bob, ask David to type `/closeout` himself. If you "
    "meant to transition a Premise's state without ending this session, the "
    "verb you want is `vv resolve`, `vv return`, or `vv unclaim` — teardown is "
    "the wrong one; surface that to David."
)


# CommonMark code spans use a run of N backticks as opener and the same run
# length as closer; runs of any other length inside the span are literal. One
# generalised pattern subsumes both inline spans and fenced blocks — the opener
# length is captured and matched verbatim by the closer.
_CODE_RE = re.compile(r"(`+).*?\1", re.DOTALL)


def _strip_code(text: str) -> str:
    return _CODE_RE.sub("", text)


def _last_typed_text(transcript_path: Path) -> str:
    """Most recent user-typed message body in the transcript, or "".

    Skips tool results, harness-injected meta entries (skill bodies),
    and task-notification origins.
    """
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
    """David's most recent typed message, code spans stripped.

    The text in which a protected slash-literal counts as authorisation.
    """
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
