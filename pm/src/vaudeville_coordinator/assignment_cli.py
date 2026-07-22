"""CLI handlers for Assignment-aggregate subcommands.

Thin adapter layer between Typer dispatch in `cli.py` and "core". The
handlers carry the small decisions that are theirs (the id-shape guard
before a write, the cwd Component default, the display projection) and
take the "core" operation they delegate to as an injected callable, named
in the domain's own words at the call site. The composition root binds
the real "core" op; tests bind a fake.
"""

from __future__ import annotations

import sys
from collections.abc import Callable

from vaudeville_core import Assignment, component_from_assignment_id

from vaudeville_coordinator import assignment_factory
from vaudeville_coordinator.assignment_factory import CreateAssignment
from vaudeville_coordinator.assignment_view import AssignmentView
from vaudeville_coordinator.route_constraint import route_refusal


def show(assignment_id: str, *, fetch: Callable[[str], Assignment]) -> None:
    """Print an Assignment's display view as pretty-printed JSON.

    JSON output keeps the surface unambiguous for both LLM agents (which
    read structured data reliably) and shell pipelines (``vv assignment-show
    BOB-N | jq '.deps_inward[] | select(.state_resolved == false)'``).
    The rendering is one line because the schema and YouTrack-shape
    projection live in ``assignment_view``; new display fields appear by
    editing the ``AssignmentView`` model, no rendering changes needed.
    """
    print(AssignmentView.from_assignment(fetch(assignment_id)).model_dump_json(indent=2))


def create(
    summary: str,
    description: str,
    route: str,
    type_name: str,
    workflow: str,
    component: str | None,
    *,
    create_assignment: CreateAssignment,
    default_component: Callable[[], str],
) -> None:
    reason = route_refusal(type_name, route)
    if reason:
        sys.exit(reason)

    component = component or default_component()
    assignment_id = assignment_factory.create(
        component,
        summary=summary,
        description=description,
        route=route,
        type_name=type_name,
        workflow=workflow,
        create_assignment=create_assignment,
    )
    print(assignment_id)


def claim(assignment_id: str, *, claim_assignment: Callable[[str], None]) -> None:
    component_from_assignment_id(assignment_id)  # validates id shape; exits on malformed
    claim_assignment(assignment_id)
    print(f"Claimed {assignment_id} (State Active, Workflow Claimed)")


def comment_add(assignment_id: str, body: str, *, add_comment: Callable[[str, str], None]) -> None:
    component_from_assignment_id(assignment_id)
    add_comment(assignment_id, body)
