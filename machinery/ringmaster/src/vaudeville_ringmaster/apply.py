"""The Apply operation: build the Artifact and hand it to its own carried installer for the Host."""

from __future__ import annotations

import tempfile
from pathlib import Path

from vaudeville_ringmaster.assemble import assemble_apply_plan
from vaudeville_ringmaster.build import build_artifact
from vaudeville_ringmaster.installer_activation import RunInstaller
from vaudeville_ringmaster.pristine_guard import enforce_pristine_guard_on
from vaudeville_ringmaster.registry import Registry
from vaudeville_ringmaster.session_clone import require_each_session_clone_present_in
from vaudeville_ringmaster.uv_operations import BuildWheel


def apply(
    registry: Registry,
    session_clones_dir: Path,
    *,
    config_dir: Path,
    build_wheel: BuildWheel,
    run_installer: RunInstaller,
) -> None:
    clones = require_each_session_clone_present_in(registry, session_clones_dir)
    enforce_pristine_guard_on(clones)
    plan = assemble_apply_plan(registry, clones)
    with tempfile.TemporaryDirectory() as artifact_root:
        artifact = build_artifact(plan, Path(artifact_root), build_wheel=build_wheel)
        # Hand the built Artifact to its own carried installer — the same self-install path a tenant
        # runs — within the temp dir's lifetime, since the installer reads the Artifact by path. The
        # installer owns placement and the host integrity/wiring/prime orchestration.
        run_installer(artifact_root=artifact.root, destination="host", config_dir=config_dir)
