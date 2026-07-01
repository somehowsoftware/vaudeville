from __future__ import annotations

import time
from collections.abc import Callable

from vaudeville_cue.parlay_decide import Outcome, decide
from vaudeville_cue.parlay_github import GithubError, poll
from vaudeville_cue.parlay_reviewer import disposition
from vaudeville_cue.parlay_snapshot import Snapshot

# The wait's re-poll cadence, well under GitHub's authenticated rate limit.
_WAIT_TICK = 30.0

# How many consecutive re-poll failures the wait tolerates before it stops swallowing them. A blip
# is the absence of an observation, so the wait keeps the last-good snapshot and tries the next
# tick; a run past this budget is a persistent outage and surfaces rather than waiting silently to a
# convergence read off stale state.
_BLIP_BUDGET = 3


def wait_for_reviewer(
    repo: str,
    pr: int,
    sensed: Snapshot,
    *,
    head_first_seen_at: float,
    escalating: bool,
    open_count: int,
    interval: float,
    poll: Callable[[str, int], Snapshot] = poll,
    now: Callable[[], float] = time.time,
    sleep: Callable[[float], None] = time.sleep,
    tick: float = _WAIT_TICK,
    blip_budget: int = _BLIP_BUDGET,
) -> tuple[Snapshot, float]:
    # While `decide` reads WAIT — the reviewer has not ruled on this head and patience remains —
    # sleep and re-sense; stop the moment it reads anything else or the per-call budget is spent.
    # Re-deriving through the same `decide` keeps "has the reviewer settled?" from being answered
    # one way here and another at the verdict. A head that moves while we wait was first seen now,
    # so its patience restarts and the fresh stamp is carried back with the snapshot it belongs to.
    #
    # A re-poll can fail on a transient gh hiccup: the absence of an observation, not a degraded
    # one. The wait keeps the last-good snapshot and tries the next tick, but may return only a
    # snapshot a poll confirmed. While a blip is outstanding it keeps polling rather than exiting on
    # the stale look, so patience running out mid-blip cannot converge a snapshot that predates the
    # blip. An unrecovered blip — the budget spent, or the interval elapsed with the latest poll
    # still failing — surfaces, leaving state-unknown at the boundary, not laundered into a verdict.
    deadline = now() + interval
    seen_at = head_first_seen_at
    consecutive_blips = 0
    unconfirmed: GithubError | None = None
    while unconfirmed is not None or _still_waiting(
        sensed, head_first_seen_at=seen_at, escalating=escalating, open_count=open_count, now=now
    ):
        remaining = deadline - now()
        if remaining <= 0:
            if unconfirmed is not None:
                raise unconfirmed
            break
        sleep(min(tick, remaining))
        previous_head = sensed.head_sha
        try:
            sensed = poll(repo, pr)
        except GithubError as failure:
            consecutive_blips += 1
            if consecutive_blips > blip_budget:
                raise
            unconfirmed = failure
            continue
        consecutive_blips = 0
        unconfirmed = None
        if sensed.head_sha != previous_head:
            seen_at = now()
    return sensed, seen_at


def _still_waiting(
    sensed: Snapshot,
    *,
    head_first_seen_at: float,
    escalating: bool,
    open_count: int,
    now: Callable[[], float],
) -> bool:
    return (
        decide(
            disposition(sensed.reviewer, head_first_seen_at=head_first_seen_at),
            elapsed=now() - head_first_seen_at,
            ci=sensed.ci.status,
            mergeability=sensed.mergeability,
            open_count=open_count,
            escalating=escalating,
            pr_state=sensed.pr_state,
        )
        is Outcome.WAIT
    )
