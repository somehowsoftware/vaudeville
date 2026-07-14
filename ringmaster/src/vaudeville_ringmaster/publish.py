"""The Publish operation: release a versioned Artifact and its readable Exposition to the Home."""

from __future__ import annotations

import tempfile
from collections.abc import Callable
from datetime import date
from pathlib import Path

from vaudeville_ringmaster.build import build_artifact
from vaudeville_ringmaster.exposition import render_exposition
from vaudeville_ringmaster.exposition_commit import CommitExposition
from vaudeville_ringmaster.github_release import CreateRelease
from vaudeville_ringmaster.pinned_set import pin_session_clones
from vaudeville_ringmaster.pristine_guard import enforce_pristine_guard_on
from vaudeville_ringmaster.provenance import provenance_of, render_provenance_toml
from vaudeville_ringmaster.published_artifact import published_artifact_for
from vaudeville_ringmaster.published_home import PUBLISHED_HOME
from vaudeville_ringmaster.registry import Registry
from vaudeville_ringmaster.release import Release
from vaudeville_ringmaster.release_name import ReleaseName, next_release_name
from vaudeville_ringmaster.session_clone import SessionClone, require_each_session_clone_present_in
from vaudeville_ringmaster.survey import survey_manifest
from vaudeville_ringmaster.uv_operations import BuildWheel


def publish(
    registry: Registry,
    session_clones_dir: Path,
    *,
    doctrine_contributor: str | None,
    today: date,
    list_tags: Callable[[], list[str]],
    build_wheel: BuildWheel,
    create_release: CreateRelease,
    commit_exposition: CommitExposition,
    enforce_current_builder: Callable[[Path], None],
) -> None:
    clones = require_each_session_clone_present_in(registry, session_clones_dir)
    # A Release and the Exposition beside it, like a Host Installation, carry only reviewed, merged
    # code, so refuse a Rehearsal-fixed Session Clone.
    enforce_pristine_guard_on(clones)
    # Refuse a stale Builder before any work: Publish fans the Release out to every tenant with no
    # self-update behind it, so a host tool older than the vaudeville-ringmaster it builds from must
    # not ship its outdated install code as a Release.
    enforce_current_builder(session_clones_dir)
    # Name the Release before the expensive build, so a stuck tag-listing fails before the build.
    release_name = next_release_name(today, list_tags())
    manifest = survey_manifest(registry, clones)
    pinned_set = pin_session_clones(registry, clones)
    provenance = provenance_of(pinned_set, manifest)
    # The Exposition is committed on the Published Home first, and the Release is then pinned to
    # that exact commit, so the install Artifact and its readable companion share one Release Name
    # and one commit even if another push reaches the default branch in between. A failure after the
    # commit leaves an untagged commit the next Publish supersedes; the Release Name, computed from
    # tags, is not burned.
    landed_commit = _publish_exposition(
        clones,
        doctrine_contributor,
        release_name,
        render_provenance_toml(provenance),
        commit_exposition,
    )
    # Compose the Release only now: the commit its tag points at does not exist until the
    # Exposition is written.
    release = Release(name=release_name, provenance=provenance, landed_commit=landed_commit)
    with tempfile.TemporaryDirectory() as artifact_root:
        artifact = build_artifact(manifest, Path(artifact_root), build_wheel=build_wheel)
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
    clones: list[SessionClone],
    doctrine_contributor: str | None,
    release_name: ReleaseName,
    provenance_text: str,
    commit_exposition: CommitExposition,
) -> str:
    with tempfile.TemporaryDirectory() as exposition_root:
        exposition = render_exposition(
            clones,
            Path(exposition_root),
            doctrine_contributor=doctrine_contributor,
            provenance_text=provenance_text,
        )
        return commit_exposition(
            repository=PUBLISHED_HOME, version=release_name.value, exposition=exposition.root
        )
