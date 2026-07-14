# `vaudeville update` fetches the newest Artifact where a first install is handed one already on the
# host. The GitHub download is the anti-corruption layer: release language stays on its far side and
# what crosses back is a tarball reduced to an Artifact, the word the rest of Install speaks. Every
# weird case — nothing to download, an asset that is not a single tarball, one that will not
# unpack — aborts loud here, before the ordinary Install begins.

from __future__ import annotations

import tarfile
from pathlib import Path

from vaudeville_install.child_process import Completed, LaunchFailed, Outcome, Spec, TimedOut

# The GitHub repository the framework publishes its Releases to, the one a tenant fetches the newest
# Artifact from. The same repository the integrator's Published Home names, restated here because
# the Install half fetches from it and cannot depend on the integrator that publishes to it.
VAUDEVILLE_RELEASE_ORIGIN = "somehowsoftware/vaudeville"

_ARTIFACT_ASSET_GLOB = "*.tar.gz"


def build_artifact_download_spec(into: Path, *, env: dict[str, str], timeout: float) -> Spec:
    # No tag positional: gh downloads the release GitHub marks latest, which each Publish sets to
    # the release it just cut (`gh release create` marks a non-draft, non-prerelease release latest
    # by default), so latest tracks the newest published Artifact. `--pattern` takes only the
    # Artifact tarball, never gh's auto-generated source archives (which need an unpassed flag).
    return Spec(
        argv=(
            "gh",
            "release",
            "download",
            "--repo",
            VAUDEVILLE_RELEASE_ORIGIN,
            "--pattern",
            _ARTIFACT_ASSET_GLOB,
            "--dir",
            str(into),
        ),
        env=env,
        timeout=timeout,
    )


def interpret_artifact_download(outcome: Outcome, into: Path) -> Path:
    if not (isinstance(outcome, Completed) and outcome.returncode == 0):
        raise ArtifactDownloadFailed(_why_download_failed(outcome))
    assets = sorted(into.glob(_ARTIFACT_ASSET_GLOB))
    if len(assets) != 1:
        raise ArtifactAssetNotUnique(len(assets))
    return assets[0]


def unpack_artifact(tarball: Path, into: Path) -> Path:
    # Publish packs the Artifact's children by name with no root entry, so extracting into a
    # directory makes that directory the Artifact root — indistinguishable from the `--artifact`
    # root a first Install is given. `filter="data"` refuses any member that would escape it.
    try:
        with tarfile.open(tarball, "r:gz") as archive:
            archive.extractall(into, filter="data")
    except (tarfile.TarError, OSError) as broken:
        raise ArtifactUnpackFailed(f"{tarball}: {broken}") from broken
    return into


def _why_download_failed(outcome: Outcome) -> str:
    match outcome:
        case Completed(returncode=returncode, stderr=stderr):
            detail = stderr.strip()
            base = f"`gh release download` exited {returncode}"
            return f"{base}: {detail}" if detail else base
        case TimedOut(timeout=timeout):
            return f"`gh release download` did not finish within {timeout:g}s and was terminated"
        case LaunchFailed(reason=reason):
            return reason


class ArtifactDownloadFailed(RuntimeError):
    def __init__(self, cause: str) -> None:
        super().__init__(cause)
        self.cause = cause

    def __str__(self) -> str:
        return (
            "Could not download the newest framework Artifact from "
            f"{VAUDEVILLE_RELEASE_ORIGIN}. An update needs a reachable, authenticated `gh`; "
            f"nothing was installed.\n{self.cause}"
        )


class ArtifactAssetNotUnique(RuntimeError):
    def __init__(self, count: int) -> None:
        super().__init__(count)
        self.count = count

    def __str__(self) -> str:
        return (
            f"The newest release carries {self.count} `{_ARTIFACT_ASSET_GLOB}` assets; an update "
            "needs exactly one Artifact tarball. Nothing was installed; this is a Publish-side "
            "fault to resolve at the release, not on the host."
        )


class ArtifactUnpackFailed(RuntimeError):
    def __init__(self, cause: str) -> None:
        super().__init__(cause)
        self.cause = cause

    def __str__(self) -> str:
        return (
            "Downloaded the newest framework Artifact but could not unpack it; nothing was "
            f"installed.\n{self.cause}"
        )
