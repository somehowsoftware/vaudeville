# Two callers build this one activation argv and must not drift: the integrator's Deploy/Rehearse
# and the tenant's `vaudeville update`. Keeping the invocation here — a fact about the installer,
# whose binary name is this package's own console script — is what makes "the tenant's update
# installs exactly as a first install did" true by construction. Only the runner differs per caller.

from __future__ import annotations

from pathlib import Path

from vaudeville_install.child_process import Completed, LaunchFailed, Outcome, Spec, TimedOut

INSTALLER_BINARY = "vaudeville-install"
_INSTALLER_WHEEL_GLOB = "vaudeville_install-*.whl"


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


def build_host_activation_spec(
    installer_wheel: Path,
    *,
    artifact_root: Path,
    config_dir: Path,
    env: dict[str, str],
    timeout: float,
) -> Spec:
    # The tenant's ``vaudeville update`` activation: always the Host Destination, never the
    # Rehearsal carve-out, so no ``--root``/``--host-home``. Funnelled through the child-process
    # boundary (``capture_stdout=False`` so the installer's own placement/priming output reaches the
    # operator live, exactly as a first install does), unlike the integrator's terminal-inheriting
    # runner. Safe to run non-interactively: the carried installer's machine path takes no prompt.
    return Spec(
        argv=installer_activation_argv(
            installer_wheel,
            artifact_root=artifact_root,
            destination="host",
            config_dir=config_dir,
            staged_root=None,
            host_home=None,
        ),
        env=env,
        timeout=timeout,
        capture_stdout=False,
    )


def interpret_host_activation(outcome: Outcome) -> None:
    if isinstance(outcome, Completed) and outcome.returncode == 0:
        return
    raise InstallerFailed("host", _why_activation_failed(outcome))


def _why_activation_failed(outcome: Outcome) -> str:
    match outcome:
        case Completed(returncode=returncode, stderr=stderr):
            # stderr is captured even with stdout inherited; the installer's own placement/priming
            # diagnostic has already streamed to the operator, so this is the terse tail.
            detail = stderr.strip()
            base = f"the carried installer exited {returncode}"
            return f"{base}: {detail}" if detail else f"{base}; see its diagnostic above"
        case TimedOut(timeout=timeout):
            return f"the carried installer did not finish within {timeout:g}s and was terminated"
        case LaunchFailed(reason=reason):
            return reason


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
    def __init__(self, destination: str, cause: str) -> None:
        super().__init__(destination, cause)
        self.destination = destination
        self.cause = cause

    def __str__(self) -> str:
        return (
            f"The carried installer failed installing to the {self.destination} Destination.\n"
            f"{self.cause}"
        )
