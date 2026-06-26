from __future__ import annotations

from collections.abc import Callable

from vaudeville_coordinator import file_cli
from vaudeville_coordinator.assignment_factory import CreateAssignment
from vaudeville_coordinator.link_cli import DependEdge


def file_command(
    summary: str,
    description: str,
    route: str,
    deps: list[str],
    component: str | None,
    *,
    create_assignment: CreateAssignment,
    add_depend: DependEdge,
    default_component: Callable[[], str],
) -> None:
    file_cli.file(
        summary,
        description,
        route,
        deps,
        "Command",
        "Submitted",
        component,
        create_assignment=create_assignment,
        add_depend=add_depend,
        default_component=default_component,
    )
