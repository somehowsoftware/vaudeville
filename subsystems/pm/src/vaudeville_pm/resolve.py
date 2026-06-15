"""Resolving close of a Premise: deliver or abandon."""

from __future__ import annotations

from collections.abc import Callable

from vaudeville_core import ABANDONED, DELIVERED, ExitProfile

RESOLVING_DISPOSITIONS = {"delivered": DELIVERED, "abandoned": ABANDONED}


def resolve(
    premise_id: str,
    disposition: str,
    reason: str,
    *,
    bookkeep: Callable[[str, ExitProfile, str], None],
) -> None:
    bookkeep(premise_id, RESOLVING_DISPOSITIONS[disposition], reason)
