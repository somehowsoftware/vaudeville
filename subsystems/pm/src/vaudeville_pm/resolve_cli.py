"""CLI handler for the `resolve` subcommand."""

from __future__ import annotations

import sys
from collections.abc import Callable

from vaudeville_core import ExitProfile, project_from_premise_id

from vaudeville_pm import resolve


def resolve_premise(
    disposition: str,
    premise_id: str,
    reason: str,
    *,
    bookkeep: Callable[[str, ExitProfile, str], None],
) -> None:
    if disposition not in resolve.RESOLVING_DISPOSITIONS:
        sys.exit(f"unknown disposition {disposition!r}; expected delivered or abandoned")
    project_from_premise_id(premise_id)
    resolve.resolve(premise_id, disposition, reason, bookkeep=bookkeep)
