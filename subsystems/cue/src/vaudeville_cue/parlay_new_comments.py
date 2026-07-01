from __future__ import annotations

from collections.abc import Sequence

from vaudeville_cue.parlay_comments import ReviewComment


def new_comments(
    comments: Sequence[ReviewComment], *, seen: frozenset[int]
) -> tuple[ReviewComment, ...]:
    return tuple(comment for comment in comments if comment.id not in seen)
