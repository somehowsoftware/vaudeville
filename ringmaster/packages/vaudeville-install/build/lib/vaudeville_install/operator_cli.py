from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Annotated

import typer

from vaudeville_install.child_process import run
from vaudeville_install.config_origin import ConfigOriginUnrecorded, config_origin
from vaudeville_install.destination import Host
from vaudeville_install.host_vv import host_vv_environment, streaming_vv_runner
from vaudeville_install.installer_activation import (
    InstallerFailed,
    InstallerNotCarried,
    build_host_activation_spec,
    carried_installer_wheel_in,
    interpret_host_activation,
)
from vaudeville_install.newest_artifact import (
    ArtifactAssetNotUnique,
    ArtifactDownloadFailed,
    ArtifactUnpackFailed,
    build_artifact_download_spec,
    interpret_artifact_download,
    unpack_artifact,
)
from vaudeville_install.operator_refresh import run_refresh
from vaudeville_install.operator_update import Acquire, Activate, run_update
from vaudeville_install.prime_foundations import FoundationsNotPrimed
from vaudeville_install.tenant_config import TenantConfigUnreadable

# `vv prime` drives several `claude` turns per Component, so a reprime inherits the install's
# generous ceiling: the timeout breaks a hang, it does not bound a valid prime.
_PRIME_TIMEOUT_SECONDS = 3600.0
# An update's download gets a generous network ceiling: the timeout breaks a hang, not a fetch.
_DOWNLOAD_TIMEOUT_SECONDS = 1800.0
# The activation closes on the same Priming a prime runs, so it takes the prime ceiling.
_ACTIVATE_TIMEOUT_SECONDS = _PRIME_TIMEOUT_SECONDS

_REFRESH_FAILURES = (TenantConfigUnreadable, FoundationsNotPrimed, ConfigOriginUnrecorded)
_UPDATE_FAILURES = (
    ConfigOriginUnrecorded,
    ArtifactDownloadFailed,
    ArtifactAssetNotUnique,
    ArtifactUnpackFailed,
    InstallerNotCarried,
    InstallerFailed,
)

app = typer.Typer(add_completion=False)


@app.callback(
    help="Operate this host's Vaudeville installation: sync its config, or upgrade its framework."
)
def _operator() -> None:
    # A no-op root callback so Typer keeps `refresh`/`update` named subcommands rather than
    # collapsing a single-command app into the bare program the `vaudeville` Facade composes.
    return


@app.command(
    help="Sync the tenant's config into this host, repriming if the project docs or map changed."
)
def refresh(
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run", help="Show what a refresh would place and whether it would reprime."
        ),
    ] = False,
    yes: Annotated[
        bool,
        typer.Option(
            "-y", "--yes", help="Reprime without confirmation when the project docs or map changed."
        ),
    ] = False,
    config_dir: Annotated[
        Path | None,
        typer.Option(
            "--config-dir", help="The tenant's config dir (project map, credentials, docs)."
        ),
    ] = None,
) -> None:
    layout = Host(home=Path.home()).layout
    prime_vv = streaming_vv_runner(
        run, layout.bin_dir / "vv", host_vv_environment(os.environ), _PRIME_TIMEOUT_SECONDS
    )
    try:
        run_refresh(
            config_dir=config_origin(config_dir, layout),
            layout=layout,
            prime_vv=prime_vv,
            dry_run=dry_run,
            assume_yes=yes,
            confirm=typer.confirm,
            report=typer.echo,
        )
    except _REFRESH_FAILURES as failure:
        raise SystemExit(str(failure)) from failure


@app.command(
    help="Upgrade this host to the newest framework Release: pull the newest published Artifact and"
    " install it, exactly as a first install would. Usually best left to an agent — the download or"
    " a schema change can surprise, and an agent handles that better than a flag ever will."
)
def update(
    config_dir: Annotated[
        Path | None,
        typer.Option(
            "--config-dir", help="The tenant's config dir (project map, credentials, docs)."
        ),
    ] = None,
) -> None:
    try:
        config = config_origin(config_dir, Host(home=Path.home()).layout)
        # The scratch need not outlive the install: the installer copies the Artifact onto the host,
        # and nothing reads back into this workspace afterwards.
        with tempfile.TemporaryDirectory() as workspace:
            run_update(
                config_dir=config,
                acquire=_newest_artifact_acquirer(Path(workspace)),
                activate=_host_activator(config),
                report=typer.echo,
            )
    except _UPDATE_FAILURES as failure:
        raise SystemExit(str(failure)) from failure


def _newest_artifact_acquirer(workspace: Path) -> Acquire:
    # `gh` under the ambient environment: the tenant's own GitHub authentication reads the release,
    # never the integrator's elevated Published-Home token — the Install half never holds it.
    ambient_env = dict(os.environ)

    def acquire() -> Path:
        download_dir = workspace / "download"
        download_dir.mkdir()
        tarball = interpret_artifact_download(
            run(
                build_artifact_download_spec(
                    download_dir, env=ambient_env, timeout=_DOWNLOAD_TIMEOUT_SECONDS
                )
            ),
            download_dir,
        )
        return unpack_artifact(tarball, workspace / "artifact")

    return acquire


def _host_activator(config_dir: Path) -> Activate:
    # The host environment minus the Rehearsal Redirect, exactly as the install and a reprime
    # resolve it, so the activation and its closing Priming act on the Host, not rehearsal scratch.
    host_env = host_vv_environment(os.environ)

    def activate(artifact_root: Path) -> None:
        wheel = carried_installer_wheel_in(artifact_root)
        interpret_host_activation(
            run(
                build_host_activation_spec(
                    wheel,
                    artifact_root=artifact_root,
                    config_dir=config_dir,
                    env=host_env,
                    timeout=_ACTIVATE_TIMEOUT_SECONDS,
                )
            )
        )

    return activate


def main() -> None:
    app()
