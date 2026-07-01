from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum

from vaudeville_cue.parlay_comments import ReviewComment, reviewer_comments
from vaudeville_cue.parlay_reviewer import JsonObject, ReviewerSignal, reviewer_signal


class Mergeability(Enum):
    MERGEABLE = "mergeable"
    CONFLICTING = "conflicting"
    # GitHub returns null while it is still computing mergeability, and again once the PR is no
    # longer open, which is why a terminal PR is read from pr_state, not from here.
    UNKNOWN = "unknown"


class PrState(Enum):
    OPEN = "open"
    MERGED = "merged"
    CLOSED = "closed"


class CiStatus(Enum):
    GREEN = "green"
    RED = "red"
    PENDING = "pending"
    NONE = "none"


@dataclass(frozen=True)
class Ci:
    status: CiStatus
    # A handle to the raw log, never the log: its bulk must stay out of the judge's context.
    run_handle: int | None


@dataclass(frozen=True)
class Snapshot:
    comments: tuple[ReviewComment, ...]
    mergeability: Mergeability
    ci: Ci
    reviewer: ReviewerSignal
    pr_state: PrState
    head_sha: str


def snapshot(
    *,
    issue_comments: Sequence[JsonObject],
    review_comments: Sequence[JsonObject],
    reviews: Sequence[JsonObject],
    reactions: Sequence[JsonObject],
    pr_view: JsonObject,
    ci_runs: Sequence[JsonObject],
) -> Snapshot:
    head_sha = str(pr_view.get("headRefOid", ""))
    return Snapshot(
        comments=reviewer_comments(issue_comments, review_comments, reviews, head_sha),
        mergeability=_mergeability(pr_view),
        ci=_ci(ci_runs),
        reviewer=reviewer_signal(reviews, reactions, head_sha),
        pr_state=_pr_state(pr_view),
        head_sha=head_sha,
    )


def _mergeability(pr_view: JsonObject) -> Mergeability:
    raw = pr_view.get("mergeable")
    if raw == "MERGEABLE":
        return Mergeability.MERGEABLE
    if raw == "CONFLICTING":
        return Mergeability.CONFLICTING
    return Mergeability.UNKNOWN


def _pr_state(pr_view: JsonObject) -> PrState:
    raw = pr_view.get("state")
    if raw == "MERGED":
        return PrState.MERGED
    if raw == "CLOSED":
        return PrState.CLOSED
    return PrState.OPEN


def _ci(ci_runs: Sequence[JsonObject]) -> Ci:
    # The caller fetches only the latest run for the commit, so the first is the one.
    if not ci_runs:
        return Ci(status=CiStatus.NONE, run_handle=None)
    run = ci_runs[0]
    handle = _as_int(run.get("databaseId"))
    if run.get("status") != "completed":
        return Ci(status=CiStatus.PENDING, run_handle=handle)
    if run.get("conclusion") == "success":
        return Ci(status=CiStatus.GREEN, run_handle=handle)
    return Ci(status=CiStatus.RED, run_handle=handle)


def _as_int(value: object) -> int:
    return value if isinstance(value, int) else 0
