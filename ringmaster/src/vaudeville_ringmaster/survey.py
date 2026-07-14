"""The Survey phase: read-only discovery and validation that produces the Manifest."""

from __future__ import annotations

from vaudeville_ringmaster.contribution import discover_contribution_in
from vaudeville_ringmaster.manifest import Manifest, raise_if_manifest_has_collisions
from vaudeville_ringmaster.registry import Registry
from vaudeville_ringmaster.session_clone import SessionClone
from vaudeville_ringmaster.worktree import Worktree, clone_root_of, name_of_owning_repo_for


def survey_manifest(
    registry: Registry,
    session_clones: list[SessionClone],
    worktree: Worktree | None = None,
) -> Manifest:
    owning_name = name_of_owning_repo_for(worktree, registry) if worktree is not None else None
    contributions = []
    for session_clone in session_clones:
        if session_clone.name == owning_name and worktree is not None:
            source_root = clone_root_of(worktree)
        else:
            source_root = session_clone.path
        contributions.append(discover_contribution_in(session_clone.name, source_root))
    manifest = Manifest(contributions=tuple(contributions))
    raise_if_manifest_has_collisions(manifest)
    return manifest
