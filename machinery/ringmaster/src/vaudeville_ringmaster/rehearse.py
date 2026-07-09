"""The Rehearse operation: build the Artifact and install it to a Rehearsal Installation
through its carried installer."""

from __future__ import annotations

import tempfile
from pathlib import Path

from vaudeville_ringmaster.build import build_artifact
from vaudeville_ringmaster.installer_activation import RunInstaller
from vaudeville_ringmaster.registry import Registry
from vaudeville_ringmaster.session_clone import require_each_session_clone_present_in
from vaudeville_ringmaster.survey import survey_manifest
from vaudeville_ringmaster.uv_operations import BuildWheel
from vaudeville_ringmaster.worktree import Worktree


def rehearse(
    registry: Registry,
    session_clones_dir: Path,
    worktree: Worktree,
    staged_root: Path,
    *,
    config_dir: Path,
    build_wheel: BuildWheel,
    run_installer: RunInstaller,
    host_home: Path,
) -> Path:
    clones = require_each_session_clone_present_in(registry, session_clones_dir)
    manifest = survey_manifest(registry, clones, worktree=worktree)
    with tempfile.TemporaryDirectory() as artifact_root:
        artifact = build_artifact(manifest, Path(artifact_root), build_wheel=build_wheel)
        run_installer(
            artifact_root=artifact.root,
            destination="staging",
            config_dir=config_dir,
            staged_root=staged_root,
            host_home=host_home,
        )
    return staged_root
