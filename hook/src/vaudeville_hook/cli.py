from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer

from vaudeville_hook import stay

app = typer.Typer(
    name="vv-hook",
    help="Vaudeville Hook CLI: the screen — the outside sense that shows a running Bob, "
    "and the corpus it commits, what its own loop cannot form.",
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.callback()
def _callback() -> None:
    # Force Typer into multi-command mode so the facade's `vv <subcommand>` dispatch keeps
    # the subcommand name in argv. Without this, Typer flattens a single-command app and
    # the dispatch loses the subcommand.
    pass


@app.command(
    name="stay",
    help=(
        "Record a stay: your answer to a headroom nudge you have judged wrong. The gentle "
        "and active rungs stand down for the rest of this session, so you can hold the seam "
        "you are working toward rather than checkpoint at the screen's cadence. The "
        "aggressive and emergency rungs still fire — they are the backstop, and no stay "
        "moves them. A stay names no token ceiling: it dies with the session, and the "
        "checkpoint you are holding off is the thing that ends both, so there is no reset "
        "to remember and no trajectory to predict. Binds the stay to this session itself, "
        "and writes over a predecessor session's stay without reading it first."
    ),
)
def stay_command(
    reason: Annotated[
        str,
        typer.Argument(help="Why you are holding: the seam you mean to reach before you shed."),
    ],
    session_id: Annotated[
        Optional[str],
        typer.Option(envvar=stay.SESSION_ID_ENV, hidden=True),
    ] = None,
) -> None:
    try:
        confirmation = stay.record_stay(
            reason,
            stay_path=stay.stay_path_in(Path.cwd()),
            session_id=session_id,
        )
    except stay.StayRefused as refusal:
        typer.echo(str(refusal), err=True)
        raise typer.Exit(code=2) from refusal
    typer.echo(confirmation)


def main() -> None:
    app()
