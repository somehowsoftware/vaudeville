"""The Discard operation."""

from __future__ import annotations

from pathlib import Path

from vaudeville_ringmaster.session_clone import discard_all_session_clones_in


def discard(session_clones_dir: Path) -> None:
    discard_all_session_clones_in(session_clones_dir)
