"""The Data File slot: discover a Contributor's flat runtime files, collected into an Artifact."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from vaudeville_install.artifact import is_reserved_data_file_name

_SCAFFOLD_SUBDIR = Path("scaffold") / ".vaudeville"


@dataclass(frozen=True)
class DataFile:
    name: str
    source_path: Path


def discover_each_data_file_in(source_root: Path) -> list[DataFile]:
    container = source_root / _SCAFFOLD_SUBDIR
    if not container.is_dir():
        return []
    return [
        DataFile(name=entry.name, source_path=entry)
        for entry in sorted(container.iterdir())
        if entry.is_file() and not is_reserved_data_file_name(entry.name)
    ]


def install_data_file_at(data_file: DataFile, destination_dir: Path) -> None:
    destination_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(data_file.source_path, destination_dir / data_file.name)
