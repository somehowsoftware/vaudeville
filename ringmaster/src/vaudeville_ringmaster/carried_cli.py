"""Carry the integrated command line into the Artifact: Facade, Contributor wheels, installer."""

from __future__ import annotations

import tempfile
from pathlib import Path

import vaudeville_ringmaster
from vaudeville_ringmaster.carried_contribution import contribution_carries_a_wheel
from vaudeville_ringmaster.facade import (
    facade_modules_of,
    federation_distributions_of,
    operator_modules_of,
)
from vaudeville_ringmaster.facade_distribution import render_facade_distribution
from vaudeville_ringmaster.manifest import Manifest
from vaudeville_ringmaster.uv_operations import BuildWheel

INTEGRATOR_NAME = "vaudeville-ringmaster"
_CARRIED_INSTALLER_SOURCE = Path("packages") / "vaudeville-install"


def carry_integrated_cli_into(manifest: Manifest, into: Path, build_wheel: BuildWheel) -> None:
    into.mkdir(parents=True, exist_ok=True)
    for contribution in manifest.contributions:
        if contribution_carries_a_wheel(contribution):
            build_wheel(contribution.source_root, into)
    with tempfile.TemporaryDirectory() as facade_source:
        # Stamp the Facade with the version of the ringmaster that built it, so a deployed `vv`
        # is traceable to its build rather than frozen at a literal every build serves alike.
        render_facade_distribution(
            Path(facade_source),
            facade_modules=facade_modules_of(manifest),
            operator_modules=operator_modules_of(manifest),
            distributions=federation_distributions_of(manifest),
            version=vaudeville_ringmaster.__version__,
        )
        build_wheel(Path(facade_source), into)
    build_wheel(_carried_installer_source_in(manifest), into)


def _carried_installer_source_in(manifest: Manifest) -> Path:
    # The installer is the integrator's workspace sibling; build it from the integrator's own source
    # in the Manifest (which Rehearse substitutes with the worktree under rehearsal) so the carried
    # installer tracks the integrator it ships beside.
    integrator = next((c for c in manifest.contributions if c.name == INTEGRATOR_NAME), None)
    if integrator is None:
        raise IntegratorContributionMissing(INTEGRATOR_NAME)
    return integrator.source_root / _CARRIED_INSTALLER_SOURCE


class IntegratorContributionMissing(RuntimeError):
    def __init__(self, name: str) -> None:
        super().__init__(f"Manifest has no {name!r} contribution to build the installer from.")
