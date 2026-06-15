"""CLI handler for the compound ``file`` subcommand.

Composes a Premise-create with optional Depend edges so a caller can
author a fully linked Premise with one ``vv`` call instead of two. Both
``vv file`` and ``vv tangent`` route through it — ``vv tangent`` reuses
this path so the dep-id guard and create-before-link ordering are not
duplicated. The handler lives in its own module — separate from
``premise_cli`` and ``link_cli`` — so each adapter file imports only the
handlers it adapts; this one straddles creation and linking.

The ordering is the contract: edge-target ids are validated before the
Premise is created, so a malformed ``--dep`` aborts without leaving an
unlinked Premise on the tracker; then the edges are attached in input
order. Both kernel operations are injected so the ordering is exercised
against recorded calls.
"""

from __future__ import annotations

from collections.abc import Callable

from vaudeville_core import project_from_premise_id

from vaudeville_pm import premise_factory
from vaudeville_pm.link_cli import DependEdge
from vaudeville_pm.premise_factory import CreatePremise


def file(
    summary: str,
    description: str,
    route: str,
    deps: list[str],
    type_name: str,
    workflow: str,
    project: str | None,
    *,
    create_premise: CreatePremise,
    add_depend: DependEdge,
    default_project: Callable[[], str],
) -> None:
    for edge_target in deps:
        project_from_premise_id(edge_target)

    resolved_project = project or default_project()
    premise_id = premise_factory.create(
        resolved_project,
        summary=summary,
        description=description,
        route=route,
        type_name=type_name,
        workflow=workflow,
        create_premise=create_premise,
    )

    for dep in deps:
        add_depend(premise_id, dep)

    print(premise_id)
