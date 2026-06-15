"""The Publish operation: release a versioned Artifact and its readable Exposition to the Home."""

from __future__ import annotations

import tempfile
from collections.abc import Callable
from datetime import date
from pathlib import Path

from vaudeville_ringmaster.assemble import assemble_apply_plan
from vaudeville_ringmaster.build import build_artifact
from vaudeville_ringmaster.exposition import ExpositionLayout, render_exposition
from vaudeville_ringmaster.exposition_commit import CommitExposition
from vaudeville_ringmaster.github_release import CreateRelease
from vaudeville_ringmaster.pristine_guard import enforce_pristine_guard_on
from vaudeville_ringmaster.provenance import (
    builder_provenance,
    provenance_for,
    render_provenance_manifest,
)
from vaudeville_ringmaster.published_version import (
    PUBLISHED_HOME,
    next_published_version,
    published_version_asset_for,
)
from vaudeville_ringmaster.registry import Registry
from vaudeville_ringmaster.session_clone import SessionClone, require_each_session_clone_present_in
from vaudeville_ringmaster.uv_operations import BuildWheel


def publish(
    registry: Registry,
    session_clones_dir: Path,
    *,
    layout: ExpositionLayout,
    today: date,
    list_tags: Callable[[], list[str]],
    build_wheel: BuildWheel,
    create_release: CreateRelease,
    commit_exposition: CommitExposition,
) -> None:
    clones = require_each_session_clone_present_in(registry, session_clones_dir)
    # A Published Version and the Exposition beside it, like a Host Scaffold, carry only reviewed,
    # merged code — so refuse a Hot-fixed Session Clone.
    enforce_pristine_guard_on(clones)
    # Resolve the version before the expensive build, so a stuck tag-listing fails before the build.
    version = next_published_version(today, list_tags())
    plan = assemble_apply_plan(registry, clones)
    # Computed from the Plan — the same source Build carries from — not the raw Session Clones,
    # which would record the integrator (the Builder, not a payload) as if it shipped.
    provenance_text = render_provenance_manifest(
        provenance_for(registry, plan), builder_provenance()
    )
    # The Exposition commit lands on the Published Home first, and the Release is then pinned to
    # that exact commit — so the install Artifact and its readable companion share one version and
    # one commit even if another push reaches the default branch in between. A failure after the
    # commit leaves an untagged commit the next Publish supersedes; the version, computed from tags,
    # is not burned.
    exposition_commit_sha = _publish_exposition(
        registry, clones, layout, version, provenance_text, commit_exposition
    )
    with tempfile.TemporaryDirectory() as artifact_root:
        artifact = build_artifact(plan, Path(artifact_root), build_wheel=build_wheel)
        with tempfile.TemporaryDirectory() as packaging_dir:
            asset = published_version_asset_for(
                artifact, Path(packaging_dir) / f"vaudeville-{version}.tar.gz"
            )
            create_release(
                repository=PUBLISHED_HOME,
                version=version,
                asset=asset,
                target=exposition_commit_sha,
            )


def _publish_exposition(
    registry: Registry,
    clones: list[SessionClone],
    layout: ExpositionLayout,
    version: str,
    provenance_text: str,
    commit_exposition: CommitExposition,
) -> str:
    with tempfile.TemporaryDirectory() as exposition_root:
        exposition = render_exposition(
            layout, registry, clones, Path(exposition_root), provenance_text=provenance_text
        )
        return commit_exposition(
            repository=PUBLISHED_HOME, version=version, exposition=exposition.root
        )
