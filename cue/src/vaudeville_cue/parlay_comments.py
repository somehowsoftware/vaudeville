from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum

from vaudeville_cue.parlay_reviewer import JsonObject, is_reviewer, login

# Codex's findings arrive as inline comments; the body it posts with every review is a per-pass
# envelope that carries none. A body reaches triage only when it positively reads as a finding: when
# it carries the marker an inline finding's footer leaves, which the envelope never does. Positive
# recognition is the safe polarity — a novel finding shape escapes triage, as it did before bodies
# were read at all, rather than the envelope being queued afresh under the review's id every head
# and blocking convergence. Held as data so a newly-seen marker is a one-line addition.
_FINDING_MARKERS = ("Useful? React with",)


class CommentSource(Enum):
    REVIEW = "review"
    CONVERSATION = "conversation"


@dataclass(frozen=True)
class ReviewComment:
    id: int
    author: str
    body: str
    timestamp: str
    source: CommentSource = CommentSource.CONVERSATION
    path: str = ""
    line: int | None = None
    html_url: str = ""


def reviewer_comments(
    issue_comments: Sequence[JsonObject],
    review_comments: Sequence[JsonObject],
    reviews: Sequence[JsonObject],
    head_sha: str,
) -> tuple[ReviewComment, ...]:
    # Everything the reviewer left for triage on this PR: conversation comments, inline review
    # comments, and findings carried in a review body rather than an inline comment.
    return (
        *_from_endpoint(issue_comments, CommentSource.CONVERSATION),
        *_from_endpoint(review_comments, CommentSource.REVIEW),
        *_from_review_bodies(reviews, head_sha),
    )


def _from_endpoint(items: Sequence[JsonObject], source: CommentSource) -> tuple[ReviewComment, ...]:
    return tuple(
        ReviewComment(
            id=_as_int(item.get("id")),
            author=login(item),
            body=str(item.get("body", "")),
            timestamp=str(item.get("created_at", "")),
            source=source,
            path=str(item.get("path", "")),
            line=_as_int_or_none(item.get("line")),
            html_url=str(item.get("html_url", "")),
        )
        for item in items
        if is_reviewer(login(item))
    )


def _from_review_bodies(reviews: Sequence[JsonObject], head_sha: str) -> tuple[ReviewComment, ...]:
    # A finding Codex leaves in a review body with no inline comment would otherwise mark the head
    # reviewed and let the PR converge with it unread. Two gates beyond the reviewer: only the
    # head's review counts (a body on an outrun commit is about code that has moved), and only a
    # body that positively reads as a finding, so the envelope every review carries never queues.
    return tuple(
        ReviewComment(
            id=_as_int(review.get("id")),
            author=login(review),
            body=str(review.get("body", "")),
            timestamp=str(review.get("submitted_at", "")),
            source=CommentSource.REVIEW,
            html_url=str(review.get("html_url", "")),
        )
        for review in reviews
        if is_reviewer(login(review)) and str(review.get("commit_id", "")) == head_sha
        if _carries_finding(str(review.get("body", "")))
    )


def _carries_finding(body: str) -> bool:
    return any(marker in body for marker in _FINDING_MARKERS)


def _as_int(value: object) -> int:
    return value if isinstance(value, int) else 0


def _as_int_or_none(value: object) -> int | None:
    return value if isinstance(value, int) else None
