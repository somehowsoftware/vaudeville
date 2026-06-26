from __future__ import annotations

from typing import Annotated

import typer
from vaudeville_core import (
    PERMITTED_ROUTES,
    add_comment,
    add_depend,
    apply_bookkeeping,
    claim_assignment,
    component_from_cwd,
    create_assignment,
    find_assignments,
    get_assignment,
    list_components,
    remove_depend,
    repo_descriptions,
    sign_off,
)

from vaudeville_coordinator import (
    assignment_cli,
    available,
    command_cli,
    file_cli,
    link_cli,
    resolve_cli,
    return_cli,
    sign_off_cli,
    tangent_cli,
    unblocked_cli,
)
from vaudeville_coordinator.concern_classifier import classify_concern

app = typer.Typer(
    name="vv-coordinator",
    help="Vaudeville Coordinator CLI: author Assignments and move them through their lifecycle.",
    context_settings={"help_option_names": ["-h", "--help"]},
)

ComponentOption = Annotated[
    str | None,
    typer.Option(
        "--project",
        help=(
            "Component short name (BOB, PM, CORE, …). Defaults to the Component "
            "whose main clone contains cwd."
        ),
    ),
]

# Route and Type help read vaudeville-core's published (kind → routes) constraint so the
# CLI surface cannot drift from what the authoring gate actually enforces.
_ROUTE_BY_KIND = "; ".join(
    f"{kind} {'/'.join(sorted(routes)) or '(none)'}" for kind, routes in PERMITTED_ROUTES.items()
)
RouteOption = Annotated[str, typer.Option(help=f"Route, by --type: {_ROUTE_BY_KIND}")]
TypeOption = Annotated[
    str,
    typer.Option("--type", help=f"Type: {', '.join(PERMITTED_ROUTES)}. Default: Premise."),
]


@app.command(name="available", help="List Assignments ready to pick up in the cwd Component.")
def available_command(component: ComponentOption = None) -> None:
    available.main(component, find=find_assignments, list_all=list_components)


@app.command(
    name="resolve",
    help=(
        "Apply a resolving close (delivered or abandoned) to an Assignment: write the State "
        "transition and a reason comment. Does not tear down the worktree."
    ),
)
def resolve_command(
    disposition: Annotated[str, typer.Argument(help="delivered or abandoned")],
    assignment: Annotated[str, typer.Argument(help="Assignment id, e.g. BOB-26")],
    reason: Annotated[str, typer.Option(help="Reason body (the disposition's header is added)")],
) -> None:
    resolve_cli.resolve_assignment(disposition, assignment, reason, bookkeep=apply_bookkeeping)


@app.command(
    name="return",
    help=(
        "Return an Assignment to the pickup pool (Active/Returned + return note), unassigned. "
        "Does not tear down the worktree."
    ),
)
def return_command(
    assignment: Annotated[str, typer.Argument(help="Assignment id, e.g. BOB-26")],
    reason: Annotated[str, typer.Option(help="Return note body (header is added)")],
) -> None:
    return_cli.return_assignment(assignment, reason, bookkeep=apply_bookkeeping)


@app.command(
    name="sign-off",
    help=(
        "Sign off a Command or Manual: the operator's go-ahead that admits it to "
        "the pickup pool. Premise and Direction are pickable without it."
    ),
)
def sign_off_command(
    assignment: Annotated[str, typer.Argument(help="Assignment id, e.g. PM-26")],
) -> None:
    sign_off_cli.sign_off(assignment, sign_off=sign_off)


@app.command(
    name="unblocked",
    help=(
        "Print the newly-pickable Depend peers of a RESOLVED Assignment, one id per line. "
        "Refuses if the Assignment is not yet resolved."
    ),
)
def unblocked_command(
    assignment: Annotated[str, typer.Argument(help="Assignment id, e.g. BOB-26")],
) -> None:
    unblocked_cli.show(assignment, fetch=get_assignment)


@app.command(
    name="unblocked-sign-off",
    help=(
        "Print the Command and Manual peers a RESOLVED Assignment freed that await the "
        "operator's sign-off, one id per line. Refuses if the Assignment is not yet resolved. "
        "Separate from `unblocked` so that query's auto-pickup output still feeds a spawn loop "
        "untouched; these are surfaced for a sign-off decision, not spawned."
    ),
)
def unblocked_sign_off_command(
    assignment: Annotated[str, typer.Argument(help="Assignment id, e.g. BOB-26")],
) -> None:
    unblocked_cli.show_awaiting_sign_off(assignment, fetch=get_assignment)


@app.command(
    name="assignment-show",
    help="Print the Assignment's summary, custom fields, and Depend peers (one field per line).",
)
def assignment_show_command(
    assignment: Annotated[str, typer.Argument(help="Assignment id, e.g. BOB-26")],
) -> None:
    assignment_cli.show(assignment, fetch=get_assignment)


@app.command(
    name="assignment-create",
    help="Create an Assignment in the cwd Component (or --project) and print its idReadable.",
)
def assignment_create_command(
    summary: Annotated[str, typer.Option(help="One-line summary")],
    description: Annotated[str, typer.Option(help="Body markdown")],
    route: RouteOption = "",
    type_name: TypeOption = "Premise",
    workflow: Annotated[
        str,
        typer.Option(help="Workflow: Submitted, Returned, Claimed. Default: Submitted."),
    ] = "Submitted",
    component: ComponentOption = None,
) -> None:
    assignment_cli.create(
        summary,
        description,
        route,
        type_name,
        workflow,
        component,
        create_assignment=create_assignment,
        default_component=component_from_cwd,
    )


