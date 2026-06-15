"""Where Claude Code keeps its per-config-dir state — the projects and skills roots.

Claude Code reads its session transcripts and its skills from a config directory
named by ``$CLAUDE_CONFIG_DIR``, or ``~/.claude`` when that is unset. Both the
projects store and the skills set hang off that one directory, so resolving it in
one place keeps the two consumers from drifting. The top-level ``~/.claude.json``
config file is a separate location with its own fallback — see ``spawn.trust`` —
so it is not derived here.
"""

from __future__ import annotations

import os
from pathlib import Path


def config_dir() -> Path:
    override = os.environ.get("CLAUDE_CONFIG_DIR")
    return Path(override) if override else Path.home() / ".claude"


def skills_root() -> Path:
    return config_dir() / "skills"
