"""Carry the integrated command line into the Artifact: Facade, Contributor wheels, installer."""

from __future__ import annotations

import tempfile
from pathlib import Path

import vaudeville_install

import vaudeville_ringmaster
from vaudeville_ringmaster.apply_plan import ApplyPlan
from vaudeville_ringmaster.carried_contribution import contribution_carries_a_wheel
from vaudeville_ringmaster.facade import (
    facade_modules_of,
    federation_distributions_of,
    operator_modules_of,
)
from vaudeville_ringmaster.facade_distribution import render_facade_distribution
from vaudeville_ringmaster.uv_operations import BuildWheel


def carry_integrated_cli_into(plan: ApplyPlan, into: Path, build_wheel: BuildWheel) -> None:
    into.mkdir(parents=True, exist_ok=True)
    for contribution in plan.contributions:
        if contribution_carries_a_wheel(contribution):
            build_wheel(contribution.source_root, into)
    with tempfile.TemporaryDirectory() as facade_source:
        # Stamp the Facade with the version of the ringmaster that built it, so a deployed `vv`
        # is traceable to its build rather than frozen at a literal every build serves alike.
        render_facade_distribution(
            Path(facade_source),
            facade_modules=facade_modules_of(plan),
            operator_modules=operator_modules_of(plan),
            distributions=federation_distributions_of(plan),
            version=vaudeville_ringmaster.__version__,
        )
        build_wheel(Path(facade_source), into)
    # The installer rides inside the Artifact so a tenant can activate it with uv alone. Build
    # runs from the integrator's source, where the installer is a workspace sibling, so its wheel
    # is built from that source here rather than fetched.
    build_wheel(_installer_project_root(), into)


def _installer_project_root() -> Path:
    # vaudeville_install is installed from packages/vaudeville-install/src/vaudeville_install; its
    # project root (the directory holding pyproject.toml) is two levels above the package directory.
    return Path(vaudeville_install.__file__).resolve().parents[2]
