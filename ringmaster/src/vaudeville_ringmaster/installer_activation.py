# The integrator's runner for the carried installer. Deploy/Rehearse hand the built Artifact to the
# same `uvx --from <carried-wheel> vaudeville-install` path a tenant runs, so the two cannot drift;
# the argv, wheel, and failures live in `vaudeville_install.installer_activation`. Only the runner
# differs: this one inherits the terminal because priming is interactive and may prompt, so a
# non-zero exit surfaces without capturing the diagnostic the operator has already seen.

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Protocol

from vaudeville_install.installer_activation import (
    InstallerFailed,
    InstallerNotCarried,
    carried_installer_wheel_in,
    installer_activation_argv,
)

__all__ = [
    "InstallerFailed",
    "InstallerNotCarried",
    "RunInstaller",
    "activate_installer_with_uvx",
    "carried_installer_wheel_in",
    "installer_activation_argv",
]


class RunInstaller(Protocol):
    def __call__(
        self,
        *,
        artifact_root: Path,
        destination: str,
        config_dir: Path,
        staged_root: Path | None = None,
        host_home: Path | None = None,
    ) -> None: ...


def activate_installer_with_uvx(
    *,
    artifact_root: Path,
    destination: str,
    config_dir: Path,
    staged_root: Path | None = None,
    host_home: Path | None = None,
) -> None:
    argv = installer_activation_argv(
        carried_installer_wheel_in(artifact_root),
        artifact_root=artifact_root,
        destination=destination,
        config_dir=config_dir,
        staged_root=staged_root,
        host_home=host_home,
    )
    # Inherit the terminal: the installer's priming is interactive and may prompt. Capturing it
    # would hide those prompts behind a pipe; on failure the operator has already seen the
    # installer's own diagnostic, so only the exit status is surfaced here.
    completed = subprocess.run(argv, check=False)
    if completed.returncode != 0:
        raise InstallerFailed(destination, f"exit {completed.returncode}; see its diagnostic above")
