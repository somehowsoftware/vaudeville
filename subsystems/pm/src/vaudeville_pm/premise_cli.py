"""CLI handlers for Premise-aggregate subcommands.

Thin adapter layer between Typer dispatch in `cli.py` and the kernel. The
handlers carry the small decisions that are theirs — the id-shape guard
before a write, the cwd project default, the display projection — and
take the kernel operation they delegate to as an injected callable, named
in the domain's own words at the call site. The composition root binds
the real kernel op; tests bind a fake.
"""

from __future__ import annotations

from collections.abc import Callable

from vaudeville_core import Premise, project_from_premise_id

from vaudeville_pm import premise_factory
from vaudeville_pm.premise_factory import CreatePremise
from vaudeville_pm.premise_view import PremiseView


def show(premise_id: str, *, fetch: Callable[[str], Premise]) -> None:
    """Print a Premise's display view as pretty-printed JSON.

    JSON output keeps the surface unambiguous for both LLM agents (which
    read structured data reliably) and shell pipelines (``vv premise-show
    BOB-N | jq '.deps_inward[] | select(.state_resolved == false)'``).
    The rendering is one line because the schema and YouTrack-shape
    projection live in ``premise_view``; new display fields land by
    editing the ``PremiseView`` model, no rendering changes needed.
    """
    print(PremiseView.from_premise(fetch(premise_id)).model_dump_json(indent=2))


def create(
    summary: str,
    description: str,
    route: str,
    type_name: str,
    workflow: str,
    project: str | None,
    *,
    create_premise: CreatePremise,
    default_project: Callable[[], str],
) -> None:
    project = project or default_project()
    premise_id = premise_factory.create(
        project,
        summary=summary,
        description=description,
        route=route,
        type_name=type_name,
        workflow=workflow,
        create_premise=create_premise,
    )
    print(premise_id)


def claim(premise_id: str, *, claim_premise: Callable[[str], None]) -> None:
    project_from_premise_id(premise_id)  # validates id shape; exits on malformed
    claim_premise(premise_id)


def comment_add(premise_id: str, body: str, *, add_comment: Callable[[str, str], None]) -> None:
    project_from_premise_id(premise_id)
    add_comment(premise_id, body)
