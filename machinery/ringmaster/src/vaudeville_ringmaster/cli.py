"""Ringmaster CLI."""

from __future__ import annotations

import hashlib
from datetime import date
from pathlib import Path
from typing import Annotated

import typer
from vaudeville_install.artifact import REGISTRY_FILENAME
from vaudeville_install.doc_tree import DocTreeContainsSymlink

from vaudeville_ringmaster import apply as _apply
from vaudeville_ringmaster import audit as _audit
from vaudeville_ringmaster import build_operation as _build
from vaudeville_ringmaster import clone as _clone
from vaudeville_ringmaster import discard as _discard
from vaudeville_ringmaster import publish as _publish
from vaudeville_ringmaster import stage as _stage
from vaudeville_ringmaster.build_operation import UnsafeBuildTarget
from vaudeville_ringmaster.exposition import (
    VAUDEVILLE_EXPOSITION_LAYOUT,
    DoctrineSourceMissing,
    ExpositionContainsSymlink,
    ExpositionLayoutMismatch,
)
from vaudeville_ringmaster.exposition_commit import (
    ExpositionCommitFailed,
    exposition_committer,
)
from vaudeville_ringmaster.github_release import (
    ReleaseCreationFailed,
    TagListingFailed,
    release_creator,
    tags_in,
)
from vaudeville_ringmaster.installer_activation import (
    InstallerFailed,
    InstallerNotCarried,
    activate_installer_with_uvx,
)
from vaudeville_ringmaster.pristine_guard import HotFixedSessionClones
from vaudeville_ringmaster.provenance import MissingCloneProvenance
from vaudeville_ringmaster.published_home import (
    RINGMASTER_CREDENTIALS_FILENAME,
    PublishedHomeTokenMissing,
    gh_runner,
    git_runner,
    published_home_token,
)
from vaudeville_ringmaster.published_version import PUBLISHED_HOME
from vaudeville_ringmaster.registry import load_registry
from vaudeville_ringmaster.session_clone import MissingSessionClones
from vaudeville_ringmaster.uv_operations import build_wheel_with_uv
from vaudeville_ringmaster.worktree import Worktree

app = typer.Typer(no_args_is_help=True)

# Everything a deploy command surfaces to the operator as a clean exit-2 failure rather than a
# traceback: the Session preconditions Ringmaster checks itself, and the carried installer's exit.
# Placement, host-wiring, priming, and Foundation failures belong to the installer, which prints
# its own diagnostic and exits non-zero; that arrives here as InstallerFailed.
_DEPLOY_ERRORS = (
    DocTreeContainsSymlink,
    MissingSessionClones,
    HotFixedSessionClones,
    UnsafeBuildTarget,
    InstallerNotCarried,
    InstallerFailed,
)


def _registry_path() -> Path:
    # The roster of Contributor Repos is integrator-internal: it ships with Ringmaster as package
    # data and is read from beside this module — never from the operator's config dir or
    # ~/.vaudeville, neither of which a fresh deploy can be trusted to hold it.
    return Path(__file__).parent / REGISTRY_FILENAME


def _session_clones_dir() -> Path:
    return Path.home() / ".vaudeville" / "session-clones"


def _config_dir() -> Path:
    return Path.home() / "vaudeville-config"


def _staged_root_for(worktree_path: Path) -> Path:
    digest = hashlib.sha1(str(worktree_path.resolve()).encode()).hexdigest()[:8]
    return Path.home() / ".vaudeville" / "staged" / digest


@app.command()
def clone() -> None:
    """Open a deploy Session."""
    registry = load_registry(_registry_path())
    _clone.clone(registry, _session_clones_dir())


@app.command()
def build(out: Annotated[Path, typer.Option("--out")]) -> None:
    """Build the self-installing Artifact to a durable path and print it."""
    registry = load_registry(_registry_path())
    try:
        artifact = _build.build(
            registry, _session_clones_dir(), out, build_wheel=build_wheel_with_uv
        )
    except _DEPLOY_ERRORS as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(2) from e
    typer.echo(str(artifact.root))


@app.command()
def stage(worktree: Path) -> None:
    """Materialize a Release Candidate as a Staged Scaffold via the Artifact's carried installer."""
    registry = load_registry(_registry_path())
    try:
        staged = _stage.stage(
            registry,
            _session_clones_dir(),
            Worktree(path=worktree),
            _staged_root_for(worktree),
            config_dir=_config_dir(),
            build_wheel=build_wheel_with_uv,
            run_installer=activate_installer_with_uvx,
            host_home=Path.home(),
        )
    except _DEPLOY_ERRORS as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(2) from e
    typer.echo(str(staged))


@app.command()
def apply() -> None:
    """Deploy the Session Clones to the Host via the Artifact's carried installer."""
    registry = load_registry(_registry_path())
    try:
        _apply.apply(
            registry,
            _session_clones_dir(),
            config_dir=_config_dir(),
            build_wheel=build_wheel_with_uv,
            run_installer=activate_installer_with_uvx,
        )
    except _DEPLOY_ERRORS as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(2) from e


@app.command()
def publish() -> None:
    """Publish the install Artifact and its source Exposition as a versioned release."""
    registry = load_registry(_registry_path())
    try:
        # Resolve the elevated token before any work, and present it to every Published Home
        # interaction through the authenticated runners — gh and git both. Read from the
        # integrator-internal credentials file, never the deployed credentials.toml. Absent, this
        # aborts before the clone, build, or commit rather than using the ambient credential.
        token = published_home_token(_config_dir() / RINGMASTER_CREDENTIALS_FILENAME)
        run_gh = gh_runner(token)
        run_git = git_runner(token)
        _publish.publish(
            registry,
            _session_clones_dir(),
            layout=VAUDEVILLE_EXPOSITION_LAYOUT,
            today=date.today(),
            list_tags=lambda: tags_in(PUBLISHED_HOME, run_gh),
            build_wheel=build_wheel_with_uv,
            create_release=release_creator(run_gh),
            commit_exposition=exposition_committer(run_git),
        )
    except (
        *_DEPLOY_ERRORS,
        PublishedHomeTokenMissing,
        ReleaseCreationFailed,
        TagListingFailed,
        ExpositionCommitFailed,
        ExpositionLayoutMismatch,
        DoctrineSourceMissing,
        ExpositionContainsSymlink,
        MissingCloneProvenance,
    ) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(2) from e


@app.command()
def discard() -> None:
    """Close the deploy Session."""
    _discard.discard(_session_clones_dir())


@app.command()
def audit(
    staged: Path,
    reference: Annotated[Path | None, typer.Option("--reference")] = None,
) -> None:
    """Walk a Built Scaffold and report structural findings."""
    findings = _audit.audit_built_scaffold(staged, reference=reference)
    for finding in findings:
        typer.echo(f"{finding.severity.value}: {finding.detail}")
    raise typer.Exit(1 if _audit.findings_are_blocking(findings) else 0)
