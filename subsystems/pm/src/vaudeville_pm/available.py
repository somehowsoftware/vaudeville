"""`vv available` — list Premises ready to pick up across projects.

A Premise is pickable (the rule lives in ``vaudeville_pm.pickable``) when
its Workflow is Submitted/Returned, its Type is Premise, and every
Premise it depends on is resolved. By default this module enumerates
every project listed in ``~/.vaudeville/projects.toml`` and runs the
pickability rule per project; passing ``--project NAME`` restricts the
run to a single project. The tracker reads (``find``, ``list_all``) are
injected by the CLI composition root, so the report logic is exercised
against plain values.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

from vaudeville_core import Premise, sort_key

from vaudeville_pm.pickable import pickable

FindPremises = Callable[..., list[Premise]]
ListProjects = Callable[[], Sequence[str]]


def available_for_project(project: str, *, find: FindPremises) -> list[Premise]:
    """Pickable Premises in the given project."""
    candidates = find(
        project=project,
        workflow=["Submitted", "Returned"],
        type=["Premise"],
    )
    return [premise for premise in candidates if pickable(premise)]


def format_report(premises: list[Premise], project: str) -> str:
    if not premises:
        return f"{project} — 0 available Premises\n"
    rows = sorted(
        ((t.id, t.workflow, t.summary) for t in premises),
        key=lambda row: sort_key(row[0]),
    )
    id_width = max(len(row[0]) for row in rows)
    workflow_width = max(len(f"[{row[1]}]") for row in rows)
    lines = [f"{project} — {len(rows)} available Premise{'' if len(rows) == 1 else 's'}", ""]
    for premise_id, workflow, summary in rows:
        lines.append(f"{premise_id:<{id_width}}  {f'[{workflow}]':<{workflow_width}}  {summary}")
    return "\n".join(lines) + "\n"


def main(
    project: str | None = None,
    *,
    find: FindPremises,
    list_all: ListProjects,
) -> None:
    projects = [project] if project else list_all()
    first = True
    for name in projects:
        if not first:
            print()
        print(format_report(available_for_project(name, find=find), name), end="")
        first = False
