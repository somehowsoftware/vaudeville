from __future__ import annotations

import sys
from typing import Annotated

import typer

from vaudeville_cue import assignment_context, checkpoint_drive
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
        "Shed this Bob's conversation and resume the same work, grounded by an "
        "injected Resume Brief. Reads the Carryover on stdin, accumulates the Digest, "
        "composes the Resume Brief, persists all three at the worktree root, then "
        "launches a detached drive that sends /clear (never /compact: the clear is "
        "the token reduction, where compact re-hydrates), waits for the cleared "
        "session to appear, and injects the Brief as its first turn. Refuses before "
        "the irreversible clear when --resume names an undeployed skill, the "
        "Carryover is empty, or the session transcript cannot be resolved."
    ),
)
def checkpoint_command(
    resume: Annotated[
        str | None,
        typer.Option(
            "--resume",
            help="Continuation skill the Resume Brief closes into, without the leading "
            "slash (e.g. _continue_full_process). Omit for a bare checkpoint: the "
            "Brief closes with the work the Carryover names.",
        ),
    ] = None,
    worktree_name: Annotated[
        str | None,
        typer.Option(help="Worktree whose pane to drive (default: the one cwd is inside)."),
    ] = None,
) -> None:
    run_checkpoint(resume, worktree_name, carryover=sys.stdin.read())


@app.command(
    name="checkpoint-drive",
    hidden=True,
    help=(
        "Internal: the detached Checkpoint driver. `vv checkpoint` re-invokes this "
        "entry point (rather than `python -m`) so the driver resolves the package the "
        "same way the running command did: importable under the shiv zipapp, not only "
        "under a site-packages install. Not for direct use."
    ),
)
def checkpoint_drive_command(
    pane: Annotated[str, typer.Argument()],
    transcript_dir: Annotated[str, typer.Argument()],
    brief: Annotated[str, typer.Argument()],
) -> None:
    checkpoint_drive.main([pane, transcript_dir, brief])


def main() -> None:
    app()
