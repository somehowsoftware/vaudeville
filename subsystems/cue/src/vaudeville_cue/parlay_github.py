from __future__ import annotations

import json
import subprocess
from collections.abc import Sequence

from vaudeville_cue.parlay_reviewer import JsonObject
from vaudeville_cue.parlay_snapshot import Snapshot, snapshot

CI_WORKFLOW = "ci.yml"

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
    return snapshot(
        issue_comments=_gh_paginated(f"repos/{repo}/issues/{pr}/comments"),
        review_comments=_gh_paginated(f"repos/{repo}/pulls/{pr}/comments"),
        reviews=_gh_paginated(f"repos/{repo}/pulls/{pr}/reviews"),
        reactions=_gh_paginated(f"repos/{repo}/issues/{pr}/reactions"),
        pr_view=pr_view,
        ci_runs=_ci_runs(repo, head_sha),
    )


def _ci_runs(repo: str, head_sha: str) -> list[JsonObject]:
    if not head_sha:
        return []
    args = ["gh", "run", "list", "--repo", repo, "--workflow", CI_WORKFLOW]
    args += ["--commit", head_sha, "--limit", "1", "--json", _CI_FIELDS]
    return _gh_list(args)


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


def _gh_paginated(endpoint: str) -> list[JsonObject]:
    # GitHub's list endpoints page at 30; --paginate walks every page and --jq streams each
    # element on its own line. Without it, a PR past its first page of comments would converge
    # while later reviewer comments sit unseen.
    raw = _gh(["gh", "api", endpoint, "--paginate", "--jq", ".[]"])
    items = (json.loads(line) for line in raw.splitlines() if line.strip())
    return [item for item in items if isinstance(item, dict)]


def _gh_object(args: Sequence[str]) -> JsonObject:
    raw = _gh(args).strip()
    data = json.loads(raw) if raw else {}
    return data if isinstance(data, dict) else {}
