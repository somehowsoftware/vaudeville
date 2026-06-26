from __future__ import annotations

import re
from collections.abc import Sequence
from pathlib import PurePosixPath

from vaudeville_cue.digest import OperatorTurn
from vaudeville_cue.resume_brief import RESUME_BRIEF_OPENING
from vaudeville_cue.transcript import Message, ToolResult, ToolUse

# A user-role record is the operator speaking only when the harness recorded that
# the operator typed or queued it. Every other source under the user role is
# machinery injected into the conversation, not a turn: "system" (task-notifications),
# "sdk" (a spawned session's seed Brief), and the absent source (tool results,
# harness meta).
_OPERATOR_PROMPT_SOURCES = frozenset({"typed", "queued"})

_OPERATOR_TMP_FILE = "tmp"

# The Read tool returns a file behind a `cat -n` line-number gutter; the
# operator's words are what remains once the gutter is stripped from each line.
_READ_GUTTER = re.compile(r"^ *\d+\t", re.MULTILINE)


def operator_turns(messages: Sequence[Message]) -> list[OperatorTurn]:
    both = [*typed_operator_turns(messages), *relayed_operator_turns(messages)]
    return sorted(both, key=lambda turn: turn.line)


def typed_operator_turns(messages: Sequence[Message]) -> list[OperatorTurn]:
    kept: list[Message] = []
    for message in messages:
        if not _operator_spoke(message):
            continue
        if kept and _restreamed(kept[-1], message):
            if len(message.spoken_text) >= len(kept[-1].spoken_text):
                kept[-1] = message
            continue
        kept.append(message)
    return [OperatorTurn(message.line, message.timestamp, message.spoken_text) for message in kept]


def relayed_operator_turns(messages: Sequence[Message]) -> list[OperatorTurn]:
    tmp_read_ids: set[str] = set()
    recovered: set[str] = set()
    turns: list[OperatorTurn] = []
    for message in messages:
        for block in message.blocks:
            if isinstance(block, ToolUse) and _reads_operator_tmp(block):
                tmp_read_ids.add(block.id)
            elif isinstance(block, ToolResult) and block.tool_use_id in tmp_read_ids:
                relayed = _READ_GUTTER.sub("", block.text).strip()
                if relayed and relayed not in recovered:
                    recovered.add(relayed)
                    turns.append(
                        OperatorTurn(message.line, message.timestamp, relayed, via_tmp=True)
                    )
    return turns


def _operator_spoke(message: Message) -> bool:
    return (
        message.role == "user"
        and message.prompt_source in _OPERATOR_PROMPT_SOURCES
        and bool(message.spoken_text)
        and not _is_injected_resume_brief(message)
    )


def _is_injected_resume_brief(message: Message) -> bool:
    # A Checkpoint injects the Resume Brief as a typed user turn, so promptSource lets it
    # through; its own opening marker is what marks it machinery this subsystem wrote, not
    # the operator. Without this a later checkpoint would nest the prior Digest and
    # Carryover the Brief carries into the new one.
    return message.spoken_text.startswith(RESUME_BRIEF_OPENING)


def _restreamed(earlier: Message, later: Message) -> bool:
    if earlier.parent_uuid != later.parent_uuid:
        return False
    earlier_text, later_text = earlier.spoken_text, later.spoken_text
    return (
        earlier_text == later_text
        or later_text.startswith(earlier_text)
        or earlier_text.startswith(later_text)
    )


def _reads_operator_tmp(tool_use: ToolUse) -> bool:
    return tool_use.name == "Read" and PurePosixPath(tool_use.file_path).name == _OPERATOR_TMP_FILE
