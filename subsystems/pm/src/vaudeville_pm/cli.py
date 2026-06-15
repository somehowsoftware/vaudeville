from __future__ import annotations

from typing import Annotated

import typer
from vaudeville_core import (
    add_comment,
    add_depend,
    apply_bookkeeping,
    claim_premise,
    create_premise,
    find_premises,
    get_premise,
    list_projects,
    project_from_cwd,
    remove_depend,
)

from vaudeville_pm import (
    available,
    file_cli,
    link_cli,
    premise_cli,
    resolve_cli,
    return_cli,
    tangent_cli,
    unblocked_cli,
)

app = typer.Typer(
    name="vv-pm",
    help="Vaudeville PM CLI: planning and backlog operations on Premises.",
    context_settings={"help_option_names": ["-h", "--help"]},
)

ProjectOption = Annotated[
    str | None,
    typer.Option(
        "--project",
        help=(
            "Project short name (BOB, PM, CORE, …). Defaults to the project "
            "whose main clone contains cwd."
        ),
    ),
]


@app.command(name="available", help="List Premises ready to pick up in the cwd project.")
def available_command(project: ProjectOption = None) -> None:
    available.main(project, find=find_premises, list_all=list_projects)


@app.command(
    name="resolve",
    help=(
        "Apply a resolving close (delivered or abandoned) to a Premise: write the State "
        "transition and a reason comment. Does not tear down the worktree."
    ),
)
def resolve_command(
    disposition: Annotated[str, typer.Argument(help="delivered or abandoned")],
    premise: Annotated[str, typer.Argument(help="Premise id, e.g. BOB-26")],
    reason: Annotated[str, typer.Option(help="Reason body (the disposition's header is added)")],
) -> None:
    resolve_cli.resolve_premise(disposition, premise, reason, bookkeep=apply_bookkeeping)


@app.command(
    name="return",
    help=(
        "Return a Premise to the pickup pool (Active/Returned + return note), unassigned. "
        "Does not tear down the worktree."
    ),
)
def return_command(
    premise: Annotated[str, typer.Argument(help="Premise id, e.g. BOB-26")],
    reason: Annotated[str, typer.Option(help="Return note body (header is added)")],
) -> None:
    return_cli.return_premise(premise, reason, bookkeep=apply_bookkeeping)


@app.command(
    name="unblocked",
    help=(
        "Print the newly-pickable Depend peers of a RESOLVED Premise, one id per line. "
        "Refuses if the Premise is not yet resolved."
    ),
)
def unblocked_command(
    premise: Annotated[str, typer.Argument(help="Premise id, e.g. BOB-26")],
) -> None:
    unblocked_cli.show(premise, fetch=get_premise)


@app.command(
    name="premise-show",
    help="Print the Premise's summary, custom fields, and Depend peers (one field per line).",
)
def premise_show_command(
    premise: Annotated[str, typer.Argument(help="Premise id, e.g. BOB-26")],
) -> None:
    premise_cli.show(premise, fetch=get_premise)


@app.command(
    name="premise-create",
    help="Create a Premise in the cwd project (or --project) and print its idReadable.",
)
def premise_create_command(
    summary: Annotated[str, typer.Option(help="One-line summary")],
    description: Annotated[str, typer.Option(help="Body markdown")],
    route: Annotated[str, typer.Option(help="Route: direct, check-in, plan, manual")],
    type_name: Annotated[
        str,
        typer.Option("--type", help="Type: Premise, Bug. Default: Premise."),
    ] = "Premise",
    workflow: Annotated[
        str,
        typer.Option(help="Workflow: Submitted, Returned, Claimed. Default: Submitted."),
    ] = "Submitted",
    project: ProjectOption = None,
) -> None:
    premise_cli.create(
        summary,
        description,
        route,
        type_name,
        workflow,
        project,
        create_premise=create_premise,
        default_project=project_from_cwd,
    )


@app.command(
    name="file",
    help=(
        "Author a Premise and attach its Depend edges in one call. "
        "Prints the new Premise's idReadable on success."
    ),
)
def file_command(
    summary: Annotated[str, typer.Option(help="One-line summary")],
    description: Annotated[str, typer.Option(help="Body markdown")],
    route: Annotated[str, typer.Option(help="Route: direct, check-in, plan, manual")],
    dep: Annotated[
        list[str] | None,
        typer.Option(help="Depend-on Premise id; repeatable, one Depend edge per value"),
    ] = None,
    type_name: Annotated[
        str,
        typer.Option("--type", help="Type: Premise, Bug. Default: Premise."),
    ] = "Premise",
    workflow: Annotated[
        str,
        typer.Option(help="Workflow: Submitted, Returned, Claimed. Default: Submitted."),
    ] = "Submitted",
    project: ProjectOption = None,
) -> None:
    file_cli.file(
        summary,
        description,
        route,
        dep or [],
        type_name,
        workflow,
        project,
        create_premise=create_premise,
        add_depend=add_depend,
        default_project=project_from_cwd,
    )


@app.command(
    name="tangent",
    help=(
        "File a provisional Premise from captured fields rather than composed prose. "
        "Composes the body deterministically — a provisional banner, the operator's "
        "verbatim prompt, and the possibly-relevant context — and files it through the "
        "same create-plus-depend path as `file`, with Route fixed to check-in. "
        "Prints the new Premise's idReadable."
    ),
)
def tangent_command(
    project: Annotated[
        str,
        typer.Option(help="Project short name (BOB, PM, CORE, …) to file the tangent under"),
    ],
    summary: Annotated[str, typer.Option(help="One-line summary for the tangent Premise")],
    prompt: Annotated[str, typer.Option(help="The operator's original prompt, captured verbatim")],
    context: Annotated[
        str,
        typer.Option(
            help=(
                "Context from the conversation that might be relevant — observations "
                "only, not recommendations or proposed fixes"
            )
        ),
    ],
    dep: Annotated[
        list[str] | None,
        typer.Option(help="Depend-on Premise id; repeatable, one Depend edge per value"),
    ] = None,
) -> None:
    tangent_cli.tangent(
        project,
        summary,
        prompt,
        context,
        dep or [],
        create_premise=create_premise,
        add_depend=add_depend,
        default_project=project_from_cwd,
    )


@app.command(
    name="premise-claim",
    help="Transition a Premise to State=Active, Workflow=Claimed via the commands API.",
)
def premise_claim_command(
    premise: Annotated[str, typer.Argument(help="Premise id, e.g. BOB-26")],
) -> None:
    premise_cli.claim(premise, claim_premise=claim_premise)


@app.command(name="comment-add", help="Post a comment on a Premise.")
def comment_add_command(
    premise: Annotated[str, typer.Argument(help="Premise id, e.g. BOB-26")],
    body: Annotated[str, typer.Option(help="Comment body markdown")],
) -> None:
    premise_cli.comment_add(premise, body, add_comment=add_comment)


@app.command(name="depend-add", help="Add a Depend edge: source depends on target.")
def depend_add_command(
    source: Annotated[str, typer.Argument(help="Source Premise id (the dependent)")],
    target: Annotated[str, typer.Argument(help="Target Premise id (the prerequisite)")],
) -> None:
    link_cli.depend_add(source, target, add_depend=add_depend)


@app.command(name="depend-remove", help="Remove a Depend edge: source no longer depends on target.")
def depend_remove_command(
    source: Annotated[str, typer.Argument(help="Source Premise id (the dependent)")],
    target: Annotated[str, typer.Argument(help="Target Premise id (the prerequisite)")],
) -> None:
    link_cli.depend_remove(source, target, remove_depend=remove_depend)


def main() -> None:
    app()
