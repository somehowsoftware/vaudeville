"""The Worktree."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from vaudeville_ringmaster.registry import Registry


@dataclass(frozen=True)
class Worktree:
    path: Path


def name_of_owning_repo_with_remote(origin_remote_url: str, registry: Registry) -> str | None:
    for name, registered in registry.repos.items():
        if _urls_match_after_normalization(origin_remote_url, registered):
            return name
    return None


def name_of_owning_repo_for(worktree: Worktree, registry: Registry) -> str:
    remote = origin_remote_url_of(worktree)
    name = name_of_owning_repo_with_remote(remote, registry)
    if name is None:
        raise UnrecognizedOwningRepo(worktree, remote)
    return name


def origin_remote_url_of(worktree: Worktree) -> str:
    result = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        cwd=worktree.path,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def clone_root_of(worktree: Worktree) -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=worktree.path,
        capture_output=True,
        text=True,
        check=True,
    )
    return Path(result.stdout.strip())


class UnrecognizedOwningRepo(LookupError):
    def __init__(self, worktree: Worktree, remote: str) -> None:
        super().__init__(worktree, remote)
        self.worktree = worktree
        self.remote = remote

    def __str__(self) -> str:
        return (
            f"Worktree at {self.worktree.path} has remote {self.remote!r}, "
            "which does not match any Contributor Repo in the Registry"
        )


def _urls_match_after_normalization(left: str, right: str) -> bool:
    return _url_with_trailing_slash_and_dot_git_stripped(
        left
    ) == _url_with_trailing_slash_and_dot_git_stripped(right)


def _url_with_trailing_slash_and_dot_git_stripped(url: str) -> str:
    stripped = url.rstrip("/")
    if stripped.endswith(".git"):
        stripped = stripped[: -len(".git")]
    return stripped
