#!/usr/bin/env python3
# Ringmaster materializes this file flat into the shared hooks dir, where Claude Code
# runs it under the system python3 with no virtualenv. Hence stdlib only, no vaudeville
# import, and the lone `import screen_reach` binds another flat script in the same dir,
# not a package path.

from __future__ import annotations

import json
import sys
import traceback
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import screen_reach

SCREEN_NAME = "headroom"


# --- Core: pure and deterministic. Every location and every read arrives as a value. ---


@dataclass(frozen=True)
class EffectiveContext:
    # A nominal type, not a bare int, so a context size cannot be crossed with a rung
    # threshold, a stay ceiling, or the wall — all of which are also token counts.
    tokens: int


_USAGE_FIELDS = ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")


def effective_context_of(entries: Sequence[Mapping[str, object]]) -> EffectiveContext:
    for entry in reversed(entries):
        # Sidechain entries are a subagent's turns; the screen watches the main loop.
        if entry.get("isSidechain"):
            continue
        if entry.get("type") != "assistant":
            continue
        message = entry.get("message")
        if not isinstance(message, Mapping):
            continue
        usage = message.get("usage")
        if not isinstance(usage, Mapping):
            continue
        return EffectiveContext(sum(_usage_tokens(usage, field) for field in _USAGE_FIELDS))
    return EffectiveContext(0)


def _usage_tokens(usage: Mapping[str, object], field: str) -> int:
    value = usage.get(field, 0)
    return value if isinstance(value, int) and not isinstance(value, bool) else 0


class RungName(Enum):
    GENTLE = 1
    ACTIVE = 2
    AGGRESSIVE = 3
    EMERGENCY = 4


@dataclass(frozen=True)
class Rung:
    name: RungName
    threshold: int


@dataclass(frozen=True)
class Ladder:
    # Soft and hard rungs are separate fields, not one list with a flag, so a stay can
    # only ever be handed the soft rungs: suppressing a hard rung is not a reachable path.
    soft: tuple[Rung, ...]
    hard: tuple[Rung, ...]

    def __post_init__(self) -> None:
        rungs = self.soft + self.hard
        if not rungs:
            raise ValueError("a ladder needs at least one rung")
        thresholds = [rung.threshold for rung in rungs]
        if thresholds != sorted(thresholds) or len(set(thresholds)) != len(thresholds):
            raise ValueError(
                f"ladder thresholds must strictly ascend from soft to hard, got {thresholds}"
            )
        ranks = [rung.name.value for rung in rungs]
        if ranks != sorted(ranks):
            raise ValueError(
                f"friction must not fall as the threshold climbs, got rung ranks {ranks}"
            )

    def rungs(self) -> tuple[Rung, ...]:
        return self.soft + self.hard


# Raised, never swallowed: a garbled stay must never be read as "no ceiling".
class MalformedStay(ValueError):
    pass


@dataclass(frozen=True)
class Stay:
    # session_id binds the stay to the session that wrote it, so it self-invalidates
    # across a checkpoint: a resumed Bob runs under a fresh session, the old stay no
    # longer matches, and no cross-repository clear is needed.
    ceiling: int
    reason: str
    session_id: str


def parse_stay(data: Mapping[str, object]) -> Stay:
    ceiling = data.get("ceiling")
    reason = data.get("reason")
    session_id = data.get("session_id")
    if not isinstance(ceiling, int) or isinstance(ceiling, bool) or ceiling < 0:
        raise MalformedStay(f"stay ceiling must be a non-negative token count, got {ceiling!r}")
    if not isinstance(reason, str) or not reason.strip():
        raise MalformedStay(f"stay reason must be a non-empty string, got {reason!r}")
    if not isinstance(session_id, str) or not session_id:
        raise MalformedStay(f"stay session_id must be a non-empty string, got {session_id!r}")
    return Stay(ceiling=ceiling, reason=reason, session_id=session_id)


@dataclass(frozen=True)
class StayReading:
    # A None stay reads as the default ladder, never as "no ceiling"; `malformed` marks a
    # present-but-unreadable file so the shell can fall back to that ladder and say so.
    stay: Stay | None
    malformed: bool


_ASK = {
    RungName.GENTLE: (
        "You still have room, but the cheapest checkpoint is the one taken at a natural "
        "seam. Finish the thread you are on, then run /checkpoint."
    ),
    RungName.ACTIVE: (
        "Steer toward a checkpoint-safe state now: close the open loop and land what is in "
        "flight, then run /checkpoint at the next seam."
    ),
    RungName.AGGRESSIVE: (
        "Checkpoint now. Author your Carryover and run /checkpoint before you open new work."
    ),
    RungName.EMERGENCY: (
        "Checkpoint now — this is the top of the ladder, and the earlier rungs did not move "
        "you. Author your Carryover and run /checkpoint immediately, before any further work."
    ),
}

