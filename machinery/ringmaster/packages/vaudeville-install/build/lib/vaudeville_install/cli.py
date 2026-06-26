"""The ``vaudeville-install`` entry point: the installer's composition root.

Activated from inside a built Artifact (``uvx --from <carried-wheel> vaudeville-install …``) on a
host that has only ``uv``, this reads the host environment once, builds the real uv and host-``vv``
capabilities, and runs the install operation for the chosen Destination. No operation below
resolves the environment itself; a Host install runs against the real host state (not a Staging
stand-in) because the Staging redirects are stripped here.
"""

from __future__ import annotations

import argparse
import os
from functools import partial
from pathlib import Path

from vaudeville_install.artifact import CREDENTIALS_FILENAME, Artifact
from vaudeville_install.destination import Host
from vaudeville_install.doc_tree import DocTreeContainsSymlink
from vaudeville_install.host_vv import (
    capturing_vv_runner,
    host_vv_environment,
    interactive_vv_runner,
)
from vaudeville_install.host_wiring import (
    HostWiringError,
    binary_path,
    locate_youtrack,
    urllib_reach,
    verify_host_wiring,
    workmux_version_returncode,
)
from vaudeville_install.integrity import HostScaffoldIntegrityError
from vaudeville_install.operations import install_to_host, install_to_staging
from vaudeville_install.placement import MalformedArtifact, missing_artifact_components
from vaudeville_install.prime_foundations import FoundationsNotPrimed
from vaudeville_install.uv_operations import install_facade_with_uv

_DEPLOY_FAILURES = (
    DocTreeContainsSymlink,
    FoundationsNotPrimed,
    HostScaffoldIntegrityError,
    HostWiringError,
    MalformedArtifact,
)


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)
    artifact = Artifact(root=args.artifact)
    try:
        missing = missing_artifact_components(artifact)
        if missing:
            raise MalformedArtifact(artifact.root, missing)
        if args.destination == "host":
            _install_to_host(artifact, config_dir=args.config_dir)
        else:
            install_to_staging(
                artifact,
                root=args.root,
                host_home=args.host_home,
                config_dir=args.config_dir,
                install_facade=install_facade_with_uv,
            )
    except _DEPLOY_FAILURES as failure:
        raise SystemExit(str(failure)) from failure


def _install_to_host(artifact: Artifact, *, config_dir: Path) -> None:
    home = Path.home()
    vv_path = Host(home=home).layout.bin_dir / "vv"
    host_env = host_vv_environment(os.environ)
    api_base, api_key = locate_youtrack(os.environ, config_dir / CREDENTIALS_FILENAME)
    verify_wiring = partial(
        verify_host_wiring,
        api_base=api_base,
        api_key=api_key,
        reach=urllib_reach,
        binary_path=binary_path,
        run=workmux_version_returncode,
    )
    install_to_host(
        artifact,
        home=home,
        config_dir=config_dir,
        install_facade=install_facade_with_uv,
        probe_vv=capturing_vv_runner(vv_path, host_env),
        prime_vv=interactive_vv_runner(vv_path, host_env),
        verify_wiring=verify_wiring,
    )


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="vaudeville-install",
        description="Install a built Vaudeville Artifact at a Destination.",
    )
    parser.add_argument(
        "--artifact",
        type=Path,
        required=True,
        help="path to the built Artifact root to install from",
    )
    parser.add_argument("--destination", choices=("host", "staging"), required=True)
    parser.add_argument(
        "--config-dir",
        type=Path,
        default=Path.home() / "vaudeville-config",
        dest="config_dir",
        help="the tenant's config dir (project map, credentials, project-docs, auto-mode rules)",
    )
    parser.add_argument(
        "--root", type=Path, help="the Staging root to build (required for --destination staging)"
    )
    parser.add_argument("--host-home", type=Path, default=Path.home(), dest="host_home")
    args = parser.parse_args(argv)
    if args.destination == "staging" and args.root is None:
        parser.error("--root is required for --destination staging")
    return args
