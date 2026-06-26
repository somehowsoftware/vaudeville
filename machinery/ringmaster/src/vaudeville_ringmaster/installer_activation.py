"""Activate a built Artifact's carried installer: the integrator's deploy is the tenant's deploy.

apply and stage build the Artifact, then hand it to its own carried installer rather than placing
it in-process, so every deploy walks the exact ``uvx --from <carried-wheel> vaudeville-install``
path a tenant runs, and the two cannot drift. The installer inherits the terminal (its priming is
interactive and may prompt), so a non-zero exit is surfaced as a failure here without capturing the
diagnostic the operator has already seen.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Protocol

INSTALLER_BINARY = "vaudeville-install"
_INSTALLER_WHEEL_GLOB = "vaudeville_install-*.whl"


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


def installer_activation_argv(
    installer_wheel: Path,
    *,
    artifact_root: Path,
    destination: str,
    config_dir: Path,
    staged_root: Path | None,
    host_home: Path | None,
) -> list[str]:
    argv = [
        "uvx",
        "--python",
        "3.14",
        "--from",
        str(installer_wheel),
        INSTALLER_BINARY,
        "--artifact",
        str(artifact_root),
        "--destination",
        destination,
        "--config-dir",
        str(config_dir),
    ]
    if staged_root is not None:
        argv += ["--root", str(staged_root)]
    if host_home is not None:
        argv += ["--host-home", str(host_home)]
    return argv


def carried_installer_wheel_in(artifact_root: Path) -> Path:
    wheels = sorted((artifact_root / "cli").glob(_INSTALLER_WHEEL_GLOB))
    if not wheels:
        raise InstallerNotCarried(artifact_root)
    return wheels[-1]


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
        raise InstallerFailed(destination, completed.returncode)


class InstallerNotCarried(RuntimeError):
    def __init__(self, artifact_root: Path) -> None:
        super().__init__(artifact_root)
        self.artifact_root = artifact_root

    def __str__(self) -> str:
        return (
            f"No carried installer wheel ({_INSTALLER_WHEEL_GLOB}) under "
            f"{self.artifact_root / 'cli'}; Build did not carry the installer into the Artifact."
        )


class InstallerFailed(RuntimeError):
    def __init__(self, destination: str, returncode: int) -> None:
        super().__init__(destination, returncode)
        self.destination = destination
        self.returncode = returncode

    def __str__(self) -> str:
        return (
            f"The carried installer failed installing to the {self.destination} Destination "
            f"(exit {self.returncode}); see its diagnostic above."
        )
