from __future__ import annotations

import sys
from typing import Annotated

import typer

from vaudeville_cue import assignment_context, component_register
from vaudeville_cue.checkpoint import run_checkpoint, run_digest

app = typer.Typer(
    name="vv-cue",
    help="Vaudeville Cue CLI: what happens inside a running Bob, the first-turn "
    "Brief and the intra-session lifecycle.",
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.callback()
def _callback() -> None:
    # Force Typer into multi-command mode so the facade's `vv <subcommand>`
    # dispatch keeps the subcommand name in argv. Without this, Typer
    # flattens a single-command app and the dispatch loses the subcommand.
    pass


@app.command(
    name="assignment-context",
    help=(
        "The /spawn downstream. Fetches the assignment and renders its per-Route "
        "first-turn body to stdout. Pickability gating (Type, Workflow, Route, "
        "deps) belongs to `vv spawn-preflight` upstream."
    ),
)
def assignment_context_command(
    assignment: Annotated[str, typer.Argument(help="Assignment id, e.g. BOB-26")],
) -> None:
    assignment_context.main(assignment)


@app.command(
    name="component-register",
    help=(
        "Print the Component register: one line per Component in the tenant's federation — "
        "`- PREFIX (name): description` — read live from the host config, in prefix order. A "
        "computed view over core's config, never a curated list."
    ),
)
def component_register_command() -> None:
    component_register.main()


@app.command(
    name="digest",
    help=(
        "Print the Digest: the operator's verbatim turns, extracted from this "
        "session's transcript and line-located back into it, cumulative across this "
        "Bob's checkpoints. Recovers turns relayed through a tmp file as well as "
        "typed ones. Self-resolves the transcript from the worktree and "
        "$CLAUDE_CODE_SESSION_ID; writes nothing. Read it before authoring the "
        "Carryover: curate against the operator's actual words, not your "
        "recollection of them."
    ),
)
def digest_command() -> None:
    run_digest()


@app.command(
    name="checkpoint",
    help=(
        "Shed this Bob's conversation and resume the same work, born grounded by the "
        "Resume Brief. Reads the Carryover on stdin, accumulates the Digest, composes "
        "the Resume Brief, persists all three at the worktree root, then launches a "
        "detached `reseat` (bobiverse's primitive) that replaces this pane's "
        "session in place, seeding the fresh session with the Brief as its first turn. "
        "Refuses before the irreversible reseat when the Carryover is empty or the "
        "session transcript cannot be resolved."
    ),
)
def checkpoint_command(
    worktree_name: Annotated[
        str | None,
        typer.Option(help="Worktree whose pane to drive (default: the one cwd is inside)."),
    ] = None,
) -> None:
    run_checkpoint(worktree_name, carryover=sys.stdin.read())


def main() -> None:
    app()
