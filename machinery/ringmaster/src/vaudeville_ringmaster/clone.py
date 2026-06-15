"""The Clone operation."""

from __future__ import annotations

from pathlib import Path

from vaudeville_ringmaster.registry import Registry
from vaudeville_ringmaster.session_clone import SessionClone, clone_each_contributor_repo_into


def clone(registry: Registry, session_clones_dir: Path) -> list[SessionClone]:
    return clone_each_contributor_repo_into(registry, session_clones_dir)
