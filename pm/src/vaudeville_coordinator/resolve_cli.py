"""CLI handler for the `resolve` subcommand."""

from __future__ import annotations

import sys
from collections.abc import Callable

from vaudeville_core import ExitProfile, component_from_assignment_id

from vaudeville_coordinator import resolve


def resolve_assignment(
    disposition: str,
    assignment_id: str,
    reason: str,
    *,
    bookkeep: Callable[[str, ExitProfile, str], None],
) -> None:
    if disposition not in resolve.RESOLVING_DISPOSITIONS:
        sys.exit(f"unknown disposition {disposition!r}; expected delivered or abandoned")
    component_from_assignment_id(assignment_id)
    resolve.resolve(assignment_id, disposition, reason, bookkeep=bookkeep)
