"""CLI handler for the ``incident-report`` subcommand.

Files an unsigned check-in Command to investigate an incident, whose body is composed
deterministically from the captured fields (the agent never sees the template). It routes
through the same create-plus-depend gate as ``file``/``command``, with Type fixed to Command
and Route to check-in, so the Command waits outside the pickup pool until the operator signs
it off. The Component and worktree are resolved by the CLI shell and handed in already
resolved; the ``default_component`` path is never taken here, so a cwd fallback would be a bug.
"""

from __future__ import annotations

from typing import NoReturn

from vaudeville_core import component_from_assignment_id

from vaudeville_coordinator import file_cli
from vaudeville_coordinator.assignment_factory import CreateAssignment
from vaudeville_coordinator.incident_report import compose_body
from vaudeville_coordinator.link_cli import DependEdge


def incident_report(
    component: str,
    summary: str,
    problem: str,
    worktree: str,
    assignment: str | None,
    session: str | None,
    deps: list[str],
    *,
    create_assignment: CreateAssignment,
    add_depend: DependEdge,
) -> None:
    if assignment is not None:
        # Validate the id shape (exits on malformed) before the tracker write, so a
        # typo'd --assignment cannot be baked into the transcript locator of a Command
        # that already exists. Mirrors the guard --dep targets get inside file_cli.
        component_from_assignment_id(assignment)
    file_cli.file(
        summary,
        compose_body(problem, component, worktree, assignment, session),
        # check-in, not direct: the diagnosis is exactly what is open, so the
        # investigation wants a conversation before it slices into a deliverable.
        "check-in",
        deps,
        "Command",
        "Submitted",
        component,
        create_assignment=create_assignment,
        add_depend=add_depend,
        default_component=_component_already_resolved,
    )


def _component_already_resolved() -> NoReturn:
    raise AssertionError(
        "incident-report resolves its Component in the CLI shell before filing; "
        "the cwd default must never be consulted."
    )
