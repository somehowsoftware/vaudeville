"""The imperative shell: the integrator's uv operations for Build and for renewing the host Builder.

Installing the Facade is the installer's own uv shell (see ``vaudeville_install.uv_operations``),
so that half travels inside the Artifact.
"""

from __future__ import annotations

import os
import subprocess
import tempfile
import tomllib
from pathlib import Path
from typing import Protocol


class BuildWheel(Protocol):
    def __call__(self, source_root: Path, into: Path) -> None: ...


def build_wheel_argv(source_root: Path, into: Path) -> list[str]:
    return [
        "uv",
        "build",
        "--wheel",
        "--out-dir",
        str(into),
        str(source_root),
    ]


def build_wheel_with_uv(source_root: Path, into: Path) -> None:
    _run_uv(build_wheel_argv(source_root, into))


def build_workspace_wheels_argv(source_root: Path, into: Path) -> list[str]:
    return ["uv", "build", "--all-packages", "--wheel", "--out-dir", str(into), str(source_root)]


def renew_builder_argv(distribution: str, wheelhouse: Path) -> list[str]:
    # --reinstall implies --refresh, so a rebuilt same-version wheel is re-read, not served stale
    # from uv's cache. Unlike the Facade install, no per-distribution --refresh-package is needed.
    return [
        "uv",
        "tool",
        "install",
        "--force",
        "--reinstall",
        distribution,
        "--find-links",
        str(wheelhouse),
        "--python",
        "3.14",
    ]


def distribution_name_declared_in(pyproject: Path) -> str:
    with pyproject.open("rb") as f:
        return str(tomllib.load(f)["project"]["name"])


def renew_builder_with_uv(builder_clone: Path, *, bin_dir: Path, tool_dir: Path) -> None:
    # The renew source is a Session Clone that Discard removes, so the install must depend on
    # nothing in it. Pin the tool dirs (overriding ambient UV_TOOL_*) so ringmaster installs beside
    # the Facade, and let both uv calls inherit the terminal so a failure shows uv's own diagnostic.
    distribution = distribution_name_declared_in(builder_clone / "pyproject.toml")
    with tempfile.TemporaryDirectory() as wheelhouse_root:
        wheelhouse = Path(wheelhouse_root)
        subprocess.run(build_workspace_wheels_argv(builder_clone, wheelhouse), check=True)
        subprocess.run(
            renew_builder_argv(distribution, wheelhouse),
            check=True,
            env={**os.environ, "UV_TOOL_BIN_DIR": str(bin_dir), "UV_TOOL_DIR": str(tool_dir)},
        )


def _run_uv(argv: list[str]) -> None:
    subprocess.run(argv, check=True, capture_output=True)
