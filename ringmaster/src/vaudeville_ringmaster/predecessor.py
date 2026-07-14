from __future__ import annotations

import re
import tomllib
from collections.abc import Iterable
from dataclasses import dataclass

from vaudeville_ringmaster.github_release import RunGh, tags_in
from vaudeville_ringmaster.provenance import PROVENANCE_FILENAME

_RELEASE_TAG = re.compile(r"^v(\d+)\.(\d+)\.(\d+)\.(\d+)$")


@dataclass(frozen=True)
class Predecessor:
    release_name: str
    carried_commit_by_contributor: dict[str, str]


@dataclass(frozen=True)
class CarriedByPredecessor:
    commit: str


@dataclass(frozen=True)
class AbsentFromPredecessor:
    pass


ContributorBaseline = CarriedByPredecessor | AbsentFromPredecessor


def baseline_of(predecessor: Predecessor | None, contributor_name: str) -> ContributorBaseline:
    if predecessor is None:
        return AbsentFromPredecessor()
    commit = predecessor.carried_commit_by_contributor.get(contributor_name)
    if commit is None:
        return AbsentFromPredecessor()
    return CarriedByPredecessor(commit)


def predecessor_release_name_from(tags: Iterable[str]) -> str | None:
    releases = [
        (tuple(int(field) for field in match.groups()), tag)
        for tag in tags
        if (match := _RELEASE_TAG.match(tag)) is not None
    ]
    if not releases:
        return None
    return max(releases)[1]


def predecessor_provenance_argv(repository: str, release_name: str) -> list[str]:
    return [
        "gh",
        "api",
        f"repos/{repository}/contents/{PROVENANCE_FILENAME}?ref={release_name}",
        "-H",
        "Accept: application/vnd.github.raw",
    ]


def predecessor_from(release_name: str, provenance_text: str) -> Predecessor:
    contributors = tomllib.loads(provenance_text).get("contributors", {})
    return Predecessor(
        release_name=release_name,
        carried_commit_by_contributor={
            name: table["commit"] for name, table in contributors.items()
        },
    )


def predecessor_at(repository: str, release_name: str, run_gh: RunGh) -> Predecessor:
    outcome = run_gh(predecessor_provenance_argv(repository, release_name))
    if outcome.returncode != 0:
        raise PredecessorUnavailable(
            repository, release_name, outcome.returncode, outcome.stderr.strip()
        )
    return predecessor_from(release_name, outcome.stdout)


def resolve_predecessor(repository: str, run_gh: RunGh) -> Predecessor | None:
    release_name = predecessor_release_name_from(tags_in(repository, run_gh))
    if release_name is None:
        return None
    return predecessor_at(repository, release_name, run_gh)


class PredecessorUnavailable(RuntimeError):
    def __init__(
        self, repository: str, release_name: str, returncode: int, detail: str = ""
    ) -> None:
        super().__init__(repository, release_name, returncode, detail)
        self.repository = repository
        self.release_name = release_name
        self.returncode = returncode
        self.detail = detail

    def __str__(self) -> str:
        base = (
            f"Could not read the Provenance of Release {self.release_name} from {self.repository} "
            f"(`gh api` exited {self.returncode}); the Changeset baseline cannot be established."
        )
        return f"{base}\n{self.detail}" if self.detail else base
