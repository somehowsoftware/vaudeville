from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


class CreateRelease(Protocol):
    def __call__(self, *, repository: str, version: str, asset: Path, target: str) -> None: ...


@dataclass(frozen=True)
class GhOutcome:
    returncode: int
    stdout: str
    stderr: str


RunGh = Callable[[list[str]], GhOutcome]


def create_release_argv(*, repository: str, version: str, asset: Path, target: str) -> list[str]:
    # `--target` pins the new tag to the exposition commit Publish just pushed, rather than letting
    # `gh` resolve it to the default-branch head at release time. Without it, anything pushed to
    # the Published Home's default branch between that push and this call would steal the tag, and
    # the Release would carry one version's asset against another commit's source.
    return [
        "gh",
        "release",
        "create",
        version,
        str(asset),
        "--repo",
        repository,
        "--target",
        target,
        "--title",
        version,
        "--notes",
        f"Vaudeville {version}: the integrated install artifact. "
        "Download this asset and activate its carried installer.",
    ]


def list_tags_argv(repository: str) -> list[str]:
    # The collision check is against git tags, not releases: `gh release create` reuses an existing
    # tag (attaching the release to its stale commit instead of the Published Home's head), and a
    # tag can outlive its release (a release deleted without its tag, a hand-made tag). `--paginate`
    # walks every page so no tag is missed.
    return ["gh", "api", "--paginate", f"repos/{repository}/tags", "--jq", ".[].name"]


def raise_if_release_creation_failed(repository: str, version: str, outcome: GhOutcome) -> None:
    if outcome.returncode != 0:
        raise ReleaseCreationFailed(repository, version, outcome.returncode, outcome.stderr.strip())


def tags_from(repository: str, outcome: GhOutcome) -> list[str]:
    # An unreachable Published Home fails loudly rather than silently reporting no tags, which would
    # let a colliding version slip through.
    if outcome.returncode != 0:
        raise TagListingFailed(repository, outcome.returncode, outcome.stderr.strip())
    return [line for line in outcome.stdout.splitlines() if line]


def create_release_with_gh(
    *,
    repository: str,
    version: str,
    asset: Path,
    target: str,
    run_gh: RunGh,
) -> None:
    outcome = run_gh(
        create_release_argv(repository=repository, version=version, asset=asset, target=target)
    )
    raise_if_release_creation_failed(repository, version, outcome)


def release_creator(run_gh: RunGh) -> CreateRelease:
    # Bind the authenticated gh runner into a CreateRelease the composition root injects.
    def create_release(*, repository: str, version: str, asset: Path, target: str) -> None:
        create_release_with_gh(
            repository=repository, version=version, asset=asset, target=target, run_gh=run_gh
        )

    return create_release


def tags_in(repository: str, run_gh: RunGh) -> list[str]:
    return tags_from(repository, run_gh(list_tags_argv(repository)))


class TagListingFailed(RuntimeError):
    def __init__(self, repository: str, returncode: int, detail: str = "") -> None:
        super().__init__(repository, returncode, detail)
        self.repository = repository
        self.returncode = returncode
        self.detail = detail

    def __str__(self) -> str:
        base = (
            f"Could not list the tags already in {self.repository} "
            f"(`gh api .../tags` exited {self.returncode}); the next version cannot be computed."
        )
        return f"{base}\n{self.detail}" if self.detail else base


class ReleaseCreationFailed(RuntimeError):
    def __init__(self, repository: str, version: str, returncode: int, detail: str = "") -> None:
        super().__init__(repository, version, returncode, detail)
        self.repository = repository
        self.version = version
        self.returncode = returncode
        self.detail = detail

    def __str__(self) -> str:
        base = (
            f"Publishing version {self.version!r} to {self.repository} failed "
            f"(`gh release create` exited {self.returncode}). A fresh Published Home must already "
            "carry a base commit for `gh` to tag against."
        )
        return f"{base}\n{self.detail}" if self.detail else base
