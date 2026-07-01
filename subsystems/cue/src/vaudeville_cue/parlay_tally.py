from __future__ import annotations

from dataclasses import dataclass, replace

# Three code-changing rounds in one run is the signal that the patches are
# downstream of a misframing the reviewer could not see.
ESCALATION_ROUNDS = 3

# A backstop against the opposite failure: a loop that spins without ever patching
# (CI stuck pending, a sign-off that never comes) and so never trips the round stop.
DEFAULT_MAX_PASSES = 20


@dataclass(frozen=True)
class Tally:
    # Code-changing rounds, distinct from passes: a pass that only reads, or only
    # rejects, is not a round. The escalation backstop reads rounds, the spin
    # backstop reads passes. waived_at is the round count an operator's waiver lifted
    # the escalation at; the override derives off rounds minus it, so the count stays a
    # true history while a waiver re-arms three rounds further on.
    rounds: int
    passes: int
    addressed: frozenset[int]
    open: frozenset[int]
    waived_at: int | None = None

    @classmethod
    def empty(cls) -> Tally:
        return cls(rounds=0, passes=0, addressed=frozenset(), open=frozenset())


def observe(tally: Tally, *, surfaced: frozenset[int], code_changing: bool) -> Tally:
    # The sense owns both counts a backstop reads: every pass is a pass, and a pass whose
    # snapshot landed a commit is a round. Whether code changed is a fact the watch reads
    # off the PR head, never a disposition the agent records.
    return replace(
        tally,
        passes=tally.passes + 1,
        rounds=tally.rounds + (1 if code_changing else 0),
        open=tally.open | surfaced,
    )


def resolve(tally: Tally, *, addressed: frozenset[int]) -> Tally:
    return replace(tally, addressed=tally.addressed | addressed, open=tally.open - addressed)


def waive(tally: Tally) -> Tally:
    # The operator's lifting of the escalation, pinned to the round it fired at. rounds is left
    # to climb so a second trip past the waiver lands a louder alarm, where zeroing the count
    # would mute it and forget the run had already been here once.
    return replace(tally, waived_at=tally.rounds)


def escalating(tally: Tally) -> bool:
    # The override the decision wears outermost: three code-changing rounds since the last
    # waiver (or since the run began) is the hard stop the operator alone lifts.
    return tally.rounds - (tally.waived_at or 0) >= ESCALATION_ROUNDS


def must_stop(tally: Tally, max_passes: int) -> bool:
    return tally.passes >= max_passes
