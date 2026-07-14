"""Vaudeville-primitive predicates over `Assignment` objects.

Predicates are pure functions on `Assignment` and combinators. They take
the domain type, not raw YouTrack issue dicts; the anti-corruption
layer is the boundary that owns the dict shape.
"""

from __future__ import annotations

from collections.abc import Callable

from vaudeville_core.assignments import Assignment

Predicate = Callable[[Assignment], bool]


def deps_satisfied(assignment: Assignment) -> bool:
    """True iff every Assignment this one depends on is resolved."""
    return all(dep.state_resolved for dep in assignment.deps_inward)


def apply_predicates(
    candidates: list[Assignment], predicates: tuple[Predicate, ...]
) -> list[Assignment]:
    """Filter `candidates` to those for which every predicate is true."""
    return [t for t in candidates if all(p(t) for p in predicates)]
