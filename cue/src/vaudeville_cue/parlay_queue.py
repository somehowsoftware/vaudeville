from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path

from vaudeville_cue.parlay_comments import CommentSource, ReviewComment


def write_open_comments(rendered: Path, data: Path, comments: Sequence[ReviewComment]) -> None:
    rendered.parent.mkdir(parents=True, exist_ok=True)
    rendered.write_text(render_comments(comments), encoding="utf-8")
    data.write_text(_serialize(comments), encoding="utf-8")


def write_history(rendered: Path, data: Path, comments: Sequence[ReviewComment]) -> None:
    # The escalation's substrate accumulates: once a sense captures a finding it stays, even after
    # its head is outrun and the poll stops returning it — a review-body finding, gated to the head
    # it was left on, is the case that forced this. Re-deriving the history from each poll would
    # drop it before a three-round trip; instead union the pass's comments into what is already on
    # disk, first capture kept, so the committee sees every round's symptoms and not just the live
    # ones. The invariant that makes this complete: the sense that surfaces a finding for triage is
    # the same sense that writes it here, so nothing the agent ever acted on can be missing.
    merged = _merge_by_id(read_comment_data(data), comments)
    rendered.parent.mkdir(parents=True, exist_ok=True)
    rendered.write_text(render_comments(merged), encoding="utf-8")
    data.write_text(_serialize(merged), encoding="utf-8")


def read_comment_data(data: Path) -> tuple[ReviewComment, ...]:
    if not data.is_file():
        return ()
    return _deserialize(data.read_text(encoding="utf-8"))


def _merge_by_id(
    prior: Sequence[ReviewComment], current: Sequence[ReviewComment]
) -> tuple[ReviewComment, ...]:
    # First capture kept, insertion order preserved: earlier rounds' findings stay ahead of later
    # ones, and re-polling a comment already on disk neither reorders nor overwrites it.
    by_id = {comment.id: comment for comment in prior}
    for comment in current:
        by_id.setdefault(comment.id, comment)
    return tuple(by_id.values())


def render_comments(comments: Sequence[ReviewComment]) -> str:
    if not comments:
        return "(no reviewer comments)\n"
    blocks = [
        f"## comment {comment.id} — {comment.author} — {comment.timestamp}\n"
        f"{_where(comment)}\n\n{comment.body}\n"
        for comment in comments
    ]
    return "\n".join(blocks)


def _where(comment: ReviewComment) -> str:
    if comment.source is CommentSource.REVIEW and comment.path:
        line = f":{comment.line}" if comment.line is not None else ""
        return f"{comment.source.value} · {comment.path}{line} · {comment.html_url}"
    return f"{comment.source.value} · {comment.html_url}"


def _serialize(comments: Sequence[ReviewComment]) -> str:
    return (
        json.dumps(
            [
                {
                    "id": comment.id,
                    "author": comment.author,
                    "body": comment.body,
                    "timestamp": comment.timestamp,
                    "source": comment.source.value,
                    "path": comment.path,
                    "line": comment.line,
                    "html_url": comment.html_url,
                }
                for comment in comments
            ],
            indent=2,
        )
        + "\n"
    )


def _deserialize(stored: str) -> tuple[ReviewComment, ...]:
    return tuple(
        ReviewComment(
            id=int(item["id"]),
            author=str(item["author"]),
            body=str(item["body"]),
            timestamp=str(item["timestamp"]),
            source=CommentSource(item["source"]),
            path=str(item["path"]),
            line=item["line"],
            html_url=str(item["html_url"]),
        )
        for item in json.loads(stored)
    )
