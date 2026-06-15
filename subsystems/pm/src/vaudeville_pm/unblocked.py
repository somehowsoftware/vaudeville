"""Newly-pickable peers unblocked by a resolved Premise."""

from __future__ import annotations

from collections.abc import Callable

from vaudeville_core import Premise

from vaudeville_pm.pickable import pickable


def unblocked_peers(
    resolved: Premise,
    *,
    fetch: Callable[[str], Premise],
) -> list[Premise]:
    peers = [fetch(ref.id) for ref in resolved.deps_outward]
    return [peer for peer in peers if pickable(peer)]
