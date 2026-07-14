from __future__ import annotations

import typer
from vaudeville_core import find_assignments, list_components

from vaudeville_coordinator import pickable_table

app = typer.Typer(
    name="vaudeville-coordinator",
    help="Vaudeville operator commands.",
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.callback()
def operator() -> None:
    # Without a callback, Typer collapses a lone command into the program itself
    # and drops its name; this no-op forces group semantics so `pickable` stays a
    # named subcommand and `vaudeville pickable` composes through Ringmaster.
    ...


@app.command(
    name="pickable",
    help="Show every Pickable Assignment across all Components as one table.",
)
def pickable_command() -> None:
    pickable_table.main(find=find_assignments, list_all=list_components)


def main() -> None:
    app()
