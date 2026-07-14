from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import replace
from pathlib import Path

from vaudeville_cue.parlay_command import fail, resolved_repo, scratch_root
from vaudeville_cue.parlay_github import GithubError, RangeCommit, commits_since, poll
from vaudeville_cue.parlay_new_comments import new_comments
from vaudeville_cue.parlay_provenance import CommitProvenance, classify, is_forced_round
from vaudeville_cue.parlay_queue import write_history, write_open_comments
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
Compare = Callable[[str, str, str], tuple[RangeCommit, ...]]


def run_watch(
    pr: int,
    repo: str | None,
    interval: float,
    max_iterations: int,
    *,
    now: Callable[[], float] = time.time,
    poll: Poll = poll,
    wait: Wait = wait_for_reviewer,
    compare: Compare = commits_since,
    scratch: Callable[[], Path] = scratch_root,
) -> None:
    resolved = resolved_repo(repo)
    layout = parlay_layout(scratch(), resolved, pr)
    try:
        sensed, state, seen_at = _sense(resolved, pr, layout, interval, now, poll, wait, compare)
        tally, new_count = _observe_round(resolved, layout, state, sensed, seen_at, compare)
    except GithubError as failure:
        fail(failure)
    print(watch_report(sensed, seen_at, tally, new_count, layout, max_iterations, now))


def _sense(
    repo: str,
    pr: int,
    layout: ParlayLayout,
    interval: float,
    now: Callable[[], float],
    poll: Poll,
    wait: Wait,
    compare: Compare,
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
        forced=is_forced_round(_head_provenance(repo, state, sensed, compare)),
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
    repo: str,
    layout: ParlayLayout,
    state: RoundState,
    sensed: Snapshot,
    seen_at: float,
    compare: Compare,
) -> tuple[Tally, int]:
    # The open queue is rewritten whole so it survives a re-watch that runs before triage.
    fresh = frozenset(comment.id for comment in new_comments(sensed.comments, seen=state.seen))
    forced = is_forced_round(_head_provenance(repo, state, sensed, compare))
    tally = observe(state.tally, surfaced=fresh, forced=forced)
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
    # The escalation reads the whole run's findings, not the pruned queue: accumulate every reviewer
    # comment this sense saw onto the history, disposed rounds and outrun review bodies alike, so
    # the committee sees the repetition even once a finding has left the poll.
    write_history(layout.history, layout.history_data, sensed.comments)
    return tally, len(fresh)


def _head_provenance(
    repo: str, state: RoundState, sensed: Snapshot, compare: Compare
) -> CommitProvenance:
    if state.head == "" or sensed.head_sha == state.head:
        return CommitProvenance.UNMOVED
    gained = compare(repo, state.head, sensed.head_sha)
    answered = {answer.sha for answer in state.answers}
    return classify(
        state.head,
        sensed.head_sha,
        merged_in_range=any(commit.parents >= 2 for commit in gained),
        answered_in_range=any(commit.sha in answered for commit in gained),
    )
