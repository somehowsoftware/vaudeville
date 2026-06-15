"""Gate /spawn on the per-peer pickability stack derived from the Premise's own project.

The same workflow/type/deps predicates that `/available` and `/onward`
apply to candidate sets — but here scoped to a single Premise whose
project is derived from its id. That makes spawn-preflight the
authoritative receiving-end gate when a peer arrives via cross-project
fanout from ``/onward``: the calling Bob's project is irrelevant; the
peer's own predicate stack is what determines pickability.
"""

from __future__ import annotations

import sys

from vaudeville_core import (
    Premise,
    deps_satisfied,
    get_premise,
    project_from_premise_id,
)

SPAWNABLE_ROUTES: frozenset[str] = frozenset({"direct", "check-in", "plan", "manual"})

# A backlog problem, not a host one: distinct from the host-state exits the rest
# of the Spawn pipeline raises (missing clone, no Foundation).
PREFLIGHT_REFUSED_EXIT = 1


def preflight_refusal(premise: Premise, project: str) -> str | None:
    # Order matches unblocked_peers in /onward. deps_satisfied is the
    # authoritative dep gate — its refusal wording is canonical because a
    # Bob never spawns on a dep-blocked Premise.
    if not premise.id.startswith(f"{project}-"):
        return f"{premise.id} is not a {project} Premise"
    if premise.workflow not in {"Submitted", "Returned"}:
        workflow = premise.workflow or "<unset>"
        return f"{premise.id} Workflow is {workflow!r} (not Submitted/Returned)"
    if premise.type not in {"Premise", "Bug"}:
        type_name = premise.type or "<unset>"
        return f"{premise.id} Type is {type_name!r} (not Premise/Bug)"
    if not premise.route:
        return f"{premise.id} missing Route — needs backlog grooming"
    if premise.route not in SPAWNABLE_ROUTES:
        return f"{premise.id} Route {premise.route!r} — not a spawnable Route"
    if not deps_satisfied(premise):
        unresolved = ", ".join(d.id for d in premise.deps_inward if not d.state_resolved)
        return f"{premise.id} blocked by {unresolved} (unresolved)"
    return None


def main(premise_id: str) -> None:
    project = project_from_premise_id(premise_id)
    premise = get_premise(premise_id)
    refusal = preflight_refusal(premise, project)
    if refusal is not None:
        print(refusal, file=sys.stderr)
        sys.exit(PREFLIGHT_REFUSED_EXIT)
