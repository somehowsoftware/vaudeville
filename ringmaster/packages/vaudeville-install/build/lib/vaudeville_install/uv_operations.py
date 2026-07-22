"""The installer's uv boundary: install the Composed CLI and the Contributors it composes from the
Artifact's carried wheels (``--find-links``) plus public PyPI (``--index-url``), so a host needs
nothing but ``uv`` and the Artifact.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Protocol

from vaudeville_install.child_process import Completed, LaunchFailed, Outcome, Spec, TimedOut

PUBLIC_INDEX = "https://pypi.org/simple"


class InstallComposedCLI(Protocol):
    def __call__(
        self,
        *,
        distribution: str,
        find_links: Path,
        index_url: str,
        bin_dir: Path,
        tool_dir: Path,
    ) -> None: ...


def composed_cli_install_argv(
    distribution: str, find_links: Path, index_url: str, refresh_packages: Iterable[str]
) -> list[str]:
    refresh = [token for package in refresh_packages for token in ("--refresh-package", package)]
    return [
        "uv",
        "tool",
        "install",
        "--force",
        "--reinstall",
        *refresh,
        distribution,
        "--find-links",
        str(find_links),
        "--index-url",
        index_url,
        "--python",
        "3.14",
    ]


def carried_distribution_names_in(carried_cli: Path) -> tuple[str, ...]:
    # Carried wheels are frozen at one version, so uv's name+version cache can shadow a freshly
    # built wheel with a stale same-version one from an earlier deploy. Refreshing each carried
    # distribution forces uv to re-read these wheels, a backstop independent of versioning.
    wheels = carried_cli.glob("*.whl")
    return tuple(sorted({distribution_name_of_wheel(wheel) for wheel in wheels}))


def distribution_name_of_wheel(wheel: Path) -> str:
    # A wheel filename is `{name}-{version}-{tags}.whl` with the name PEP 503-escaped (runs of -_.
    # become _); reverse the escaping to the canonical name uv matches --refresh-package against.
    escaped_name = wheel.name.split("-", 1)[0]
    return re.sub(r"[-_.]+", "-", escaped_name).lower()


def build_uv_install_spec(
    *,
    distribution: str,
    find_links: Path,
    index_url: str,
    bin_dir: Path,
    tool_dir: Path,
    refresh_packages: Iterable[str],
    base_env: Mapping[str, str],
    timeout: float,
) -> Spec:
    env = {**base_env, "UV_TOOL_BIN_DIR": str(bin_dir), "UV_TOOL_DIR": str(tool_dir)}
    argv = composed_cli_install_argv(distribution, find_links, index_url, refresh_packages)
    return Spec(argv=argv, env=env, timeout=timeout)


def interpret_uv_install(distribution: str, outcome: Outcome) -> None:
    match outcome:
        case Completed(returncode=0):
            return
        case Completed(returncode=returncode, stdout=stdout, stderr=stderr):
            raise ComposedCLIInstallFailed(distribution, _uv_account(returncode, stdout, stderr))
        case TimedOut(timeout=timeout):
            raise ComposedCLIInstallFailed(
                distribution, f"`uv tool install` did not finish within {timeout:g}s"
            )
        case LaunchFailed(reason=reason):
            raise ComposedCLIInstallFailed(distribution, reason)


def _uv_account(returncode: int, stdout: str, stderr: str) -> str:
    streams = "\n".join(stream.strip() for stream in (stderr, stdout) if stream and stream.strip())
    header = f"`uv tool install` exited {returncode}"
    return f"{header}:\n{streams}" if streams else f"{header}, with no output captured."


class ComposedCLIInstallFailed(RuntimeError):
    def __init__(self, distribution: str, account: str) -> None:
        super().__init__(distribution, account)
        self.distribution = distribution
        self.account = account

    def __str__(self) -> str:
        return f"Installing the Composed CLI ({self.distribution}) failed:\n{self.account}"
