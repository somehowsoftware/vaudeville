from __future__ import annotations

import re
import shutil
from pathlib import Path

from vaudeville_bobiverse import claude_config

# Claude Code names a project directory by replacing every non-alphanumeric
# character of the absolute cwd with a hyphen, one for one (no run-collapsing:
# `__` becomes `--`), so a path carrying a space, `@`, `+`, or parentheses still
# resolves to the directory Claude actually wrote. scripts/teardown-archive-and-remove.sh
# (the closeout archive) reimplements this rule in shell and must stay identical.
_NON_ALPHANUMERIC = re.compile(r"[^A-Za-z0-9]")


def projects_root() -> Path:
    # The boundary read, resolved once at the composition root and passed inward
    # as a value, never re-read by the helpers below.
    return claude_config.config_dir() / "projects"


def project_directory(path: Path, *, projects_root: Path) -> Path:
    return projects_root / _NON_ALPHANUMERIC.sub("-", str(path))


def copy_session(session_id: str, *, src: Path, dst: Path) -> None:
    spine = src / f"{session_id}.jsonl"
    if not spine.is_file():
        raise FileNotFoundError(spine)
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copy2(spine, dst / f"{session_id}.jsonl")
    sidecar = src / session_id
    if sidecar.is_dir():
        shutil.copytree(sidecar, dst / session_id, dirs_exist_ok=True)
