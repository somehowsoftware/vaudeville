"""CLI handler for the `return` subcommand."""

from __future__ import annotations

from collections.abc import Callable

from vaudeville_core import ExitProfile, component_from_assignment_id

from vaudeville_coordinator import return_to_pool


def return_assignment(
    assignment_id: str,
    reason: str,
    *,
    bookkeep: Callable[[str, ExitProfile, str], None],
) -> None:
    component_from_assignment_id(assignment_id)
    return_to_pool.return_to_pool(assignment_id, reason, bookkeep=bookkeep)
