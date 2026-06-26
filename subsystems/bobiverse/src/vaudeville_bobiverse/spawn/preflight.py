from __future__ import annotations

import sys

from vaudeville_core import (
    PERMITTED_ROUTES,
    Assignment,
    component_from_assignment_id,
    deps_satisfied,
    get_assignment,
)

# A backlog problem, not a host one: distinct from the host-state exits the rest
# of the Spawn pipeline raises (missing clone, no Foundation).
PREFLIGHT_REFUSED_EXIT = 1


def route_constraint_refusal(assignment: Assignment) -> str | None:
    # vaudeville-core's (kind → permitted routes) constraint, enforced at the spawn
    # gate. Manual is the no-route kind: spawnable only when correctly routeless,
    # so a missing Route is its valid state, not its refusal.
    permitted = PERMITTED_ROUTES.get(assignment.type)
    if permitted is None:
        type_name = assignment.type or "<unset>"
        return f"{assignment.id} Type is {type_name!r} (not {'/'.join(PERMITTED_ROUTES)})"
    if not permitted:
        if assignment.route:
            return (
                f"{assignment.id} Type {assignment.type!r} takes no Route, "
                f"but has {assignment.route!r}"
            )
        return None
    if not assignment.route:
        return f"{assignment.id} missing Route: needs backlog grooming"
    if assignment.route not in permitted:
        return (
            f"{assignment.id} Route {assignment.route!r} not permitted for Type {assignment.type!r}"
        )
    return None


def sign_off_refusal(assignment: Assignment) -> str | None:
    # The operator sign-off gate (PM-124), enforced defence-in-depth at the spawn
    # gate. The pickup pool already keeps an un-signed-off Command/Manual out of
    # /available; this refuses a direct `vv spawn` that bypasses the pool.
    # Premise and Direction carry no sign-off: they are always spawnable.
    if assignment.type in {"Command", "Manual"} and not assignment.signed_off:
        return (
            f"{assignment.id} is a {assignment.type} that has not been signed off; "
            f"the operator must sign off before it can be spawned."
        )
    return None


def preflight_refusal(assignment: Assignment, component: str) -> str | None:
    # Order matches unblocked_peers in /onward. deps_satisfied is the
    # authoritative dep gate: its refusal wording is canonical because a
    # Bob never spawns on a dep-blocked Assignment.
    if not assignment.id.startswith(f"{component}-"):
        return f"{assignment.id} is not a {component} Assignment"
    if assignment.workflow not in {"Submitted", "Returned"}:
        workflow = assignment.workflow or "<unset>"
        return f"{assignment.id} Workflow is {workflow!r} (not Submitted/Returned)"
    constraint_refusal = route_constraint_refusal(assignment)
    if constraint_refusal is not None:
        return constraint_refusal
    sign_off = sign_off_refusal(assignment)
    if sign_off is not None:
        return sign_off
    if not deps_satisfied(assignment):
        unresolved = ", ".join(d.id for d in assignment.deps_inward if not d.state_resolved)
        return f"{assignment.id} blocked by {unresolved} (unresolved)"
    return None


def main(assignment_id: str) -> None:
    component = component_from_assignment_id(assignment_id)
    assignment = get_assignment(assignment_id)
    refusal = preflight_refusal(assignment, component)
    if refusal is not None:
        print(refusal, file=sys.stderr)
        sys.exit(PREFLIGHT_REFUSED_EXIT)
