from __future__ import annotations

import subprocess
from collections.abc import Callable

from vaudeville_cue.parlay_comments import CommentSource, ReviewComment
from vaudeville_cue.parlay_github import GithubError

Post = Callable[[str, str], None]


def reply(
    repo: str, pr: int, comment: ReviewComment, body: str, *, post: Post | None = None
) -> None:
    # An inline review comment carries a thread, so its disposition threads under it and the
    # reviewer marks it resolved; a conversation comment or a review body has no inline thread, so
    # its reply is a new comment on the PR conversation. `post` is the gh boundary, injected.
    if comment.source is CommentSource.REVIEW and comment.path:
        endpoint = f"repos/{repo}/pulls/{pr}/comments/{comment.id}/replies"
    else:
        endpoint = f"repos/{repo}/issues/{pr}/comments"
    (post or _gh_post)(endpoint, body)


def _gh_post(endpoint: str, body: str) -> None:
    result = subprocess.run(  # noqa: S603
        ["gh", "api", "-X", "POST", endpoint, "-f", f"body={body}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise GithubError(f"posting a reply to {endpoint} failed:\n{result.stderr.strip()}")
