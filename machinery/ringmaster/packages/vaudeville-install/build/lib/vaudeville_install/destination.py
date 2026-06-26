"""The Destination Install targets: the operator's Host, or a throwaway Staging stand-in for it."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Layout:
    skills_dir: Path
    data_dir: Path
    hooks_dir: Path
    settings_path: Path
    bin_dir: Path
    tool_dir: Path


@dataclass(frozen=True)
class Host:
    home: Path

    @property
    def layout(self) -> Layout:
        return Layout(
            skills_dir=self.home / ".claude" / "skills",
            data_dir=self.home / ".vaudeville",
            hooks_dir=self.home / ".claude" / "hooks",
            settings_path=self.home / ".claude" / "settings.json",
            bin_dir=self.home / ".local" / "bin",
            tool_dir=self.home / ".local" / "share" / "uv" / "tools",
        )


@dataclass(frozen=True)
class Staging:
    root: Path
    host_home: Path

    @property
    def layout(self) -> Layout:
        return Layout(
            skills_dir=self.root / "skills",
            data_dir=self.root / ".vaudeville",
            hooks_dir=self.root / "hooks",
            settings_path=self.root / "settings.json",
            bin_dir=self.root / "bin",
            tool_dir=self.root / "uv-tools",
        )


Destination = Host | Staging
