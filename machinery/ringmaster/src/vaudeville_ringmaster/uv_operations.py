"""The imperative shell: the real uv operations the integrator injects into Build.

Every wheel build runs through ``_run_uv``, integrator-side under the operator's own uv
configuration. Installing the Facade is the installer's own uv shell — see
``vaudeville_install.uv_operations`` — so that half travels inside the Artifact.
"""

from __future__ import annotations

import subprocess
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


def _run_uv(argv: list[str]) -> None:
    subprocess.run(argv, check=True, capture_output=True)
