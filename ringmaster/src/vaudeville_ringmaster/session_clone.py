"""The Session Clone: a fresh clone of each Contributor Repo, carried between Session commands."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from vaudeville_ringmaster.registry import Registry

# Sidecar inside each Session Clone's .git/ recording the commit SHA the clone was produced
# at. Lives under .git/ so git ignores it; the Pristine guard reads it to detect HEAD movement
# since Clone, even when the operator later pushed their rehearsal fix back to origin/main.
CLONE_TIME_SHA_SIDECAR = Path(".git") / "ringmaster-clone-sha"


@dataclass(frozen=True)
class SessionClone:
    name: str
    path: Path


def clone_each_contributor_repo_into(registry: Registry, target_dir: Path) -> list[SessionClone]:
    discard_all_session_clones_in(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    clones: list[SessionClone] = []
    for name in registry.contributor_names():
        remote = registry.remote_for(name)
        clone_path = target_dir / name
        subprocess.run(
            ["git", "clone", "--branch", "main", remote, str(clone_path)],
            check=True,
            capture_output=True,
        )
        _record_clone_time_sha_at(clone_path)
        clones.append(SessionClone(name=name, path=clone_path))
    return clones


def discard_all_session_clones_in(target_dir: Path) -> None:
    if target_dir.exists():
        shutil.rmtree(target_dir)


def recorded_clone_sha_of(session_clone: SessionClone) -> str | None:
    return recorded_clone_sha_at(session_clone.path)


def recorded_clone_sha_at(clone_root: Path) -> str | None:
    # None when the sidecar is absent: a directory not produced by Clone, which callers fail closed
    # on rather than vouch for a commit they cannot establish.
    sidecar = clone_root / CLONE_TIME_SHA_SIDECAR
    if not sidecar.is_file():
        return None
    return sidecar.read_text().strip()


def require_each_session_clone_present_in(
    registry: Registry, target_dir: Path
) -> list[SessionClone]:
    present: list[SessionClone] = []
    missing: list[str] = []
    for name in registry.contributor_names():
        clone_path = target_dir / name
        if clone_path.is_dir() and (clone_path / ".git").exists():
            present.append(SessionClone(name=name, path=clone_path))
        else:
            missing.append(name)
    if missing:
        raise MissingSessionClones(missing)
    return present


class MissingSessionClones(LookupError):
    def __init__(self, names: list[str]) -> None:
        super().__init__(names)
        self.names = names

    def __str__(self) -> str:
        listing = ", ".join(self.names)
        return f"Session Clones missing: {listing}. Run `ringmaster clone` to open a Session."


def _record_clone_time_sha_at(clone_path: Path) -> None:
    sha = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=clone_path,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    (clone_path / CLONE_TIME_SHA_SIDECAR).write_text(sha + "\n")
