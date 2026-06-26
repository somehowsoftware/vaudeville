"""The coordinator's reading of the (kind → permitted routes) constraint vaudeville-core publishes.

vaudeville-core publishes the constraint as data (``PERMITTED_ROUTES``) alongside a
``route_permitted`` predicate that returns False for every Manual, deliberately,
since a Manual permits no Route and judging a correctly-routeless Manual as valid
is the consumer's call, not the predicate's. So this context reads the published
map directly rather than the predicate: ``route_refusal`` is the authoring
boundary's admissibility decision over a raw ``(type_name, route)`` pair, naming a
domain-readable reason or returning ``None`` when the pair is admissible. Pure:
data in, a reason or None out, no I/O; the ``vv file`` / ``vv assignment-create``
handlers turn a non-None reason into the process abort at their gate.
"""

from __future__ import annotations

from vaudeville_core import PERMITTED_ROUTES


def route_refusal(type_name: str, route: str) -> str | None:
    permitted = PERMITTED_ROUTES.get(type_name)
    if permitted is None:
        return f"unknown type {type_name!r}; valid types are {', '.join(PERMITTED_ROUTES)}"
    if not permitted:
        if route:
            return f"a {type_name} takes no route; got {route!r}"
        return None
    options = ", ".join(sorted(permitted))
    if not route:
        return f"a {type_name} needs a route; one of {options}"
    if route not in permitted:
        return f"route {route!r} not permitted for a {type_name}; one of {options}"
    return None
