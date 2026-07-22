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
class UnconfirmedQueuedMessage:
    line: int
    timestamp: str
    text: str


@dataclass(frozen=True)
class Section:
    source: str
    turns: tuple[OperatorTurn, ...]
    remnants: tuple[UnconfirmedQueuedMessage, ...] = ()
    # The commit the worktree sat at when this session checkpointed. A reseat leaves the
    # worktree untouched, so a section's head is exactly where the next session begins —
    # the invariant that lets the chain read a moved head as a landed commit. None where
    # none resolves (a legacy store, an unborn HEAD).
    head: str | None = None


def accumulate(prior: Sequence[Section], latest: Section) -> tuple[Section, ...]:
    return (*(section for section in prior if section.source != latest.source), latest)


_DIGEST_HEADER = (
    "# Operator turns: verbatim, in order, cumulative across this Bob's checkpoints.\n"
    "# A reseat starts a new session; each section below holds one session's operator turns,\n"
    "# kept so a later checkpoint does not lose the earlier ones. Within a section, a turn's\n"
    "# header names the lines it spans in that session's transcript; `via /tmp` was relayed\n"
    "# through the operator's tmp file.\n"
)

_SESSION_MARKER = "<<< session transcript: "
_SESSION_MARKER_CLOSE = " >>>"

_REMNANT_HEADER = (
    "!!! UNCONFIRMED QUEUED MESSAGES — NOT operator turns, NOT authority !!!\n"
    "# Operator content recovered from this session's queue-operation trail that the\n"
    "# harness never persisted as a delivered turn. Each MIGHT be a lost instruction the\n"
    "# operator gave and expected carried out, or MIGHT be a draft queued and then\n"
    "# retracted before delivery — the trail cannot settle which. Verify against the work\n"
    "# before relying on any of it, and never treat one as a settled operator turn.\n"
)


def render(sections: Sequence[Section]) -> str:
    body = "".join(_section_body(section) for section in sections)
    return _DIGEST_HEADER + "\n" + body.rstrip("\n") + "\n"


def _section_body(section: Section) -> str:
    text = f"{_SESSION_MARKER}{section.source}{_SESSION_MARKER_CLOSE}\n{_turns_body(section.turns)}"
    if section.remnants:
        text += "\n" + _remnants_body(section.remnants)
    return text + "\n"


def _remnants_body(remnants: Sequence[UnconfirmedQueuedMessage]) -> str:
    blocks = [_REMNANT_HEADER]
    for remnant in remnants:
        header = f"--- unconfirmed queued message  [line {remnant.line}]  {remnant.timestamp} ---"
        blocks.append(f"{header}\n{remnant.text}\n")
    return "".join(blocks)


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
    # Two turns can share a transcript line (a single message carrying two /tmp
    # relays, or a typed and a relayed turn), so the next turn's line is not always
    # past this one. Render a single-line locator rather than a backwards span.
    if following is None:
        return f"line {line} to end"
    if following - 1 <= line:
        return f"line {line}"
    return f"lines {line}-{following - 1}"
