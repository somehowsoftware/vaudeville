"""The awaiting-sign-off rule: a freed Command or Manual held for the operator's
sign-off. It is the mirror of ``pickable`` over the same open-and-deps gate, differing
only on ``signed_off``. See ``docs/spec/vocabulary.md`` (Awaiting Sign-off).
"""

from __future__ import annotations

from vaudeville_core import Assignment, deps_satisfied

from vaudeville_coordinator.pickable import requires_sign_off


def awaiting_sign_off(assignment: Assignment) -> bool:
    return (
        requires_sign_off(assignment)
        and not assignment.signed_off
        and assignment.workflow in {"Submitted", "Returned"}
        and not assignment.state_resolved
        and deps_satisfied(assignment)
    )
