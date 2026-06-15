"""The Stage operation: build the Artifact and stage it through its carried installer."""

from __future__ import annotations

import tempfile
from pathlib import Path

from vaudeville_ringmaster.assemble import assemble_apply_plan
from vaudeville_ringmaster.build import build_artifact
from vaudeville_ringmaster.installer_activation import RunInstaller
from vaudeville_ringmaster.registry import Registry
from vaudeville_ringmaster.session_clone import require_each_session_clone_present_in
from vaudeville_ringmaster.uv_operations import BuildWheel
from vaudeville_ringmaster.worktree import Worktree


def stage(
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
    plan = assemble_apply_plan(registry, clones, worktree=worktree)
    with tempfile.TemporaryDirectory() as artifact_root:
        artifact = build_artifact(plan, Path(artifact_root), build_wheel=build_wheel)
        run_installer(
            artifact_root=artifact.root,
            destination="staging",
            config_dir=config_dir,
            staged_root=staged_root,
            host_home=host_home,
        )
    return staged_root
