from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import replace

from vaudeville_cue.parlay_command import fail, resolved_repo, scratch_root, yesno
from vaudeville_cue.parlay_github import GithubError, current_head
from vaudeville_cue.parlay_queue import read_open_comments, write_open_comments
from vaudeville_cue.parlay_reply import reply
from vaudeville_cue.parlay_store import head_stamp, parlay_layout, read_state, write_state
from vaudeville_cue.parlay_tally import Tally, escalating, resolve, waive


def run_record(pr: int, repo: str | None, comment_id: int, body: str) -> None:
    # Recording a disposition and posting its reply are one act, so the reply cannot be dropped:
    # the post runs first, and only a posted reply clears the comment from the queue. A failed post
    # leaves the comment open to retry — a re-reply is the safe error, a dropped one the regression.
    resolved = resolved_repo(repo)
    layout = parlay_layout(scratch_root(), resolved, pr)
    state = read_state(layout.state)
    queue = read_open_comments(layout.open_data)
    comment = next((entry for entry in queue if entry.id == comment_id), None)
    if comment is None:
        fail(f"comment {comment_id} is not in PR {pr}'s open queue.")
    try:
        reply(resolved, pr, comment, body)
    except GithubError as failure:
        fail(failure)
    tally = resolve(state.tally, addressed=frozenset({comment_id}))
    remaining = tuple(entry for entry in queue if entry.id != comment_id)
    write_state(layout.state, replace(state, tally=tally))
    write_open_comments(layout.open_comments, layout.open_data, remaining)
    print(f"recorded {comment_id}   addressed: {len(tally.addressed)}   open: {len(tally.open)}")


def run_begin(pr: int, repo: str | None, *, now: Callable[[], float] = time.time) -> None:
    # The head comes under watch when the PR opens, not at the first post-checkpoint sense, so a
    # fast +1 in the gap is judged against a clock that already started. The stamp lives in the
    # on-disk ledger, so it is inherited through the checkpoint into the watch loop.
    resolved = resolved_repo(repo)
    layout = parlay_layout(scratch_root(), resolved, pr)
    state = read_state(layout.state)
    try:
        head = current_head(resolved, pr)
    except GithubError as failure:
        fail(failure)
    seen_at = head_stamp(state, head=head, moment=now())
    write_state(layout.state, replace(state, head=head, head_first_seen_at=seen_at))
    print(f"watching: head {head} first seen at {seen_at}")


def run_waive(pr: int, repo: str | None) -> None:
    resolved = resolved_repo(repo)
    layout = parlay_layout(scratch_root(), resolved, pr)
    state = read_state(layout.state)
    tally = waive(state.tally)
    write_state(layout.state, replace(state, tally=tally))
    print(_waive_summary(tally))


def _waive_summary(tally: Tally) -> str:
    # The round count is left standing; what the waiver changed is the derived stop, so the
    # confirmation shows both — the history held, the escalation cleared.
    return f"rounds: {tally.rounds}   escalate: {yesno(escalating(tally))}"
