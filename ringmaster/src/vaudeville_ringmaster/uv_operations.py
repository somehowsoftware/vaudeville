"""The imperative shell: the integrator's uv operations for Build and for the host Self-update.

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
    # Capture uv's output so a failed build carries the build backend's own account of why on the
    # raised WheelBuildFailed, not just the child's exit code. self_update_with_uv below instead
    # inherits the terminal, streaming its uv diagnostic live; the two uv seams surface a failure by
    # different means on purpose.
    try:
        subprocess.run(
            build_wheel_argv(source_root, into), check=True, capture_output=True, text=True
        )
    except subprocess.CalledProcessError as failed_build:
        raise WheelBuildFailed(source_root, failed_build) from failed_build


class WheelBuildFailed(RuntimeError):
    def __init__(self, source_root: Path, failed_build: subprocess.CalledProcessError) -> None:
        super().__init__(source_root, failed_build.returncode)
        self.source_root = source_root
        self.returncode = failed_build.returncode
        self.stdout = failed_build.stdout
        self.stderr = failed_build.stderr

    def __str__(self) -> str:
        account = "\n".join(
            stream.strip() for stream in (self.stderr, self.stdout) if stream and stream.strip()
        )
        header = f"Building the wheel for {self.source_root} failed (exit {self.returncode})"
        return f"{header}:\n{account}" if account else f"{header}, with no output captured."


def build_workspace_wheels_argv(source_root: Path, into: Path) -> list[str]:
    return ["uv", "build", "--all-packages", "--wheel", "--out-dir", str(into), str(source_root)]


def self_update_argv(distribution: str, wheelhouse: Path) -> list[str]:
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


def self_update_with_uv(builder_clone: Path, *, bin_dir: Path, tool_dir: Path) -> None:
    # The Self-update source is a Session Clone that Discard removes, so the install must depend on
    # nothing in it. Pin the tool dirs (overriding ambient UV_TOOL_*) so ringmaster installs beside
    # the Facade, and let both uv calls inherit the terminal so a failure shows uv's own diagnostic.
    distribution = distribution_name_declared_in(builder_clone / "pyproject.toml")
    with tempfile.TemporaryDirectory() as wheelhouse_root:
        wheelhouse = Path(wheelhouse_root)
        subprocess.run(build_workspace_wheels_argv(builder_clone, wheelhouse), check=True)
        subprocess.run(
            self_update_argv(distribution, wheelhouse),
            check=True,
            env={**os.environ, "UV_TOOL_BIN_DIR": str(bin_dir), "UV_TOOL_DIR": str(tool_dir)},
        )
