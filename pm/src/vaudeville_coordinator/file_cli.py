"""CLI handler for the compound ``file`` subcommand.

Composes an Assignment-create with optional Depend edges so a caller can
author a fully linked Assignment with one ``vv`` call instead of two. Both
``vv file`` and ``vv tangent`` route through it; ``vv tangent`` reuses
this path so the dep-id guard and create-before-link ordering are not
duplicated. The handler lives in its own module, separate from
``assignment_cli`` and ``link_cli``, so each adapter file imports only the
handlers it adapts; this one straddles creation and linking.

The ordering is the contract: the (type, route) pairing and the
edge-target ids are validated before the Assignment is created, so an
inadmissible route or a malformed ``--dep`` aborts without leaving an
Assignment on the tracker; then the edges are attached in input order. Both
"core" operations are injected so the ordering is exercised against
recorded calls.

This handler is the authoring gate ``vv file``, ``vv command``, and
``vv tangent`` all funnel through, so the route-admissibility guard lives
here once and they inherit it.
"""

from __future__ import annotations

import sys
from collections.abc import Callable

from vaudeville_core import component_from_assignment_id

from vaudeville_coordinator import assignment_factory
from vaudeville_coordinator.assignment_factory import CreateAssignment
from vaudeville_coordinator.link_cli import DependEdge
from vaudeville_coordinator.route_constraint import route_refusal


def file(
    summary: str,
    description: str,
    route: str,
    deps: list[str],
    type_name: str,
    workflow: str,
    component: str | None,
    *,
    create_assignment: CreateAssignment,
    add_depend: DependEdge,
    default_component: Callable[[], str],
) -> None:
    reason = route_refusal(type_name, route)
    if reason:
        sys.exit(reason)

    for edge_target in deps:
        component_from_assignment_id(edge_target)

    resolved_component = component or default_component()
    assignment_id = assignment_factory.create(
        resolved_component,
        summary=summary,
        description=description,
        route=route,
        type_name=type_name,
        workflow=workflow,
        create_assignment=create_assignment,
    )

    for dep in deps:
        add_depend(assignment_id, dep)

    print(assignment_id)
