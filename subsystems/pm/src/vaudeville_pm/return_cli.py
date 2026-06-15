"""CLI handler for the `return` subcommand."""

from __future__ import annotations

from collections.abc import Callable

from vaudeville_core import ExitProfile, project_from_premise_id

from vaudeville_pm import return_to_pool


def return_premise(
    premise_id: str,
    reason: str,
    *,
    bookkeep: Callable[[str, ExitProfile, str], None],
) -> None:
    project_from_premise_id(premise_id)
    return_to_pool.return_to_pool(premise_id, reason, bookkeep=bookkeep)