@app.command(
    name="file",
    help=(
        "Author a Premise and attach its Depend edges in one call. "
        "Prints the new Assignment's idReadable on success."
    ),
)
def file_command(
    summary: Annotated[str, typer.Option(help="One-line summary")],
    description: Annotated[str, typer.Option(help="Body markdown")],
    route: RouteOption = "",
    dep: Annotated[
        list[str] | None,
        typer.Option(help="Depend-on Assignment id; repeatable, one Depend edge per value"),
    ] = None,
    type_name: TypeOption = "Premise",
    workflow: Annotated[
        str,
        typer.Option(help="Workflow: Submitted, Returned, Claimed. Default: Submitted."),
    ] = "Submitted",
    component: ComponentOption = None,
) -> None:
    file_cli.file(
        summary,
        description,
        route,
        dep or [],
        type_name,
        workflow,
        component,
        create_assignment=create_assignment,
        add_depend=add_depend,
        default_component=component_from_cwd,
    )


@app.command(
    name="tangent",
    help=(
        "File a provisional Premise from captured fields rather than composed prose. "
        "Composes the body deterministically (a provisional banner, the operator's "
        "verbatim prompt, and the possibly-relevant context) and files it through the "
        "same create-plus-depend path as `file`, with Route fixed to check-in. "
        "Prints the new Assignment's idReadable."
    ),
)
def tangent_command(
    summary: Annotated[str, typer.Option(help="One-line summary for the tangent Premise")],
    prompt: Annotated[str, typer.Option(help="The operator's original prompt, captured verbatim")],
    context: Annotated[
        str,
        typer.Option(
            help=(
                "Context from the conversation that might be relevant: observations "
                "only, not recommendations or proposed fixes"
            )
        ),
    ],
    component: Annotated[
        str | None,
        typer.Option(
            "--project",
            help=(
                "Override the classified Component: file the tangent under this prefix "
                "instead of letting the classifier decide from the concern's subject"
            ),
        ),
    ] = None,
    dep: Annotated[
        list[str] | None,
        typer.Option(help="Depend-on Assignment id; repeatable, one Depend edge per value"),
    ] = None,
) -> None:
    tangent_cli.tangent(
        component,
        summary,
        prompt,
        context,
        dep or [],
        classify_concern=classify_concern,
        repo_descriptions=repo_descriptions,
        create_assignment=create_assignment,
        add_depend=add_depend,
    )


@app.command(
    name="command",
    help=(
        "File a Command (the operator's settled directive) through the same "
        "create-plus-depend path as `file`, with Type Command and Route check-in "
        "(default) or direct. Does not spawn: filing and running stay decoupled. "
        "Prints the new Command's idReadable."
    ),
)
def command_command(
    summary: Annotated[str, typer.Option(help="One-line directive title")],
    description: Annotated[
        str,
        typer.Option(help="Body markdown: the ordered steps and authorization gates"),
    ],
    route: Annotated[
        str,
        typer.Option(help="Route: check-in (default) or direct"),
    ] = "check-in",
    dep: Annotated[
        list[str] | None,
        typer.Option(help="Depend-on Assignment id; repeatable, one Depend edge per value"),
    ] = None,
    component: ComponentOption = None,
) -> None:
    command_cli.file_command(
        summary,
        description,
        route,
        dep or [],
        component,
        create_assignment=create_assignment,
        add_depend=add_depend,
        default_component=component_from_cwd,
    )


@app.command(
    name="assignment-claim",
    help="Transition an Assignment to State=Active, Workflow=Claimed via the commands API.",
)
def assignment_claim_command(
    assignment: Annotated[str, typer.Argument(help="Assignment id, e.g. BOB-26")],
) -> None:
    assignment_cli.claim(assignment, claim_assignment=claim_assignment)


@app.command(name="comment-add", help="Post a comment on an Assignment.")
def comment_add_command(
    assignment: Annotated[str, typer.Argument(help="Assignment id, e.g. BOB-26")],
    body: Annotated[str, typer.Option(help="Comment body markdown")],
) -> None:
    assignment_cli.comment_add(assignment, body, add_comment=add_comment)


@app.command(name="depend-add", help="Add a Depend edge: source depends on target.")
def depend_add_command(
    source: Annotated[str, typer.Argument(help="Source Assignment id (the dependent)")],
    target: Annotated[str, typer.Argument(help="Target Assignment id (the prerequisite)")],
) -> None:
    link_cli.depend_add(source, target, add_depend=add_depend)


@app.command(name="depend-remove", help="Remove a Depend edge: source no longer depends on target.")
def depend_remove_command(
    source: Annotated[str, typer.Argument(help="Source Assignment id (the dependent)")],
    target: Annotated[str, typer.Argument(help="Target Assignment id (the prerequisite)")],
) -> None:
    link_cli.depend_remove(source, target, remove_depend=remove_depend)


def main() -> None:
    app()
