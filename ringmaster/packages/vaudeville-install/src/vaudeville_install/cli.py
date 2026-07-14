from __future__ import annotations

import argparse
import os
from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
from pathlib import Path

from vaudeville_install.artifact import CREDENTIALS_FILENAME, Artifact
from vaudeville_install.artifact_completeness import MalformedArtifact, missing_artifact_components
from vaudeville_install.child_process import Spec, run
from vaudeville_install.commissioning import CommissioningError
from vaudeville_install.destination import Host
from vaudeville_install.doc_tree import DocTreeContainsSymlink
from vaudeville_install.host_vv import (
    build_vv_spec,
    capturing_vv_runner,
    host_vv_environment,
    streaming_vv_runner,
)
from vaudeville_install.host_wiring import (
    HostWiringError,
    binary_path,
    build_ls_remote_spec,
    build_workmux_spec,
    interpret_ls_remote,
    interpret_workmux,
    locate_youtrack,
    verify_host_wiring,
    youtrack_authenticated,
)
from vaudeville_install.installer_activation import build_host_activation_spec
from vaudeville_install.newest_artifact import build_artifact_download_spec
from vaudeville_install.operations import install_to_host, install_to_rehearsal
from vaudeville_install.prime_foundations import FoundationsNotPrimed
from vaudeville_install.settings import SettingsFileUnreadable
from vaudeville_install.tenant_config import TenantConfigUnreadable, project_remotes
from vaudeville_install.tenant_hooks import HookScriptCollision
from vaudeville_install.uv_operations import (
    PUBLIC_INDEX,
    ComposedCLIInstallFailed,
    InstallComposedCLI,
    build_uv_install_spec,
    carried_distribution_names_in,
    interpret_uv_install,
)

_DEPLOY_FAILURES = (
    ComposedCLIInstallFailed,
    DocTreeContainsSymlink,
    FoundationsNotPrimed,
    CommissioningError,
    HostWiringError,
    HookScriptCollision,
    MalformedArtifact,
    SettingsFileUnreadable,
    TenantConfigUnreadable,
)

# A `vv` probe (surface, foundations-verify) is quick; a generous ceiling still catches a hang.
# `vv prime` drives several `claude` turns per Component, so its ceiling is far larger — the timeout
# exists to break a hang, never to bound a valid prime. The read-only probes (git ls-remote, workmux
# --version) are quick; uv's install can download and build, so its ceiling is generous too.
_PROBE_TIMEOUT_SECONDS = 300.0
_PRIME_TIMEOUT_SECONDS = 3600.0
_LS_REMOTE_TIMEOUT_SECONDS = 30.0
_WORKMUX_TIMEOUT_SECONDS = 30.0
_UV_TIMEOUT_SECONDS = 1800.0


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
            install_to_rehearsal(
                artifact,
                root=args.root,
                host_home=args.host_home,
                config_dir=args.config_dir,
                install_composed_cli=_uv_installer(),
            )
    except _DEPLOY_FAILURES as failure:
        raise SystemExit(str(failure)) from failure


def _install_to_host(artifact: Artifact, *, config_dir: Path) -> None:
    home = Path.home()
    vv_path = Host(home=home).layout.bin_dir / "vv"
    host_env = host_vv_environment(os.environ)
    api_base, api_key = locate_youtrack(os.environ, config_dir / CREDENTIALS_FILENAME)

    def read_remote(remote: str) -> str | None:
        return interpret_ls_remote(
            run(build_ls_remote_spec(remote, os.environ, _LS_REMOTE_TIMEOUT_SECONDS))
        )

    def workmux_runs() -> str | None:
        return interpret_workmux(run(build_workmux_spec(os.environ, _WORKMUX_TIMEOUT_SECONDS)))

    verify_wiring = partial(
        verify_host_wiring,
        api_base=api_base,
        api_key=api_key,
        remotes=project_remotes(config_dir),
        authenticate=youtrack_authenticated,
        read_remote=read_remote,
        binary_path=binary_path,
        workmux_runs=workmux_runs,
    )
    install_to_host(
        artifact,
        home=home,
        config_dir=config_dir,
        install_composed_cli=_uv_installer(),
        probe_vv=capturing_vv_runner(run, vv_path, host_env, _PROBE_TIMEOUT_SECONDS),
        prime_vv=streaming_vv_runner(run, vv_path, host_env, _PRIME_TIMEOUT_SECONDS),
        verify_wiring=verify_wiring,
    )


def _uv_installer() -> InstallComposedCLI:
    def install_composed_cli(
        *, distribution: str, find_links: Path, index_url: str, bin_dir: Path, tool_dir: Path
    ) -> None:
        spec = build_uv_install_spec(
            distribution=distribution,
            find_links=find_links,
            index_url=index_url,
            bin_dir=bin_dir,
            tool_dir=tool_dir,
            refresh_packages=carried_distribution_names_in(find_links),
            base_env=os.environ,
            timeout=_UV_TIMEOUT_SECONDS,
        )
        interpret_uv_install(distribution, run(spec))

    return install_composed_cli


@dataclass(frozen=True)
class Boundary:
    name: str
    sample_spec: Callable[[], Spec]


# A representative Spec for every place the install shells out, in one walkable value: a fitness
# test asserts each builds a bounded Spec, and the child-process import test backstops that no
# boundary escapes this set. The git ls-remote sample carries a token in its URL on purpose — the
# Spec's argv legitimately holds it (git needs it), while `interpret_ls_remote` strips it from any
# operator-facing message.
INSTALL_BOUNDARIES: tuple[Boundary, ...] = (
    Boundary(
        "vv prime",
        lambda: build_vv_spec(
            Path("/vv"), {}, ("prime",), capture_stdout=False, timeout=_PRIME_TIMEOUT_SECONDS
        ),
    ),
    Boundary(
        "vv probe",
        lambda: build_vv_spec(
            Path("/vv"), {}, ("--surface",), capture_stdout=True, timeout=_PROBE_TIMEOUT_SECONDS
        ),
    ),
    Boundary(
        "git ls-remote",
        lambda: build_ls_remote_spec(
            "https://user:token@example.invalid/tenant/repo.git", {}, _LS_REMOTE_TIMEOUT_SECONDS
        ),
    ),
    Boundary("workmux --version", lambda: build_workmux_spec({}, _WORKMUX_TIMEOUT_SECONDS)),
    Boundary(
        "uv tool install",
        lambda: build_uv_install_spec(
            distribution="vaudeville-vv",
            find_links=Path("/links"),
            index_url=PUBLIC_INDEX,
            bin_dir=Path("/bin"),
            tool_dir=Path("/tool"),
            refresh_packages=(),
            base_env={},
            timeout=_UV_TIMEOUT_SECONDS,
        ),
    ),
    Boundary(
        "gh release download",
        lambda: build_artifact_download_spec(
            Path("/download"), env={}, timeout=_UV_TIMEOUT_SECONDS
        ),
    ),
    Boundary(
        "carried installer activation",
        lambda: build_host_activation_spec(
            Path("/art/cli/vaudeville_install-0.0-py3-none-any.whl"),
            artifact_root=Path("/art"),
            config_dir=Path("/cfg"),
            env={},
            timeout=_PRIME_TIMEOUT_SECONDS,
        ),
    ),
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
        "--root", type=Path, help="the Rehearsal root to build (required for --destination staging)"
    )
    parser.add_argument("--host-home", type=Path, default=Path.home(), dest="host_home")
    args = parser.parse_args(argv)
    if args.destination == "staging" and args.root is None:
        parser.error("--root is required for --destination staging")
    return args
