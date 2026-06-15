"""The installer's operations: place a built Artifact at a Destination, and — for the Host —
leave it deployable-from.

Pure over the injected uv and host-``vv`` capabilities (the composition root in ``cli`` supplies
the real ones), so a test drives the whole flow with fakes. The Host install verifies the command
surface and host wiring before priming the Foundations and verifying them; Staging is placement
only, because its verification is the smoke against the Staged Scaffold rather than these host
checks.
"""

from __future__ import annotations

from pathlib import Path

from vaudeville_install.artifact import Artifact
from vaudeville_install.destination import Host, Staging
from vaudeville_install.host_vv import RunVv
from vaudeville_install.host_wiring import VerifyWiring
from vaudeville_install.integrity import verify_command_surface, verify_foundations
from vaudeville_install.placement import install_artifact
from vaudeville_install.prime_foundations import prime_foundations
from vaudeville_install.uv_operations import InstallFacade


def install_to_host(
    artifact: Artifact,
    *,
    home: Path,
    config_dir: Path,
    install_facade: InstallFacade,
    probe_vv: RunVv,
    prime_vv: RunVv,
    verify_wiring: VerifyWiring,
) -> None:
    install_artifact(
        artifact, Host(home=home), config_dir=config_dir, install_facade=install_facade
    )
    # The surface probe and the wiring check gate priming (priming runs `vv prime`, which a broken
    # `vv` or an unwired host would trip); the Foundation probe then confirms priming took.
    verify_command_surface(probe_vv)
    verify_wiring()
    prime_foundations(prime_vv)
    verify_foundations(probe_vv)


def install_to_staging(
    artifact: Artifact,
    *,
    root: Path,
    host_home: Path,
    config_dir: Path,
    install_facade: InstallFacade,
) -> None:
    install_artifact(
        artifact,
        Staging(root=root, host_home=host_home),
        config_dir=config_dir,
        install_facade=install_facade,
    )
