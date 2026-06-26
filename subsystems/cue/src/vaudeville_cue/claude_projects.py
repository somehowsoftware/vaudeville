from __future__ import annotations

import re
from pathlib import Path

from vaudeville_cue import claude_config

# Claude Code names a project directory by replacing every non-alphanumeric
# character of the absolute cwd with a hyphen, one for one (no run-collapsing:
# `__` becomes `--`), so a path carrying a space, `@`, `+`, or parentheses still
# resolves to the directory Claude actually wrote. This rule must match Claude
# Code's own project-dir naming exactly; it is how a Checkpoint resolves the
# transcript directory its own session's conversation was recorded into.
_NON_ALPHANUMERIC = re.compile(r"[^A-Za-z0-9]")


def projects_root() -> Path:
    # The boundary read, resolved once at the composition root and passed inward
    # as a value, never re-read by the helpers below.
    return claude_config.config_dir() / "projects"


def project_directory(path: Path, *, projects_root: Path) -> Path:
    return projects_root / _NON_ALPHANUMERIC.sub("-", str(path))
