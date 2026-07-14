"""`vaudeville pickable`: every pickable Assignment across all Components as
one table, where ``vv available`` prints per-Component sections. The operator surface for
the pickable set.
"""

from __future__ import annotations

from collections.abc import Sequence

from vaudeville_core import Assignment, sort_key

from vaudeville_coordinator.available import (
    FindAssignments,
    ListComponents,
    available_for_component,
)

COLUMNS = ("ID", "Title", "Unblocks", "Route", "Workflow")

# A summary longer than this is truncated with an ellipsis so one wide
# Title does not stretch the whole table past legibility.
TITLE_WIDTH = 60


def pickable_across_components(
    *, find: FindAssignments, list_all: ListComponents
) -> list[Assignment]:
    """Every Pickable Assignment in every Component."""
    return [
        assignment
        for component in list_all()
        for assignment in available_for_component(component, find=find)
    ]


def legible_title(summary: str) -> str:
    if len(summary) <= TITLE_WIDTH:
        return summary
    return summary[: TITLE_WIDTH - 1] + "…"


def unblocks(assignment: Assignment) -> str:
    return ", ".join(ref.id for ref in assignment.deps_outward)


def format_table(assignments: list[Assignment]) -> str:
    if not assignments:
        return "No Pickable Assignments.\n"
    rows = [
        (
            assignment.id,
            legible_title(assignment.summary),
            unblocks(assignment),
            assignment.route,
            assignment.workflow,
        )
        for assignment in sorted(assignments, key=lambda assignment: sort_key(assignment.id))
    ]
    widths = [
        max(len(COLUMNS[column]), *(len(row[column]) for row in rows))
        for column in range(len(COLUMNS))
    ]

    def line(cells: Sequence[str]) -> str:
        return "  ".join(cell.ljust(widths[column]) for column, cell in enumerate(cells)).rstrip()

    rule = "  ".join("-" * width for width in widths)
    return "\n".join([line(COLUMNS), rule, *(line(row) for row in rows)]) + "\n"


def main(*, find: FindAssignments, list_all: ListComponents) -> None:
    print(format_table(pickable_across_components(find=find, list_all=list_all)), end="")
