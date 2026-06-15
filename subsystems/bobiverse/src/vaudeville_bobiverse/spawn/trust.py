"""Pre-accept Claude Code's folder-trust for a spawned Bob's worktree.

Claude Code blocks on an interactive "trust this folder?" dialog the first time
it opens a directory not recorded as trusted. A spawned Bob runs headless under
Remote Control, so no one answers it and the Bob hangs before it reads its Brief.
Spawning a Bob into a worktree is the operator trusting that worktree, so the
spawn writes the ``hasTrustDialogAccepted`` flag Claude Code records on a human's
acceptance — into ``$CLAUDE_CONFIG_DIR/.claude.json``, or ``~/.claude.json`` on
the host install — before launch.
"""

from __future__ import annotations

import fcntl
import json
import os
import tempfile
from pathlib import Path
from typing import Any

TRUST_KEY = "hasTrustDialogAccepted"


def claude_config_file() -> Path:
    config_dir = os.environ.get("CLAUDE_CONFIG_DIR")
    base = Path(config_dir) if config_dir else Path.home()
    return base / ".claude.json"


def config_trusting_worktree(config: dict[str, Any], worktree: Path) -> dict[str, Any]:
    projects = dict(config.get("projects", {}))
    entry = dict(projects.get(str(worktree), {}))
    entry[TRUST_KEY] = True
    projects[str(worktree)] = entry
    return {**config, "projects": projects}


def record_worktree_trust(worktree: Path, *, config_file: Path) -> None:
    config_file.parent.mkdir(parents=True, exist_ok=True)
    # A fanout close (`/onward`) and concurrent closes spawn several Bobs at once,
    # each rewriting this one shared file; hold an exclusive lock across the
    # read-modify-write and replace atomically so concurrent spawns don't drop
    # each other's trust entries.
    lock = config_file.with_name(config_file.name + ".lock")
    with lock.open("w") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        config = json.loads(config_file.read_text()) if config_file.exists() else {}
        updated = config_trusting_worktree(config, worktree)
        _replace_atomically(config_file, json.dumps(updated, indent=2))


def _replace_atomically(target: Path, text: str) -> None:
    with tempfile.NamedTemporaryFile(
        "w", dir=target.parent, prefix=target.name, suffix=".tmp", delete=False
    ) as scratch:
        scratch.write(text)
        scratch_path = scratch.name
    os.replace(scratch_path, target)
