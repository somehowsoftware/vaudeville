from __future__ import annotations

import json
from dataclasses import dataclass

from vaudeville_ringmaster.github_release import GhOutcome, RunGh
from vaudeville_ringmaster.predecessor import (
    AbsentFromPredecessor,
    CarriedByPredecessor,
    ContributorBaseline,
)


@dataclass(frozen=True)
class MergedPullRequest:
    number: int
    title: str
    body: str
    author: str


def repo_slug_from(remote: str) -> str:
    return remote.removeprefix("https://github.com/").removesuffix(".git")


def changeset_commits_argv(slug: str, baseline: ContributorBaseline, head: str) -> list[str]:
    match baseline:
        case CarriedByPredecessor(commit):
            return _commit_range_argv(slug, commit, head)
        case AbsentFromPredecessor():
            return _whole_history_argv(slug, head)


def _commit_range_argv(slug: str, baseline_commit: str, head: str) -> list[str]:
    # The compare endpoint caps its commits list at 250 and emits the Link headers `--paginate`
    # follows only when a paging parameter is present, so `per_page` is what makes `--paginate`
    # walk a range past 250 rather than silently dropping the tail.
    return [
        "gh",
        "api",
        "--paginate",
        f"repos/{slug}/compare/{baseline_commit}...{head}?per_page=100",
        "--jq",
        ".commits[].sha",
    ]


def _whole_history_argv(slug: str, head: str) -> list[str]:
    return [
        "gh",
        "api",
        "--paginate",
        f"repos/{slug}/commits?sha={head}",
        "--jq",
        ".[].sha",
    ]


def pull_requests_for_commit_argv(slug: str, sha: str) -> list[str]:
    return [
        "gh",
        "api",
        f"repos/{slug}/commits/{sha}/pulls",
        "--jq",
        ".[] | {number: .number, title: .title, body: .body, author: .user.login}",
    ]


def commit_shas_in(slug: str, outcome: GhOutcome) -> list[str]:
    if outcome.returncode != 0:
        raise ChangeHistoryUnavailable(slug, outcome.returncode, outcome.stderr.strip())
    return [line for line in outcome.stdout.splitlines() if line]


def merged_pull_requests_from(slug: str, outcome: GhOutcome) -> list[MergedPullRequest]:
    if outcome.returncode != 0:
        raise ChangeHistoryUnavailable(slug, outcome.returncode, outcome.stderr.strip())
    pull_requests: list[MergedPullRequest] = []
    for line in outcome.stdout.splitlines():
        if not line:
            continue
        payload = json.loads(line)
        pull_requests.append(
            MergedPullRequest(
                number=payload["number"],
                title=payload["title"] or "",
                body=payload["body"] or "",
                author=payload["author"] or "",
            )
        )
    return pull_requests


def merged_pull_requests(
    slug: str, baseline: ContributorBaseline, head: str, run_gh: RunGh
) -> tuple[MergedPullRequest, ...]:
    shas = commit_shas_in(slug, run_gh(changeset_commits_argv(slug, baseline, head)))
    return _pull_requests_across(slug, shas, run_gh)


def _pull_requests_across(
    slug: str, shas: list[str], run_gh: RunGh
) -> tuple[MergedPullRequest, ...]:
    seen: dict[int, MergedPullRequest] = {}
    for sha in shas:
        outcome = run_gh(pull_requests_for_commit_argv(slug, sha))
        for pull_request in merged_pull_requests_from(slug, outcome):
            seen.setdefault(pull_request.number, pull_request)
    return tuple(seen.values())


class ChangeHistoryUnavailable(RuntimeError):
    def __init__(self, slug: str, returncode: int, detail: str = "") -> None:
        super().__init__(slug, returncode, detail)
        self.slug = slug
        self.returncode = returncode
        self.detail = detail

    def __str__(self) -> str:
        base = (
            f"Could not read the change history of {self.slug} "
            f"(`gh api` exited {self.returncode}); the Changeset since the Predecessor "
            "cannot be assembled."
        )
        return f"{base}\n{self.detail}" if self.detail else base
