"""Seed a stored Foundation transcript into a clone so ``workmux add --fork`` resolves.

``--fork=<session-id>`` resolves the conversation within the *current worktree's*
Claude project directory — the clone spawn cd's into. The Foundation transcript
lives in the path-independent store, not under that clone's encoding, so spawn
copies it in before ``workmux add``. This is what lets a Bob fork its Foundation
no matter where its clone sits on disk.

A successful seed yields a ``SeededClone``: the clone the transcript was copied
into and the session the fork resolves. ``workmux`` builds its fork invocation
only from that witness, so seed-before-fork is structural — a Bob cannot be
launched against a clone its Foundation was never seeded into.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from vaudeville_bobiverse import claude_projects, foundation

STRANDED_FOUNDATION_EXIT = 2


@dataclass(frozen=True)
class SeededClone:
    clone: Path
    foundation_session: str


def seed_foundation(
    session_id: str, *, into_clone: Path, projects_root: Path, data_files_root: Path
) -> SeededClone:
    store = foundation.transcript_store(data_files_root=data_files_root)
    try:
        claude_projects.copy_session(
            session_id,
            src=store,
            dst=claude_projects.project_directory(into_clone, projects_root=projects_root),
        )
    except FileNotFoundError:
        print(
            f"Error: Foundation transcript for session {session_id} is not in the store "
            f"({store}); the Foundation is stranded. Run `vv prime` to repopulate it.",
            file=sys.stderr,
        )
        sys.exit(STRANDED_FOUNDATION_EXIT)
    return SeededClone(clone=into_clone, foundation_session=session_id)
