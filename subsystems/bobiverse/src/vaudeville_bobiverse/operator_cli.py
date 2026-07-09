from __future__ import annotations

from collections.abc import Callable
from typing import Annotated

import typer
from vaudeville_core import component_from_name, list_components

from vaudeville_bobiverse import bob as bob_mod
from vaudeville_bobiverse import claude_projects
from vaudeville_bobiverse import prime as prime_mod
from vaudeville_bobiverse.data_dir import data_dir
from vaudeville_bobiverse.spawn import orchestrate

PRIME_USAGE_EXIT = 2
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


def canonical_assignment_id(assignment: str) -> str:
    # An Assignment id's namespace prefix is canonically uppercase, and `vv spawn`
    # rejects any other case. The operator types the id in whatever case is to
    # hand; canonicalizing here lets `vaudeville spawn bob-197` resolve the same
    # Assignment as BOB-197 without widening the strict machine surface.
    return assignment.upper()


def spawn_each(assignment_ids: list[str], spawn_one: Callable[[str], None]) -> bool:
    # Serial for legible per-id reporting, not for safety: each spawn cuts from an
    # immutable base commit it resolves for itself, so concurrent spawns share no
    # mutable state to race on. The downstream gates exit on failure without reliably
    # naming the id, so this loop names it: on a SystemExit the gate's cause is already
    # on stderr and only the exit code is left to add; an ordinary exception has not
    # been printed at all.
    any_failed = False
    for assignment_id in assignment_ids:
        try:
            spawn_one(assignment_id)
        except SystemExit as spawn_exit:
            typer.echo(
                f"Error spawning {assignment_id}: exited with status {spawn_exit.code}; "
                "continuing with the rest.",
                err=True,
            )
            any_failed = True
        except Exception as error:
            typer.echo(f"Error spawning {assignment_id}: {error}", err=True)
            any_failed = True
    return any_failed


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
) -> None:
    if spawn_each([canonical_assignment_id(a) for a in assignments], orchestrate.spawn):
        raise typer.Exit(code=SPAWN_FAILED_EXIT)


@app.command(
    name="bob",
    help=(
        "Fork an Assignment-less ad-hoc Bob into a Component's primed "
        "Foundation. Accepts the Component's long or short name and "
        "resolves it to a prefix."
    ),
)
def bob_command(
    component: Annotated[str, typer.Argument(help="Component name, e.g. bobiverse or bob")],
) -> None:
    bob_mod.bob(component_from_name(component))


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
        raise typer.Exit(code=PRIME_USAGE_EXIT)
    if component is not None:
        prime_mod.main(component_from_name(component), data_dir(), claude_projects.projects_root())
        return
    prime_mod.main_all(list_components(), data_dir(), claude_projects.projects_root())


def main() -> None:
    app()
