from __future__ import annotations

import dataclasses
import json
from dataclasses import dataclass

from vaudeville_ringmaster.carried_set import CarriedSet
from vaudeville_ringmaster.github_release import RunGh
from vaudeville_ringmaster.merged_pull_request import (
    MergedPullRequest,
    merged_pull_requests,
    repo_slug_from,
)
from vaudeville_ringmaster.pin import Pin
from vaudeville_ringmaster.predecessor import (
    CarriedByPredecessor,
    ContributorBaseline,
    Predecessor,
    baseline_of,
)


@dataclass(frozen=True)
class ContributorChangeset:
    name: str
    baseline: str | None
    head: str
    pull_requests: tuple[MergedPullRequest, ...]


@dataclass(frozen=True)
class RemovedContributor:
    name: str
    last_carried: str


@dataclass(frozen=True)
class Changeset:
    predecessor: str | None
    contributors: tuple[ContributorChangeset, ...]
    removed: tuple[RemovedContributor, ...]


def changeset_of(
    carried_set: CarriedSet, predecessor: Predecessor | None, run_gh: RunGh
) -> Changeset:
    return Changeset(
        predecessor=predecessor.release_name if predecessor is not None else None,
        contributors=tuple(
            _contributor_changeset(pin, baseline_of(predecessor, pin.name), run_gh)
            for pin in carried_set.pins
        ),
        removed=_removed_contributors(predecessor, {pin.name for pin in carried_set.pins}),
    )


def _contributor_changeset(
    pin: Pin, baseline: ContributorBaseline, run_gh: RunGh
) -> ContributorChangeset:
    return ContributorChangeset(
        name=pin.name,
        baseline=baseline.commit if isinstance(baseline, CarriedByPredecessor) else None,
        head=pin.commit,
        pull_requests=merged_pull_requests(
            repo_slug_from(pin.remote), baseline, pin.commit, run_gh
        ),
    )


def _removed_contributors(
    predecessor: Predecessor | None, carried_names: set[str]
) -> tuple[RemovedContributor, ...]:
    if predecessor is None:
        return ()
    return tuple(
        RemovedContributor(name=name, last_carried=commit)
        for name, commit in predecessor.carried_commit_by_contributor.items()
        if name not in carried_names
    )


def changeset_as_json(changeset: Changeset) -> str:
    return json.dumps(dataclasses.asdict(changeset), indent=2)
