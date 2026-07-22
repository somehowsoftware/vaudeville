from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from vaudeville_core import component_from_name

from vaudeville_bobiverse import bob as bob_mod
from vaudeville_bobiverse import claude_projects
from vaudeville_bobiverse import components as components_mod
from vaudeville_bobiverse import enroll as enroll_mod
from vaudeville_bobiverse import prime as prime_mod
from vaudeville_bobiverse.config_origin import ConfigOriginUnrecorded, config_origin
from vaudeville_bobiverse.data_dir import data_dir
from vaudeville_bobiverse.spawn import orchestrate

USAGE_EXIT = 2
SPAWN_FAILED_EXIT = 1

app = typer.Typer(
    name="vaudeville-bob",
    help="Vaudeville operator commands.",
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.callback()
def operator() -> None:
    # Without a callback, Typer collapses a lone command into the program itself
    # and drops its name; this no-op forces group semantics so `spawn` stays a
    # named subcommand and `vaudeville spawn` composes through Ringmaster.
    ...


@app.command(
    name="spawn",
    help=(
        "Spawn a Bob on each given Assignment, in order. Accepts ids in any case and "
        "canonicalizes them. A failure on one id is reported to stderr and the run "
        "continues to the next; exits non-zero if any id failed."
    ),
)
def spawn_command(
    assignments: Annotated[
        list[str], typer.Argument(help="Assignment ids, e.g. BOB-197 BOB-198 (any case)")
    ],
    model: Annotated[
        str | None,
        typer.Option("--model", help="Model every spawned Bob runs on (default: opus)."),
    ] = None,
) -> None:
    failures = orchestrate.spawn_each(assignments, model)
    for failure in failures:
        typer.echo(f"Error spawning {failure.assignment_id}: {failure.reason}", err=True)
    if failures:
        raise typer.Exit(code=SPAWN_FAILED_EXIT)


@app.command(
    name="bob",
    help=(
        "Fork an Assignment-less ad-hoc Bob into a Component's primed "
        "Foundation. Accepts the Component's long or short name and "
        "resolves it to a prefix. A bare `bob` with no name is an error that "
        "lists the known names."
    ),
)
def bob_command(
    component: Annotated[
        str | None, typer.Argument(help="Component name, e.g. bobiverse or bob")
    ] = None,
    model: Annotated[
        str | None,
        typer.Option("--model", help="Model the ad-hoc Bob runs on (default: opus)."),
    ] = None,
) -> None:
    if component is None:
        typer.echo(
            components_mod.bare_bob_rejection(components_mod.registered_component_names()),
            err=True,
        )
        raise typer.Exit(code=USAGE_EXIT)
    bob_mod.bob(component_from_name(component), model)


def prime_rejection(component: str | None, every: bool) -> str | None:
    # Priming every Component is too broad to be the silent default, so a
    # bare `prime` is an error rather than an implicit `--all`; a name and `--all`
    # together name two scopes at once and are equally refused.
    if component is not None and every:
        return "Pass a Component name or --all, not both."
    if component is None and not every:
        return "Name a Component, or pass --all to prime every Component."
    return None


@app.command(
    name="prime",
    help=(
        "Refresh a Component's Foundation, or every Component's "
        "with --all. Accepts the Component's long or short name and "
        "resolves it to a prefix. A bare `prime` with neither a name nor --all is "
        "an error, and the two are mutually exclusive."
    ),
)
def prime_command(
    component: Annotated[
        str | None,
        typer.Argument(help="Component name, e.g. bobiverse or bob"),
    ] = None,
    every: Annotated[bool, typer.Option("--all", help="Prime every Component.")] = False,
) -> None:
    rejection = prime_rejection(component, every)
    if rejection is not None:
        typer.echo(rejection, err=True)
        raise typer.Exit(code=USAGE_EXIT)
    prefix = component_from_name(component) if component is not None else None
    prime_mod.prime_one_or_all(
        prefix, data_files_root=data_dir(), projects_root=claude_projects.projects_root()
    )


@app.command(
    name="enroll",
    help=(
        "Wire an existing repository into Vaudeville as a Component: provision its "
        "tracker project, register it in vaudeville.toml, and scaffold its documentary "
        "skeleton (a Context gets a stub spec and vocabulary; a Resource gets none). "
        "Admits a repo the tenant already built -- it never creates the repository or "
        "its CI, branch protection, or review rules. Accepts the prefix in any case. "
        "The Foundation is not built here: commit and push the scaffold, then run "
        "`vaudeville prime <prefix>`."
    ),
)
def enroll_command(
    prefix: Annotated[str, typer.Argument(help="Component prefix, e.g. WEB (any case)")],
    repo_path: Annotated[
        Path, typer.Option("--repo-path", help="Path to the existing repository to enroll.")
    ],
    name: Annotated[str, typer.Option("--name", help="Operator-facing long name.")],
    kind: Annotated[
        enroll_mod.ComponentKind,
        typer.Option("--kind", help="'context' (adjudicates a domain) or 'resource' (holds none)."),
    ],
    remote: Annotated[
        str | None,
        typer.Option("--remote", help="Canonical git remote (defaults to the repo's own origin)."),
    ] = None,
    short_name: Annotated[
        str | None, typer.Option("--short-name", help="Optional operator-facing short name.")
    ] = None,
    description: Annotated[
        str | None,
        typer.Option("--description", help="Optional one-sentence Component summary."),
    ] = None,
    config_dir: Annotated[
        Path | None,
        typer.Option(
            "--config-dir",
            help="The tenant's config repo, holding the register enroll writes to."
            " Defaults to the config dir this host was installed from.",
        ),
    ] = None,
) -> None:
    try:
        authored_config_dir = config_origin(config_dir)
    except ConfigOriginUnrecorded as unrecorded:
        typer.echo(str(unrecorded), err=True)
        raise typer.Exit(code=USAGE_EXIT) from unrecorded
    enroll_mod.enroll(
        prefix.upper(),
        repo_path=repo_path,
        name=name,
        kind=kind,
        remote=remote,
        short_name=short_name,
        description=description,
        authored_config_dir=authored_config_dir,
    )


def main() -> None:
    app()
