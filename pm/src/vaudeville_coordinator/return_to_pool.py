"""Return an Assignment to the pickup pool: the non-resolving transition."""

from __future__ import annotations

from collections.abc import Callable

from vaudeville_core import RETURNED, ExitProfile


def return_to_pool(
    assignment_id: str,
    reason: str,
    *,
    bookkeep: Callable[[str, ExitProfile, str], None],
) -> None:
    bookkeep(assignment_id, RETURNED, reason)
