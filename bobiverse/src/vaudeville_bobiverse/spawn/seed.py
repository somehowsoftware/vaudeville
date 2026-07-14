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
    # `workmux add --fork` resolves its source conversation within the clone's
    # Claude project directory, but the Foundation transcript lives in the
    # path-independent store, not under that clone's path encoding; so copy it in
    # first, or the fork has nothing to resolve.
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
