from __future__ import annotations

from collections.abc import Callable

from vaudeville_core import Assignment

from vaudeville_coordinator.awaiting_sign_off import awaiting_sign_off
from vaudeville_coordinator.pickable import pickable


def unblocked_peers(
    resolved: Assignment,
    *,
    fetch: Callable[[str], Assignment],
) -> list[Assignment]:
    return [peer for peer in _outward_peers(resolved, fetch=fetch) if pickable(peer)]


def awaiting_sign_off_peers(
    resolved: Assignment,
    *,
    fetch: Callable[[str], Assignment],
) -> list[Assignment]:
    return [peer for peer in _outward_peers(resolved, fetch=fetch) if awaiting_sign_off(peer)]


def _outward_peers(resolved: Assignment, *, fetch: Callable[[str], Assignment]) -> list[Assignment]:
    return [fetch(ref.id) for ref in resolved.deps_outward]
