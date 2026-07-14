from __future__ import annotations

from dataclasses import dataclass, replace

# Three forced rounds in one run is the signal that the patches sit downstream
# of a misframing the reviewer could not see.
ESCALATION_ROUNDS = 3

# A backstop against the opposite failure: a loop that spins without ever patching
# (CI stuck pending, a sign-off that never comes) and so never trips the round stop.
DEFAULT_MAX_PASSES = 20


@dataclass(frozen=True)
class Tally:
    # Forced rounds, distinct from passes: a pass that only reads, only rejects, or only carries
    # the author's own progress is not a round. The escalation backstop reads rounds, the spin
    # backstop reads passes. waived_at is the round count an operator's waiver lifted the escalation
    # at; the override derives off rounds minus it, so the count stays a true history while a waiver
    # re-arms three rounds further on.
    rounds: int
    passes: int
    addressed: frozenset[int]
    open: frozenset[int]
    waived_at: int | None = None

    @classmethod
    def empty(cls) -> Tally:
        return cls(rounds=0, passes=0, addressed=frozenset(), open=frozenset())


def observe(tally: Tally, *, surfaced: frozenset[int], forced: bool) -> Tally:
    return replace(
        tally,
        passes=tally.passes + 1,
        rounds=tally.rounds + (1 if forced else 0),
        open=tally.open | surfaced,
    )


def resolve(tally: Tally, *, addressed: frozenset[int]) -> Tally:
    return replace(tally, addressed=tally.addressed | addressed, open=tally.open - addressed)


def waive(tally: Tally) -> Tally:
    # Lift the escalation, pinned to the round it fired at. rounds is left to climb so a second
    # trip past the waiver lands a louder alarm; zeroing the count would mute it and forget the
    # run had already been here once.
    return replace(tally, waived_at=tally.rounds)


def escalating(tally: Tally) -> bool:
    # The override the decision wears outermost: three forced rounds since the last waiver
    # (or since the run began) is the hard stop, and only a waiver clears it.
    return tally.rounds - (tally.waived_at or 0) >= ESCALATION_ROUNDS


def must_stop(tally: Tally, max_passes: int) -> bool:
    return tally.passes >= max_passes
