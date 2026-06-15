from __future__ import annotations

from typing import Annotated

import typer

from vaudeville_cue import premise_context

app = typer.Typer(
    name="vv-cue",
    help="Vaudeville Cue CLI: the launcher body for a freshly-spawned Bob's first turn.",
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.callback()
def _callback() -> None:
    # Force Typer into multi-command mode so the facade's `vv <subcommand>`
    # dispatch keeps the subcommand name in argv. Without this, Typer
    # flattens a single-command app and the dispatch loses the subcommand.
    pass


@app.command(
    name="premise-context",
    help=(
        "The /spawn downstream. Fetches the Premise and renders its per-Route "
        "first-turn body to stdout. Pickability gating (Type, Workflow, Route, "
        "deps) belongs to `vv spawn-preflight` upstream."
    ),
)
def premise_context_command(
    premise: Annotated[str, typer.Argument(help="Premise id, e.g. BOB-26")],
) -> None:
    premise_context.main(premise)


def main() -> None:
    app()
