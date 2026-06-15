"""The imperative shell for the installer's uv calls: install the Facade from the carried wheels.

Mirrors the integrator's wheel-building uv shell on the install side: the installer resolves the
Facade and the Contributors it composes from the Unit's carried wheels (``--find-links``) plus
public PyPI (``--index-url``), so a host needs nothing but ``uv`` and the Unit.
"""

from __future__ import annotations

import os
import re
import subprocess
from collections.abc import Iterable
from pathlib import Path
from typing import Protocol

PUBLIC_INDEX = "https://pypi.org/simple"


class InstallFacade(Protocol):
    def __call__(
        self,
        *,
        distribution: str,
        find_links: Path,
        index_url: str,
        bin_dir: Path,
        tool_dir: Path,
    ) -> None: ...


def facade_install_argv(
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


def install_facade_with_uv(
    *,
    distribution: str,
    find_links: Path,
    index_url: str,
    bin_dir: Path,
    tool_dir: Path,
) -> None:
    _run_uv(
        facade_install_argv(
            distribution, find_links, index_url, carried_distribution_names_in(find_links)
        ),
        extra_env={"UV_TOOL_BIN_DIR": str(bin_dir), "UV_TOOL_DIR": str(tool_dir)},
    )


def _run_uv(argv: list[str], *, extra_env: dict[str, str] | None = None) -> None:
    environment = {**os.environ, **extra_env} if extra_env else None
    subprocess.run(argv, env=environment, check=True, capture_output=True)
