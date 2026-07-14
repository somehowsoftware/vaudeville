from __future__ import annotations

import json
import subprocess
from collections.abc import Sequence
from dataclasses import dataclass

from vaudeville_cue.parlay_reviewer import JsonObject
from vaudeville_cue.parlay_snapshot import Snapshot, snapshot

CI_WORKFLOW = "ci.yml"

# GitHub runs only a workflow whose state is "active"; these are its other documented states, all
# producing no run. Only they clear the CI gate -- an unrecognized state stays present, so a new
# running state is never mistaken for absent CI and converged silently.
_INERT_WORKFLOW_STATES = frozenset(
    {"disabled_manually", "disabled_inactivity", "disabled_fork", "deleted"}
)

_PR_FIELDS = "mergeable,mergeStateStatus,headRefOid,state"
_CI_FIELDS = "databaseId,status,conclusion,url"


class GithubError(RuntimeError):
    pass


def current_repo() -> str:
    return _gh(["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"]).strip()


def current_head(repo: str, pr: int) -> str:
    args = [
        "gh",
        "pr",
        "view",
        str(pr),
        "--repo",
        repo,
        "--json",
        "headRefOid",
        "-q",
        ".headRefOid",
    ]
    return _gh(args).strip()


def poll(repo: str, pr: int) -> Snapshot:
    pr_view = _gh_object(["gh", "pr", "view", str(pr), "--repo", repo, "--json", _PR_FIELDS])
    head_sha = str(pr_view.get("headRefOid", ""))
    ci_runs = _ci_runs(repo, head_sha) if _ci_present(_ci_workflows(repo)) else None
    return snapshot(
        issue_comments=_gh_paginated(f"repos/{repo}/issues/{pr}/comments"),
        review_comments=_gh_paginated(f"repos/{repo}/pulls/{pr}/comments"),
        reviews=_gh_paginated(f"repos/{repo}/pulls/{pr}/reviews"),
        reactions=_gh_paginated(f"repos/{repo}/issues/{pr}/reactions"),
        pr_view=pr_view,
        ci_runs=ci_runs,
    )


def _ci_workflows(repo: str) -> list[JsonObject]:
    return _gh_paginated(f"repos/{repo}/actions/workflows", ".workflows[]")


def _ci_present(workflows: Sequence[JsonObject]) -> bool:
    # GitHub lists each workflow by repo-relative path (".github/workflows/ci.yml") and keeps
    # listing a disabled or deleted one though it fires no run, so a bare basename match would leave
    # settled() awaiting a run that never comes. A gh failure raises upstream, so absence is only
    # ever a clean listing, never a swallowed error.
    return any(
        str(w.get("path", "")).rsplit("/", 1)[-1] == CI_WORKFLOW
        and str(w.get("state", "active")) not in _INERT_WORKFLOW_STATES
        for w in workflows
    )


def _ci_runs(repo: str, head_sha: str) -> list[JsonObject]:
    if not head_sha:
        return []
    args = ["gh", "run", "list", "--repo", repo, "--workflow", CI_WORKFLOW]
    args += ["--commit", head_sha, "--limit", "1", "--json", _CI_FIELDS]
    return _gh_list(args)


@dataclass(frozen=True)
class RangeCommit:
    sha: str
    parents: int


def commits_since(repo: str, base: str, head: str) -> tuple[RangeCommit, ...]:
    # The compare endpoint walks the whole interval rather than the head alone, so a merge or an
    # answering commit buried behind a later single-parent commit still surfaces. Once the branch
    # has merged main the interval also carries main's own commits and the merges among them, but
    # those enter only through that reconciliation, so they mark a real merge and never invent one.
    raw = _gh(
        [
            "gh",
            "api",
            f"repos/{repo}/compare/{base}...{head}",
            "--jq",
            "[.commits[] | {sha: .sha, parents: (.parents | length)}]",
        ]
    ).strip()
    data = json.loads(raw) if raw else []
    return tuple(RangeCommit(sha=str(item["sha"]), parents=int(item["parents"])) for item in data)


def _gh(args: Sequence[str]) -> str:
    result = subprocess.run(list(args), capture_output=True, text=True, check=False)  # noqa: S603
    if result.returncode != 0:
        raise GithubError(f"`{' '.join(args)}` failed:\n{result.stderr.strip()}")
    return result.stdout


def _gh_list(args: Sequence[str]) -> list[JsonObject]:
    raw = _gh(args).strip()
    if not raw:
        return []
    data = json.loads(raw)
    return [item for item in data if isinstance(item, dict)] if isinstance(data, list) else []


def _gh_paginated(endpoint: str, jq: str = ".[]") -> list[JsonObject]:
    # GitHub pages these list endpoints at 30, and a missed later page silently converges a PR it
    # should not -- a reviewer comment past page one goes unread, or a ci.yml among more than thirty
    # workflows reads as absent CI. The jq selects the array to stream: ".[]" for a bare list,
    # ".workflows[]" for the workflows endpoint, which wraps its list in an object.
    raw = _gh(["gh", "api", endpoint, "--paginate", "--jq", jq])
    items = (json.loads(line) for line in raw.splitlines() if line.strip())
    return [item for item in items if isinstance(item, dict)]


def _gh_object(args: Sequence[str]) -> JsonObject:
    raw = _gh(args).strip()
    data = json.loads(raw) if raw else {}
    return data if isinstance(data, dict) else {}
