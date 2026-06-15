from __future__ import annotations

from typing import Annotated

import typer

from vaudeville_bobiverse.spawn import orchestrate

app = typer.Typer(
    name="vaudeville-bob",
    help="Vaudeville operator commands contributed by bobiverse.",
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.callback()
def operator() -> None:
    # Without a callback, Typer collapses a lone command into the program itself
    # and drops its name; this no-op forces group semantics so `spawn` stays a
    # named subcommand and `vaudeville spawn` composes through Ringmaster.
    ...


def canonical_premise_id(premise: str) -> str:
    # A Premise id's namespace prefix is canonically uppercase, and `vv spawn`
    # rejects any other case. The operator types the id in whatever case is to
    # hand; canonicalizing here lets `vaudeville spawn bob-197` resolve the same
    # Premise as BOB-197 without widening the strict machine surface.
    return premise.upper()


@app.command(
    name="spawn",
    help=(
        "Spawn a Bob on an existing Premise. Accepts the Premise id in any case, "
        "canonicalizes it, and delegates to the same spawn pipeline as `vv spawn`."
    ),
)
def spawn_command(
    premise: Annotated[str, typer.Argument(help="Premise id, e.g. BOB-197 (any case)")],
) -> None:
    orchestrate.spawn(canonical_premise_id(premise))


def main() -> None:
    app()
