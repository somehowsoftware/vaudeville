from __future__ import annotations

import sys
from typing import Annotated

import typer

from vaudeville_cue import assignment_context, parlay_record, parlay_watch
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
        "Shed this Bob's conversation and resume the same work, born grounded by the "
        "Resume Brief. Reads the Carryover on stdin, accumulates the Digest, composes "
        "the Resume Brief, persists all three at the worktree root, then launches a "
        "detached `reseat` (bobiverse's primitive) that replaces this pane's "
        "session in place, seeding the fresh session with the Brief as its first turn. "
        "Refuses before the irreversible reseat when --resume names an undeployed "
        "skill, the Carryover is empty, or the session transcript cannot be resolved."
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
    name="parlay-watch",
    help=(
        "Sense one PR for a convergence round and report only what the judge needs to act: the "
        "convergence verdict, how many new reviewer comments arrived (written verbatim to a file "
        "for the digest's discarded context, never echoed here), CI status with a handle to its "
        "raw log, mergeability, the reviewer's disposition, and the running round count, advanced "
        "whenever the PR head has moved since the last sense. Waits for Codex to rule on the head, "
        "up to "
        "--interval per call, before reporting; once the wait for a review exhausts the loop's "
        "patience a settled PR converges on the reviewer's silence. The raw CI log and the full "
        "comment history stay out of the judge's context by construction."
    ),
)
def parlay_watch_command(
    pr: Annotated[int, typer.Argument(help="PR number to converge.")],
    repo: Annotated[
        str | None,
        typer.Option(help="owner/repo of the PR (default: the current repository)."),
    ] = None,
    interval: Annotated[
        float, typer.Option(help="Upper bound, in seconds, on a single call's wait for Codex.")
    ] = 270.0,
    max_iterations: Annotated[
        int,
        typer.Option(help="Pass cap; the summary reports stop:yes once the loop reaches it."),
    ] = 20,
) -> None:
    parlay_watch.run_watch(pr, repo, interval, max_iterations)


@app.command(
    name="parlay-record",
    help=(
        "Dispose of one reviewer comment: post the disposition reply to it (what changed and why "
        "the underlying problem is gone, or the reasoning for changing no code) and clear it from "
        "the open queue, in one act so the reply can never be dropped. The reply threads under an "
        "inline review comment; a conversation comment or a review body gets a new PR comment. The "
        "escalation round count is sensed by parlay-watch from the PR head, not asserted here."
    ),
)
def parlay_record_command(
    pr: Annotated[int, typer.Argument(help="PR number being converged.")],
    comment_id: Annotated[int, typer.Argument(help="The reviewer comment id being disposed of.")],
    reply: Annotated[str, typer.Option(help="The disposition reply posted to the comment.")],
    repo: Annotated[
        str | None,
        typer.Option(help="owner/repo of the PR (default: the current repository)."),
    ] = None,
) -> None:
    parlay_record.run_record(pr, repo, comment_id, reply)


@app.command(
    name="parlay-begin",
    help=(
        "Bring a PR's head under parlay watch the moment it is opened, stamping the head-currency "
        "clock from the system clock now. Run by _tender right after the PR is created, so a fast "
        "Codex sign-off arriving before the first post-checkpoint sense is judged against a clock "
        "already running, not one that starts after it."
    ),
)
def parlay_begin_command(
    pr: Annotated[int, typer.Argument(help="PR number just opened.")],
    repo: Annotated[
        str | None,
        typer.Option(help="owner/repo of the PR (default: the current repository)."),
    ] = None,
) -> None:
    parlay_record.run_begin(pr, repo)


@app.command(
    name="parlay-waive",
    help=(
        "Lift a tripped three-round escalation on the operator's authority, so the convergence "
        "loop resumes past a stop the operator has judged not a fatal misframing. The round "
        "count is left standing, not zeroed, so a later third code-changing round past the "
        "waiver escalates again — a second trip is a louder alarm, not a fresh start."
    ),
)
def parlay_waive_command(
    pr: Annotated[int, typer.Argument(help="PR number whose escalation to waive.")],
    repo: Annotated[
        str | None,
        typer.Option(help="owner/repo of the PR (default: the current repository)."),
    ] = None,
) -> None:
    parlay_record.run_waive(pr, repo)


def main() -> None:
    app()
