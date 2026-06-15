"""The Skill slot."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

_SCAFFOLD_SUBDIR = Path("scaffold") / ".claude" / "skills"


@dataclass(frozen=True)
class Skill:
    name: str
    source_path: Path


def discover_each_skill_in(source_root: Path) -> list[Skill]:
    container = source_root / _SCAFFOLD_SUBDIR
    if not container.is_dir():
        return []
    return [
        Skill(name=entry.name, source_path=entry)
        for entry in sorted(container.iterdir())
        if entry.is_dir()
    ]


def install_skill_at(skill: Skill, destination_root: Path) -> None:
    destination = destination_root / skill.name
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(skill.source_path, destination)
