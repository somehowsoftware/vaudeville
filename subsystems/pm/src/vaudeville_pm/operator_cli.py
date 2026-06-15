from __future__ import annotations

import typer
from vaudeville_core import find_premises, list_projects

from vaudeville_pm import pickable_table

app = typer.Typer(
    name="vaudeville-pm",
    help="Vaudeville operator commands contributed by vaudeville-pm.",
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
    help="Show every Pickable Premise across all Managed Repositories as one table.",
)
def pickable_command() -> None:
    pickable_table.main(find=find_premises, list_all=list_projects)


def main() -> None:
    app()
