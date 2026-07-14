"""A Contributor's distribution: the name its code installs under, or None when it ships no code."""

from __future__ import annotations

import tomllib
from collections.abc import Mapping
from pathlib import Path
from typing import Any


def distribution_declared_in(pyproject: Mapping[str, Any]) -> str | None:
    if "build-system" not in pyproject:
        return None
    project = pyproject.get("project", {})
    name = project.get("name") if isinstance(project, dict) else None
    return name if isinstance(name, str) else None


def discover_distribution_in(source_root: Path) -> str | None:
    pyproject = source_root / "pyproject.toml"
    if not pyproject.is_file():
        return None
    with pyproject.open("rb") as f:
        declaration = tomllib.load(f)
    return distribution_declared_in(declaration)
