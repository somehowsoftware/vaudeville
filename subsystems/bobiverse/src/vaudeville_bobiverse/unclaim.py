from __future__ import annotations

from collections.abc import Callable

from vaudeville_core import UNCLAIM, ExitProfile, apply_transition


def unclaim_assignment(
    assignment: str,
    *,
    transition: Callable[[str, ExitProfile], None] = apply_transition,
) -> None:
    transition(assignment, UNCLAIM)
