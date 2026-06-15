from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class OperatorTurn:
    line: int
    timestamp: str
    text: str
    via_tmp: bool = False


@dataclass(frozen=True)
class Section:
    source: str
    turns: tuple[OperatorTurn, ...]


def accumulate(prior: Sequence[Section], latest: Section) -> tuple[Section, ...]:
    return (*(section for section in prior if section.source != latest.source), latest)


_DIGEST_HEADER = (
    "# Operator turns — verbatim, in order, cumulative across this Bob's checkpoints.\n"
    "# A /clear starts a new session; each section below holds one session's operator turns,\n"
    "# kept so a later checkpoint does not lose the earlier ones. Within a section, a turn's\n"
    "# header names the lines it spans in that session's transcript; `via /tmp` was relayed\n"
    "# through the operator's tmp file.\n"
)

_SESSION_MARKER = "<<< session transcript: "
_SESSION_MARKER_CLOSE = " >>>"


def render(sections: Sequence[Section]) -> str:
    body = "".join(
        f"{_SESSION_MARKER}{section.source}{_SESSION_MARKER_CLOSE}\n{_turns_body(section.turns)}\n"
        for section in sections
    )
    return _DIGEST_HEADER + "\n" + body.rstrip("\n") + "\n"


def _turns_body(turns: Sequence[OperatorTurn]) -> str:
    if not turns:
        return "(no operator turns in this session)\n"
    lines = [turn.line for turn in turns]
    blocks = []
    for index, turn in enumerate(turns):
        following = lines[index + 1] if index + 1 < len(lines) else None
        via = " via /tmp" if turn.via_tmp else ""
        header = f"=== operator turn  [{_span(turn.line, following)}]{via}  {turn.timestamp} ==="
        blocks.append(f"{header}\n{turn.text}\n")
    return "".join(blocks)


def _span(line: int, following: int | None) -> str:
    # Two turns can share a transcript line — a single message carrying two /tmp
    # relays, or a typed and a relayed turn — so the next turn's line is not always
    # past this one. Render a single-line locator rather than a backwards span.
    if following is None:
        return f"line {line} to end"
    if following - 1 <= line:
        return f"line {line}"
    return f"lines {line}-{following - 1}"
