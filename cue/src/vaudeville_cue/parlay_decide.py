from __future__ import annotations

from enum import Enum

from vaudeville_cue.parlay_reviewer import ReviewDisposition
from vaudeville_cue.parlay_snapshot import CiStatus, Mergeability, PrState

# How long the loop waits for the reviewer on a head before its silence reads as a skip and a
# settled PR may converge on it — comfortably longer than Codex's normal review latency, so a slow
# review is not mistaken for a skipped one.
REVIEW_TIMEOUT_SECONDS = 1800.0


class Outcome(Enum):
    # The per-round decision. WAIT is a fourth outcome of the one decision, not a pre-step, so the
    # reviewer's signal is read once; the shell consumes WAIT by sleeping and re-sensing. CLOSED is
    # the loop's exit when the PR was closed unmerged out from under it.
    WAIT = "wait"
    KEEP_GOING = "keep-going"
    CONVERGED = "converged"
    ESCALATE = "escalate"
    CLOSED = "closed"


def settled(*, open_count: int, mergeability: Mergeability, ci: CiStatus) -> bool:
    ci_clears = ci in (CiStatus.GREEN, CiStatus.ABSENT)
    return open_count == 0 and mergeability is Mergeability.MERGEABLE and ci_clears


def patience_exhausted(elapsed: float, *, timeout: float = REVIEW_TIMEOUT_SECONDS) -> bool:
    # `elapsed` is measured by the shell (now minus head_first_seen_at) and handed in; the core
    # never reads the wall itself.
    return elapsed > timeout


def decide(
    review: ReviewDisposition,
    *,
    elapsed: float,
    ci: CiStatus,
    mergeability: Mergeability,
    open_count: int,
    escalating: bool,
    pr_state: PrState,
) -> Outcome:
    # One total decision over the round, a priority order rather than symmetric axes. A terminal
    # PR ends the loop ahead of everything: a merge is the strongest convergence there is, and a
    # close ends it unmerged — both read from pr_state, since mergeability goes UNKNOWN once a PR
    # leaves the open state. Then escalation overrides; a reviewer the loop still has patience for
    # is waited on; a settled PR converges; otherwise keep going.
    if pr_state is PrState.MERGED:
        return Outcome.CONVERGED
    if pr_state is PrState.CLOSED:
        return Outcome.CLOSED
    if escalating:
        return Outcome.ESCALATE
    if review is ReviewDisposition.PENDING and not patience_exhausted(elapsed):
        return Outcome.WAIT
    if settled(open_count=open_count, mergeability=mergeability, ci=ci):
        return Outcome.CONVERGED
    return Outcome.KEEP_GOING
