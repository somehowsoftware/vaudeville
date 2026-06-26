"""The Pin: one Contributor Repo frozen at the commit its Session Clone was produced at."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from vaudeville_ringmaster.session_clone import recorded_clone_sha_at


@dataclass(frozen=True)
class Pin:
    name: str
    remote: str
    commit: str


def pin_clone(name: str, remote: str, clone_root: Path) -> Pin:
    commit = recorded_clone_sha_at(clone_root)
    if commit is None:
        raise UnpinnableClone(name)
    return Pin(name=name, remote=remote, commit=commit)


class UnpinnableClone(RuntimeError):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.name = name

    def __str__(self) -> str:
        return (
            f"Session Clone {self.name!r} carries no recorded clone-time commit, so it cannot be "
            "pinned. It was not produced by `ringmaster clone`; re-run Clone to open a fresh "
            "Session before Publish."
        )
