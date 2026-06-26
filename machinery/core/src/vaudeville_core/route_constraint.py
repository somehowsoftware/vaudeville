"""The (kind → permitted routes) constraint: the one definition consumers read instead of
each re-deriving it.

Core publishes the constraint; it does not enforce. Consumers (spawn-preflight, Coordinator
authoring) read it and reject at their own gates. Data only: no I/O.
"""

from __future__ import annotations

from vaudeville_core.assignments import Assignment

PERMITTED_ROUTES: dict[str, frozenset[str]] = {
    "Premise": frozenset({"check-in", "plan", "explore"}),
    "Direction": frozenset({"check-in"}),
    "Command": frozenset({"check-in", "direct"}),
    "Manual": frozenset(),
}


def route_permitted(assignment: Assignment) -> bool:
    """True iff the Assignment carries a Route its kind permits.

    False for every Manual is deliberate, not a gap: a Manual permits no Route, and judging a
    correctly routeless Manual as valid is the consumer's spawnability call, not this predicate's.
    """
    return assignment.route in PERMITTED_ROUTES.get(assignment.type, frozenset())
