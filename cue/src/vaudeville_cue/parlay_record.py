from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import replace
from pathlib import Path

from vaudeville_cue.parlay_command import fail, resolved_repo, scratch_root, yesno
from vaudeville_cue.parlay_comments import ReviewComment
from vaudeville_cue.parlay_github import GithubError, current_head
from vaudeville_cue.parlay_queue import read_comment_data, write_open_comments
from vaudeville_cue.parlay_reply import reply
from vaudeville_cue.parlay_store import (
    Answer,
    RoundState,
    head_stamp,
    parlay_layout,
    read_state,
    write_state,
)
from vaudeville_cue.parlay_tally import Tally, escalating, resolve, waive

Reply = Callable[[str, int, ReviewComment, str], None]


def run_record(
    pr: int,
    repo: str | None,
    comment_id: int,
    body: str,
    *,
    fix_sha: str | None = None,
    rejected: bool = False,
    scratch: Callable[[], Path] = scratch_root,
    reply: Reply = reply,
) -> None:
    if rejected and fix_sha is not None:
        fail("a reasoned rejection changes no code, so it takes no --fix-sha.")
    if not rejected and fix_sha is None:
        fail("a fix must name the commit that answered it, via --fix-sha.")
    resolved = resolved_repo(repo)
    layout = parlay_layout(scratch(), resolved, pr)
    state = read_state(layout.state)
    queue = read_comment_data(layout.open_data)
    comment = next((entry for entry in queue if entry.id == comment_id), None)
    if comment is None:
        fail(f"comment {comment_id} is not in PR {pr}'s open queue.")
    # The post runs before the state write so a dropped reply is impossible: a failed post leaves
    # the comment open to retry, and only a posted reply clears it. A re-reply is the safe error.
    try:
        reply(resolved, pr, comment, body)
    except GithubError as failure:
        fail(failure)
    updated = record_disposition(state, comment_id, fix_sha=fix_sha)
    remaining = tuple(entry for entry in queue if entry.id != comment_id)
    write_state(layout.state, updated)
    write_open_comments(layout.open_comments, layout.open_data, remaining)
    print(
        f"recorded {comment_id}   addressed: {len(updated.tally.addressed)}   "
        f"open: {len(updated.tally.open)}"
    )


def record_disposition(state: RoundState, comment_id: int, *, fix_sha: str | None) -> RoundState:
    tally = resolve(state.tally, addressed=frozenset({comment_id}))
    answers = state.answers if fix_sha is None else state.answers | {Answer(comment_id, fix_sha)}
    return replace(state, tally=tally, answers=answers)


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
