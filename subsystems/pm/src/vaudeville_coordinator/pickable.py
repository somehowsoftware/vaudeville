"""The pickability rule: when a Bob may claim an Assignment now. It is the one predicate
``available`` and ``unblocked`` both gate on, so the two cannot drift. The kind-clearance
rule it turns on is context UL: see ``docs/spec/vocabulary.md`` (Pickable).
"""

from __future__ import annotations

from vaudeville_core import Assignment, deps_satisfied


def requires_sign_off(assignment: Assignment) -> bool:
    # Command and Manual carry the operator's authority, so they enter the pool only
    # once the operator signs off; agent-authored Premise and Direction need no clearance.
    return assignment.type in {"Command", "Manual"}


def pickable(assignment: Assignment) -> bool:
    # Self-clearing is an explicit allowlist (Premise, Direction), not `not
    # requires_sign_off`: a kind the gate does not recognise is not pickable even when
    # signed off, so an unrecognised kind fails safe rather than auto-admitting.
    kind_cleared = assignment.type in {"Premise", "Direction"} or (
        requires_sign_off(assignment) and assignment.signed_off
    )
    return (
        kind_cleared
        and assignment.workflow in {"Submitted", "Returned"}
        and not assignment.state_resolved
        and deps_satisfied(assignment)
    )
