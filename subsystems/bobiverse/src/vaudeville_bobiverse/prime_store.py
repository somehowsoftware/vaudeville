from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import NoReturn

from vaudeville_bobiverse import claude_projects, foundation


def seed_bedrock(
    bedrock_session_id: str, *, reading: Path, projects_root: Path, data_files_root: Path
) -> None:
    # `claude --resume` keys a transcript by the cwd it runs in, so copy the shared
    # Bedrock into the reading's project dir before forking the Foundation there.
    bedrock_at = claude_projects.project_directory(data_files_root, projects_root=projects_root)
    try:
        claude_projects.copy_session(
            bedrock_session_id,
            src=bedrock_at,
            dst=claude_projects.project_directory(reading, projects_root=projects_root),
        )
    except FileNotFoundError:
        _abort(
            f"Bedrock transcript for session {bedrock_session_id} not found under "
            f"{bedrock_at}; cannot fork the Foundation in {reading}."
        )


def store_foundation_transcript(
    session_id: str, *, primed_in: Path, projects_root: Path, data_files_root: Path
) -> None:
    # Lift the forked Foundation out of its cwd-encoded project dir into the
    # path-independent store, so it is seedable regardless of where it was primed.
    primed_at = claude_projects.project_directory(primed_in, projects_root=projects_root)
    try:
        claude_projects.copy_session(
            session_id,
            src=primed_at,
            dst=foundation.transcript_store(data_files_root=data_files_root),
        )
    except FileNotFoundError:
        _abort(
            f"primed transcript for session {session_id} not found under {primed_at}; "
            f"cannot store the Foundation."
        )


def discard_reading_scratch(reading: Path, *, projects_root: Path) -> None:
    # The reading's Claude project dir holds only prime-time scratch: the seeded
    # Bedrock copy and the forked Foundation transcript. It lives under the config
    # dir, outside the reading's temp clone, so vaudeville-core's teardown never
    # reaches it and every fork would otherwise leave an orphan behind. Once the
    # Foundation is lifted into the store this dir is pure residue, so remove it.
    # ignore_errors keeps cleanup from ever masking the fork's own outcome, and the
    # per-reading path means concurrent forks never race over one directory.
    shutil.rmtree(
        claude_projects.project_directory(reading, projects_root=projects_root),
        ignore_errors=True,
    )


def _abort(message: str) -> NoReturn:
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(1)
