"""Reset every managed clone to a clean checkout of origin/main."""

from __future__ import annotations

import subprocess
from pathlib import Path


def refresh_clones(clones: list[Path]) -> None:
    for clone in clones:
        if not (clone / ".git").exists():
            continue
        subprocess.run(["git", "fetch", "origin"], cwd=clone, check=False)
        subprocess.run(
            ["git", "checkout", "-f", "-B", "main", "origin/main"], cwd=clone, check=False
        )
        subprocess.run(["git", "clean", "-fd"], cwd=clone, check=False)
