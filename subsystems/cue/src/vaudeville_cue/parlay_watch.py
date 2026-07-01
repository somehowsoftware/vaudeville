from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import replace
from pathlib import Path

from vaudeville_cue.parlay_command import fail, resolved_repo, scratch_root
from vaudeville_cue.parlay_github import GithubError, poll
from vaudeville_cue.parlay_new_comments import new_comments
from vaudeville_cue.parlay_queue import write_open_comments
from vaudeville_cue.parlay_snapshot import Snapshot
from vaudeville_cue.parlay_store import (
    ParlayLayout,
    RoundState,
    head_stamp,
    parlay_layout,
    read_state,
    write_state,
)
from vaudeville_cue.parlay_tally import Tally, escalating, observe
from vaudeville_cue.parlay_verdict import watch_report
from vaudeville_cue.parlay_wait import wait_for_reviewer

# The gh, git, and clock seams the watch crosses, injected at this edge so the shell's wiring is
# tested by handing it fakes rather than by patching its collaborators.
Poll = Callable[[str, int], Snapshot]
Wait = Callable[..., tuple[Snapshot, float]]


def run_watch(
    pr: int,
    repo: str | None,
    interval: float,
    max_iterations: int,
    *,
    now: Callable[[], float] = time.time,
    poll: Poll = poll,
    wait: Wait = wait_for_reviewer,
    scratch: Callable[[], Path] = scratch_root,
) -> None:
    resolved = resolved_repo(repo)
    layout = parlay_layout(scratch(), resolved, pr)
    try:
        sensed, state, seen_at = _sense(resolved, pr, layout, interval, now, poll, wait)
    except GithubError as failure:
        fail(failure)
    tally, new_count = _observe_round(layout, state, sensed, seen_at)
    print(watch_report(sensed, seen_at, tally, new_count, layout, max_iterations, now))


def _sense(
    repo: str,
    pr: int,
    layout: ParlayLayout,
    interval: float,
    now: Callable[[], float],
    poll: Poll,
    wait: Wait,
) -> tuple[Snapshot, RoundState, float]:
    # Read the ledger, poll the PR, stamp the head this call enters on, and wait for the reviewer
    # to rule on it. The entry escalation, read off the head before the wait, short-circuits a wait
    # the loop would only spend on a stop the operator alone can lift.
    state = read_state(layout.state)
    sensed = poll(repo, pr)
    seen_at = head_stamp(state, head=sensed.head_sha, moment=now())
    entry = observe(
        state.tally,
        surfaced=frozenset(),
        code_changing=code_changing_round(state.head, sensed.head_sha),
    )
    sensed, seen_at = wait(
        repo,
        pr,
        sensed,
        head_first_seen_at=seen_at,
        escalating=escalating(entry),
        open_count=len(state.tally.open),
        interval=interval,
        poll=poll,
        now=now,
    )
    return sensed, state, seen_at


def _observe_round(
    layout: ParlayLayout, state: RoundState, sensed: Snapshot, seen_at: float
) -> tuple[Tally, int]:
    # Fold the settled snapshot into the ledger: one pass, a code-changing round iff the head moved
    # since the last observe — during the wait or between watches alike. The open queue is rewritten
    # whole so it survives a re-watch that runs before triage.
    fresh = frozenset(comment.id for comment in new_comments(sensed.comments, seen=state.seen))
    code_changing = code_changing_round(state.head, sensed.head_sha)
    tally = observe(state.tally, surfaced=fresh, code_changing=code_changing)
    write_state(
        layout.state,
        replace(
            state,
            tally=tally,
            seen=state.seen | fresh,
            head=sensed.head_sha,
            head_first_seen_at=seen_at,
        ),
    )
    open_now = tuple(comment for comment in sensed.comments if comment.id in tally.open)
    write_open_comments(layout.open_comments, layout.open_data, open_now)
    return tally, len(fresh)


def code_changing_round(last_head: str, head_sha: str) -> bool:
    # A fresh ledger has no baseline head, so its first sense is never a round; after that, a moved
    # head means a commit landed — a fix or a merge resolution, both of which escalation must feel.
    return last_head != "" and head_sha != last_head
