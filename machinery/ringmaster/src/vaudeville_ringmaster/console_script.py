"""The Console Script slot: a Contributor's ``[project.scripts]`` entry points."""

from __future__ import annotations

import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ConsoleScript:
    name: str
    target: str


def console_scripts_declared_in(pyproject: Mapping[str, Any]) -> list[ConsoleScript]:
    project = pyproject.get("project", {})
    scripts = project.get("scripts", {}) if isinstance(project, dict) else {}
    if not isinstance(scripts, dict):
        return []
    return [
        ConsoleScript(name=name, target=target)
        for name, target in scripts.items()
        if isinstance(name, str) and isinstance(target, str)
    ]


def discover_each_console_script_in(source_root: Path) -> list[ConsoleScript]:
    pyproject = source_root / "pyproject.toml"
    if not pyproject.is_file():
        return []
    with pyproject.open("rb") as f:
        declaration = tomllib.load(f)
    return console_scripts_declared_in(declaration)
