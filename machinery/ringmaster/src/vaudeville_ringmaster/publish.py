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
from vaudeville_ringmaster.pinned_set import pin_session_clones
from vaudeville_ringmaster.pristine_guard import enforce_pristine_guard_on
from vaudeville_ringmaster.provenance import provenance_of, render_provenance_manifest
from vaudeville_ringmaster.published_artifact import published_artifact_for
from vaudeville_ringmaster.published_home import PUBLISHED_HOME
from vaudeville_ringmaster.registry import Registry
from vaudeville_ringmaster.release import Release
from vaudeville_ringmaster.release_name import ReleaseName, next_release_name
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
    # A Release and the Exposition beside it, like a Host Scaffold, carry only reviewed, merged
    # code, so refuse a Hot-fixed Session Clone.
    enforce_pristine_guard_on(clones)
    # Name the Release before the expensive build, so a stuck tag-listing fails before the build.
    release_name = next_release_name(today, list_tags())
    plan = assemble_apply_plan(registry, clones)
    pinned_set = pin_session_clones(registry, clones)
    provenance = provenance_of(pinned_set, plan)
    # The Exposition is committed on the Published Home first, and the Release is then pinned to
    # that exact commit, so the install Artifact and its readable companion share one Release Name
    # and one commit even if another push reaches the default branch in between. A failure after the
    # commit leaves an untagged commit the next Publish supersedes; the Release Name, computed from
    # tags, is not burned.
    landed_commit = _publish_exposition(
        registry,
        clones,
        layout,
        release_name,
        render_provenance_manifest(provenance),
        commit_exposition,
    )
    # Compose the Release only now: the commit its tag points at does not exist until the
    # Exposition is written.
    release = Release(name=release_name, provenance=provenance, landed_commit=landed_commit)
    with tempfile.TemporaryDirectory() as artifact_root:
        artifact = build_artifact(plan, Path(artifact_root), build_wheel=build_wheel)
        with tempfile.TemporaryDirectory() as packaging_dir:
            asset = published_artifact_for(
                artifact, Path(packaging_dir) / release.name.asset_filename
            )
            create_release(
                repository=PUBLISHED_HOME,
                version=release.name.value,
                asset=asset,
                target=release.landed_commit,
            )


def _publish_exposition(
    registry: Registry,
    clones: list[SessionClone],
    layout: ExpositionLayout,
    release_name: ReleaseName,
    provenance_text: str,
    commit_exposition: CommitExposition,
) -> str:
    with tempfile.TemporaryDirectory() as exposition_root:
        exposition = render_exposition(
            layout, registry, clones, Path(exposition_root), provenance_text=provenance_text
        )
        return commit_exposition(
            repository=PUBLISHED_HOME, version=release_name.value, exposition=exposition.root
        )