_STAY_OFFER = " If you have a reason to hold, record a stay instead and the soft rungs stand down."


@dataclass(frozen=True)
class Verdict:
    rung: Rung | None
    soft: bool
    effective_context: EffectiveContext
    wall: int

    @property
    def is_clear(self) -> bool:
        return self.rung is None

    def perception(self) -> str | None:
        if self.rung is None:
            return None
        tokens = self.effective_context.tokens
        # The ladder is a shed cadence, not wall proximity, so below the wall the perception
        # names the standing cost of the context, not a distance that would only reassure
        # against the block being issued. The wall is the frame only at or past it, where the
        # whole-conversation turn a checkpoint itself needs is the thing now at risk.
        if tokens >= self.wall:
            standing = (
                f"at or past the wall at {self.wall:,}, past which no faithful "
                "Carryover can be authored"
            )
        else:
            standing = "re-read in full every turn"
        ask = _ASK[self.rung.name]
        offer = _STAY_OFFER if self.soft else ""
        return (
            f"Headroom screen: you are at {tokens:,} tokens of effective context, "
            f"{standing}. {ask}{offer}"
        )


def reach_verdict(
    effective_context: EffectiveContext,
    ladder: Ladder,
    wall: int,
    stay: Stay | None,
) -> Verdict:
    # Hard rungs are consulted first and take no stay: this is what makes the aggressive
    # and emergency rungs unsuppressable — the branch that would let a stay reach them
    # does not exist.
    reached = _highest_reached(effective_context, ladder.hard)
    if reached is not None:
        return Verdict(rung=reached, soft=False, effective_context=effective_context, wall=wall)
    reached = _soft_rung_reached(effective_context, ladder, stay)
    if reached is not None:
        return Verdict(rung=reached, soft=True, effective_context=effective_context, wall=wall)
    return Verdict(rung=None, soft=False, effective_context=effective_context, wall=wall)


def _soft_rung_reached(
    effective_context: EffectiveContext,
    ladder: Ladder,
    stay: Stay | None,
) -> Rung | None:
    if stay is not None and effective_context.tokens < stay.ceiling:
        return None
    return _highest_reached(effective_context, ladder.soft)


def _highest_reached(effective_context: EffectiveContext, rungs: tuple[Rung, ...]) -> Rung | None:
    reached: Rung | None = None
    for rung in rungs:
        if effective_context.tokens >= rung.threshold:
            reached = rung
    return reached


@dataclass(frozen=True)
class HookResponse:
    hook_event_name: str
    additional_context: str | None = None
    decision_block: bool = False
    reason: str | None = None

    def to_output(self) -> dict[str, object] | None:
        output: dict[str, object] = {}
        if self.decision_block:
            output["decision"] = "block"
            if self.reason is not None:
                output["reason"] = self.reason
        if self.additional_context is not None:
            output["hookSpecificOutput"] = {
                "hookEventName": self.hook_event_name,
                "additionalContext": self.additional_context,
            }
        return output or None


def respond(
    verdict: Verdict,
    *,
    stay_path: Path,
    malformed_stay: bool,
    session_id: str,
    hook_event_name: str,
) -> HookResponse:
    lines: list[str] = []
    if malformed_stay:
        lines.append(
            f"Headroom screen: the stay file at {stay_path} is present but unreadable; "
            "it was ignored and the default ladder applies. Fix or remove it."
        )
    perception = verdict.perception()
    if perception is not None:
        if verdict.soft:
            # Hand the Bob the literal session_id to copy: a stay is bound to its session,
            # so a wrong guess would self-invalidate in silence.
            perception += (
                f" To record a stay, write {stay_path} with a ceiling, a reason, and "
                f'session_id "{session_id}".'
            )
        lines.append(perception)
    if not lines:
        return HookResponse(hook_event_name=hook_event_name)
    message = " ".join(lines)
    reached_hard_rung = verdict.rung is not None and not verdict.soft
    if reached_hard_rung:
        return HookResponse(hook_event_name=hook_event_name, decision_block=True, reason=message)
    return HookResponse(hook_event_name=hook_event_name, additional_context=message)


@dataclass(frozen=True)
class Configuration:
    ladder: Ladder
    wall: int


