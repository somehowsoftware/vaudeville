"""Vaudeville-primitive predicates over `Premise` objects.

Predicates are pure functions on `Premise` and combinators. They take
the domain type, not raw YouTrack issue dicts — the anti-corruption
layer is the boundary that owns the dict shape.
"""

from __future__ import annotations

from collections.abc import Callable

from vaudeville_core.premises import Premise

Predicate = Callable[[Premise], bool]


def deps_satisfied(premise: Premise) -> bool:
    """True iff every Premise this one depends on is resolved."""
    return all(dep.state_resolved for dep in premise.deps_inward)


def apply_predicates(candidates: list[Premise], predicates: tuple[Predicate, ...]) -> list[Premise]:
    """Filter `candidates` to those for which every predicate is true."""
    return [t for t in candidates if all(p(t) for p in predicates)]
