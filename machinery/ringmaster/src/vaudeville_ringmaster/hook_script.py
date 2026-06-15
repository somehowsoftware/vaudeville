"""The Hook Script slot."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

_SCAFFOLD_SUBDIR = Path("scaffold") / ".claude" / "hooks"


@dataclass(frozen=True)
class HookScript:
    name: str
    source_path: Path


def discover_each_hook_script_in(source_root: Path) -> list[HookScript]:
    container = source_root / _SCAFFOLD_SUBDIR
    if not container.is_dir():
        return []
    return [
        HookScript(name=entry.name, source_path=entry)
        for entry in sorted(container.iterdir())
        if entry.is_file()
    ]


def install_hook_script_at(hook_script: HookScript, destination_dir: Path) -> None:
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / hook_script.name
    shutil.copy2(hook_script.source_path, destination)
    # Hook Scripts are executables by definition; ensure +x even if the Contributor committed
    # the source without it. Claude Code's runtime invocation fails otherwise.
    destination.chmod(destination.stat().st_mode | 0o111)
