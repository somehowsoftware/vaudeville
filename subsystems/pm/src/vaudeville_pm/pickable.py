"""The Vaudeville pickability rule, in one place.

A Premise is *pickable* when a Bob may claim it now: it is an open
Premise (Type Premise, Workflow Submitted or Returned) and every Premise
it depends on is resolved. ``available`` and ``unblocked`` both gate on
this rule; it lives here as a single pure predicate so the two cannot
drift apart.
"""

from __future__ import annotations

from vaudeville_core import Premise, deps_satisfied


def pickable(premise: Premise) -> bool:
    return (
        premise.type == "Premise"
        and premise.workflow in {"Submitted", "Returned"}
        and not premise.state_resolved
        and deps_satisfied(premise)
    )
