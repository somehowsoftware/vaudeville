from __future__ import annotations

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


def _abort(message: str) -> NoReturn:
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(1)
