"""`vv available`: list the pickable Assignments in each Component, one section apiece."""

from __future__ import annotations

from collections.abc import Callable, Sequence

from vaudeville_core import Assignment, sort_key

from vaudeville_coordinator.pickable import pickable

FindAssignments = Callable[..., list[Assignment]]
ListComponents = Callable[[], Sequence[str]]


def available_for_component(component: str, *, find: FindAssignments) -> list[Assignment]:
    """Pickable Assignments in the given Component."""
    # Narrow only on Workflow: fetch every Submitted/Returned candidate and let
    # `pickable` filter by kind and sign-off, so a signed-off Command or Manual is
    # not dropped by the query before the predicate sees it.
    candidates = find(
        component=component,
        workflow=["Submitted", "Returned"],
    )
    return [assignment for assignment in candidates if pickable(assignment)]


def format_report(assignments: list[Assignment], component: str) -> str:
    if not assignments:
        return f"{component}: 0 available Assignments\n"
    rows = sorted(
        ((t.id, t.workflow, t.summary) for t in assignments),
        key=lambda row: sort_key(row[0]),
    )
    id_width = max(len(row[0]) for row in rows)
    workflow_width = max(len(f"[{row[1]}]") for row in rows)
    lines = [f"{component}: {len(rows)} available Assignment{'' if len(rows) == 1 else 's'}", ""]
    for assignment_id, workflow, summary in rows:
        lines.append(f"{assignment_id:<{id_width}}  {f'[{workflow}]':<{workflow_width}}  {summary}")
    return "\n".join(lines) + "\n"


def main(
    component: str | None = None,
    *,
    find: FindAssignments,
    list_all: ListComponents,
) -> None:
    components = [component] if component else list_all()
    first = True
    for name in components:
        if not first:
            print()
        print(format_report(available_for_component(name, find=find), name), end="")
        first = False
