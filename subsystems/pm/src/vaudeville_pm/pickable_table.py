"""`vaudeville pickable` — every Pickable Premise across all Managed Repositories, as one table.

The operator surface for the Pickable set. Where ``vv available`` prints
per-project sections for a machine reader, this renders a single
five-column table — ID, Title, Unblocks, Route, Workflow — over every
Managed Repository at once, sorted by id (prefix, then number). The
pickability rule lives in ``vaudeville_pm.pickable`` and the per-project
gather in ``vaudeville_pm.available``; this module reuses both and adds
only the cross-repository flatten and the operator's table rendering. The
tracker reads (``find``, ``list_all``) are injected by the CLI
composition root, so the rendering is exercised against plain values.
"""

from __future__ import annotations

from collections.abc import Sequence

from vaudeville_core import Premise, sort_key

from vaudeville_pm.available import FindPremises, ListProjects, available_for_project

COLUMNS = ("ID", "Title", "Unblocks", "Route", "Workflow")

# A summary longer than this is truncated with an ellipsis so one wide
# Title does not stretch the whole table past legibility.
TITLE_WIDTH = 60


def pickable_across_repositories(*, find: FindPremises, list_all: ListProjects) -> list[Premise]:
    """Every Pickable Premise in every Managed Repository."""
    return [
        premise for project in list_all() for premise in available_for_project(project, find=find)
    ]


def legible_title(summary: str) -> str:
    if len(summary) <= TITLE_WIDTH:
        return summary
    return summary[: TITLE_WIDTH - 1] + "…"


def unblocks(premise: Premise) -> str:
    return ", ".join(ref.id for ref in premise.deps_outward)


def format_table(premises: list[Premise]) -> str:
    if not premises:
        return "No Pickable Premises.\n"
    rows = [
        (
            premise.id,
            legible_title(premise.summary),
            unblocks(premise),
            premise.route,
            premise.workflow,
        )
        for premise in sorted(premises, key=lambda premise: sort_key(premise.id))
    ]
    widths = [
        max(len(COLUMNS[column]), *(len(row[column]) for row in rows))
        for column in range(len(COLUMNS))
    ]

    def line(cells: Sequence[str]) -> str:
        return "  ".join(cell.ljust(widths[column]) for column, cell in enumerate(cells)).rstrip()

    rule = "  ".join("-" * width for width in widths)
    return "\n".join([line(COLUMNS), rule, *(line(row) for row in rows)]) + "\n"


def main(*, find: FindPremises, list_all: ListProjects) -> None:
    print(format_table(pickable_across_repositories(find=find, list_all=list_all)), end="")
