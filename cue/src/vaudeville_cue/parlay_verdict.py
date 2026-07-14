from __future__ import annotations

from collections.abc import Callable

from vaudeville_cue.parlay_command import yesno
from vaudeville_cue.parlay_decide import Outcome, decide
from vaudeville_cue.parlay_reviewer import ReviewDisposition, disposition
from vaudeville_cue.parlay_snapshot import PrState, Snapshot
from vaudeville_cue.parlay_store import ParlayLayout
from vaudeville_cue.parlay_tally import Tally, escalating, must_stop


def watch_report(
    sensed: Snapshot,
    seen_at: float,
    tally: Tally,
    new_count: int,
    layout: ParlayLayout,
    max_iterations: int,
    now: Callable[[], float],
) -> str:
    review = disposition(sensed.reviewer, head_first_seen_at=seen_at)
    outcome = decide(
        review,
        elapsed=now() - seen_at,
        ci=sensed.ci.status,
        mergeability=sensed.mergeability,
        open_count=len(tally.open),
        escalating=escalating(tally),
        pr_state=sensed.pr_state,
    )
    convergence = verdict(outcome, review, sensed.pr_state)
    return _summary(convergence, sensed, review, new_count, tally, layout, max_iterations)


def verdict(outcome: Outcome, review: ReviewDisposition, pr_state: PrState) -> str:
    # The agent-facing convergence word. WAIT never reaches the agent: the wait consumes it, and a
    # still-pending reviewer once the budget ends surfaces as keep-going — the signal to re-sense.
    if outcome is Outcome.CLOSED:
        return "closed"
    if outcome is Outcome.ESCALATE:
        return "escalate"
    if outcome is Outcome.CONVERGED:
        if pr_state is PrState.MERGED:
            return "merged"
        return "signed-off" if review is ReviewDisposition.CLEAN else "steady-state"
    return "keep-going"


def _summary(
    convergence: str,
    sensed: Snapshot,
    review: ReviewDisposition,
    new_count: int,
    tally: Tally,
    layout: ParlayLayout,
    max_iterations: int,
) -> str:
    handle = "" if sensed.ci.run_handle is None else f" (run {sensed.ci.run_handle})"
    passes = f"{tally.passes}/{max_iterations}"
    return "\n".join(
        [
            f"convergence: {convergence}",
            f"open-comments: {len(tally.open)} -> {layout.open_comments}",
            f"comment-history: {layout.history}",
            f"new-this-pass: {new_count}",
            f"ci: {sensed.ci.status.value}{handle}",
            f"mergeability: {sensed.mergeability.value}",
            f"reviewer: {review.value}",
            f"rounds: {tally.rounds}   escalate: {yesno(escalating(tally))}",
            f"passes: {passes}   stop: {yesno(must_stop(tally, max_iterations))}",
            f"head: {sensed.head_sha}",
        ]
    )
