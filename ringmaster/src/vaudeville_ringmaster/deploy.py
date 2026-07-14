"""The Deploy operation: build the Artifact and hand it to its carried installer for the Host."""

from __future__ import annotations

import tempfile
from collections.abc import Callable
from pathlib import Path

from vaudeville_ringmaster.build import build_artifact
from vaudeville_ringmaster.installer_activation import RunInstaller
from vaudeville_ringmaster.pristine_guard import enforce_pristine_guard_on
from vaudeville_ringmaster.registry import Registry
from vaudeville_ringmaster.session_clone import require_each_session_clone_present_in
from vaudeville_ringmaster.survey import survey_manifest
from vaudeville_ringmaster.uv_operations import BuildWheel


def deploy(
    registry: Registry,
    session_clones_dir: Path,
    *,
    config_dir: Path,
    build_wheel: BuildWheel,
    run_installer: RunInstaller,
    self_update: Callable[[Path], None],
    enforce_current_builder: Callable[[Path], None],
) -> None:
    clones = require_each_session_clone_present_in(registry, session_clones_dir)
    enforce_pristine_guard_on(clones)
    # Refuse before Build if this ringmaster is older than the vaudeville-ringmaster it would build
    # from: a stale host tool would deploy its own outdated install code, and self-update alone
    # cannot catch that, since it runs only after the deploy it should have prevented.
    enforce_current_builder(session_clones_dir)
    manifest = survey_manifest(registry, clones)
    with tempfile.TemporaryDirectory() as artifact_root:
        artifact = build_artifact(manifest, Path(artifact_root), build_wheel=build_wheel)
        # Hand the built Artifact to its own carried installer (the same self-install path a tenant
        # runs) within the temp dir's lifetime, since the installer reads the Artifact by path. The
        # installer owns placement and the host Commissioning.
        run_installer(artifact_root=artifact.root, destination="host", config_dir=config_dir)
    # Ringmaster isn't part of the Host Installation the installer places, so the host's ringmaster
    # would otherwise stay pinned while the code it deploys advances. Self-update it from its own
    # Session Clone (already Pristine-guarded above) after the install, so a failed deploy never
    # moves it.
    self_update(session_clones_dir / "vaudeville-ringmaster")