# The rungs are a shed cadence, not runway against the wall. A checkpoint lands a Bob near a
# ~35k floor, and it climbs from there on context that is mostly re-read tool exhaust, paid
# again every turn; each rung presses a shed as that climb outgrows the working set. GENTLE
# leads the point sessions naturally shed at; ACTIVE and AGGRESSIVE escalate from nudge to
# block as the climb runs past typical; EMERGENCY sits just above AGGRESSIVE, enough to land
# the open thread. The hard rungs enforce a shed the nudges failed to get — they do not
# reserve room below the wall, which near-the-top growth is too slow to threaten.
_DEFAULT_LADDER = Ladder(
    soft=(
        Rung(RungName.GENTLE, 150_000),
        Rung(RungName.ACTIVE, 250_000),
    ),
    hard=(
        Rung(RungName.AGGRESSIVE, 350_000),
        Rung(RungName.EMERGENCY, 400_000),
    ),
)

# The context window past which sending the whole conversation — an ordinary turn, a
# compact, the Carryover-authoring turn a checkpoint needs — begins to fail. Tunable to
# the model its Bobs run under.
_DEFAULT_WALL = 1_000_000


def tenant_configuration() -> Configuration:
    return Configuration(ladder=_DEFAULT_LADDER, wall=_DEFAULT_WALL)


# --- Shell: the file's only I/O. Resolves the core's values from the running session and
# --- maps the verdict onto the Claude Code hook substrate. ---

_SCRATCH = ".scratch"
_STAY_FILE = "headroom-stay.json"


def effective_context_at(transcript_path: Path) -> EffectiveContext:
    # Read this session's transcript alone: a checkpoint or clear opens a fresh transcript
    # that begins small, and the screen must not carry a count across that seam.
    entries: list[Mapping[str, object]] = []
    for raw_line in transcript_path.read_text().splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except ValueError:  # the live transcript's final line may be half-written
            continue
        if isinstance(entry, Mapping):
            entries.append(entry)
    return effective_context_of(entries)


def stay_on_file(stay_path: Path, current_session_id: str) -> StayReading:
    if not stay_path.exists():
        return StayReading(stay=None, malformed=False)
    try:
        raw = stay_path.read_text()
    except OSError:
        return StayReading(stay=None, malformed=True)
    try:
        data = json.loads(raw)
    except ValueError:  # JSONDecodeError is a ValueError
        return StayReading(stay=None, malformed=True)
    if not isinstance(data, Mapping):
        return StayReading(stay=None, malformed=True)
    try:
        stay = parse_stay(data)
    except MalformedStay:
        return StayReading(stay=None, malformed=True)
    # A well-formed stay under a different session is stale from before a checkpoint: read
    # as absent, so it self-invalidates with no cross-repository clear.
    if stay.session_id != current_session_id:
        return StayReading(stay=None, malformed=False)
    return StayReading(stay=stay, malformed=False)


def look(stdin: Mapping[str, object], config: Configuration) -> HookResponse:
    # Registered on PostToolBatch (once per turn), not PostToolUse (once per tool):
    # repeating the guidance every tool would spend the very headroom the screen guards.
    # The look mutates nothing, so a repeated firing is still as correct as a single one.
    transcript_path = Path(str(stdin["transcript_path"]))
    session_id = str(stdin["session_id"])
    cwd = Path(str(stdin["cwd"]))
    hook_event_name = str(stdin.get("hook_event_name", "PostToolBatch"))
    stay_path = cwd / _SCRATCH / _STAY_FILE

    effective_context = effective_context_at(transcript_path)
    reading = stay_on_file(stay_path, session_id)
    verdict = reach_verdict(effective_context, config.ladder, config.wall, reading.stay)
    return respond(
        verdict,
        stay_path=stay_path,
        malformed_stay=reading.malformed,
        session_id=session_id,
        hook_event_name=hook_event_name,
    )


def main() -> int:
    try:
        stdin = json.load(sys.stdin)
    except ValueError:  # JSONDecodeError is a ValueError
        return 0
    if not isinstance(stdin, dict):
        return 0
    # The reach guard runs before any transcript is read: a screen switched off for this
    # Component says nothing and exits.
    cwd = stdin.get("cwd")
    if screen_reach.screen_disabled_here(SCREEN_NAME, cwd if isinstance(cwd, str) else None):
        return 0
    try:
        output = look(stdin, tenant_configuration()).to_output()
    except Exception:  # the screen observes the Bob; it must never be what stops it
        traceback.print_exc(file=sys.stderr)
        return 0
    if output is not None:
        json.dump(output, sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
