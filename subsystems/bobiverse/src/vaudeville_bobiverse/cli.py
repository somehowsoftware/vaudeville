from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated

import typer
from vaudeville_core import list_projects, project_from_cwd

from vaudeville_bobiverse import checkpoint_drive, claude_projects, foundation, foundation_verify
from vaudeville_bobiverse import prime as prime_mod
from vaudeville_bobiverse import unclaim as unclaim_mod
from vaudeville_bobiverse.checkpoint import run_checkpoint, run_digest
from vaudeville_bobiverse.data_dir import data_dir
from vaudeville_bobiverse.prime_fanout import (
    MAX_PRIME_CONCURRENCY,
    fork_every_foundation,
    prime_report,
)
from vaudeville_bobiverse.spawn import launcher, orchestrate, preflight, target_repo
from vaudeville_bobiverse.teardown import run as run_teardown

PRIME_LOG_DIR = Path("/tmp")

app = typer.Typer(
    name="vv-bob",
    help="Vaudeville Bobiverse CLI: Bob session lifecycle and host environment resolution.",
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.command(
    name="teardown",
    help=(
        "Tear down a worktree: archive the worktree body and the Bob's Claude "
        "transcript, then remove the git worktree and kill its pane. No tracker "
        "writes — sequence `vv resolve`/`vv return`/`vv unclaim` first if the "
        "Premise needs a transition."
    ),
)
def teardown_command(
    worktree_name: Annotated[
        str | None,
        typer.Option(help="Worktree to tear down (default: the one cwd is inside)."),
    ] = None,
) -> None:
    run_teardown(worktree_name)


@app.command(
    name="digest",
    help=(
        "Print the Digest — the operator's verbatim turns, extracted from this "
        "session's transcript and line-located back into it, cumulative across this "
        "Bob's checkpoints. Recovers turns relayed through a tmp file as well as "
        "typed ones. Self-resolves the transcript from the worktree and "
        "$CLAUDE_CODE_SESSION_ID; writes nothing. Read it before authoring the "
        "Carryover — curate against the operator's actual words, not your "
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
            "slash (e.g. _continue_materialize). Omit for a bare checkpoint: the "
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
        "same way the running command did — importable under the shiv zipapp, not only "
        "under a site-packages install. Not for direct use."
    ),
)
def checkpoint_drive_command(
    pane: Annotated[str, typer.Argument()],
    transcript_dir: Annotated[str, typer.Argument()],
    brief: Annotated[str, typer.Argument()],
) -> None:
    checkpoint_drive.main([pane, transcript_dir, brief])


@app.command(
    name="unclaim",
    help=(
        "Re-pool a Premise with no record it was claimed: State=Ready, "
        "Workflow=Submitted, Assignee cleared, no comment. The bobiverse-local "
        "sibling of `vv resolve`/`vv return`; does not tear down the worktree."
    ),
)
def unclaim_command(
    premise: Annotated[str, typer.Argument(help="Premise id, e.g. BOB-26")],
) -> None:
    unclaim_mod.unclaim_premise(premise)


@app.command(
    name="current-project",
    help="Print the project short name whose main clone contains cwd.",
)
def current_project_command() -> None:
    print(project_from_cwd())


@app.command(
    name="spawn-preflight",
    help=(
        "Refuse `/spawn` on Premises that fail the same predicate stack "
        "`/available` uses (project, Workflow, Type, deps). "
        "Silent and exit 0 on pass; one-line refusal on stderr and exit 1 on fail."
    ),
)
def spawn_preflight_command(
    premise: Annotated[str, typer.Argument(help="Premise id, e.g. BOB-26")],
) -> None:
    preflight.main(premise)


@app.command(
    name="spawn-launcher",
    help=(
        "Run the configured /spawn downstream, write the launcher file, "
        "and print its path. Skill bash captures stdout and passes it to "
        "`workmux add --prompt-file`."
    ),
)
def spawn_launcher_command(
    premise: Annotated[str, typer.Argument(help="Premise id, e.g. BOB-26")],
) -> None:
    launcher.main(premise)


@app.command(
    name="spawn",
    help=(
        "Run the full /spawn pipeline: preflight, resolve target repo, generate "
        "launcher, invoke `workmux add` from the target repo. Composes the "
        "spawn-* subcommands so /delegate can spawn with one call. Before launching "
        "it resets every managed clone to a clean origin/main — discarding uncommitted "
        "changes in those clones — and records the new worktree's folder-trust in the "
        "Claude config ($CLAUDE_CONFIG_DIR, default ~/.claude)."
    ),
)
def spawn_command(
    premise: Annotated[str, typer.Argument(help="Premise id, e.g. BOB-26")],
) -> None:
    orchestrate.spawn(premise)


@app.command(
    name="spawn-target-repo",
    help=(
        "Resolve the absolute repo path /spawn should cd into for a given "
        "Premise id, using the repo_path field of ~/.vaudeville/projects.toml. "
        "Prints the path on stdout; exits non-zero with a stderr message on "
        "unknown prefix or malformed id."
    ),
)
def spawn_target_repo_command(
    premise: Annotated[str, typer.Argument(help="Premise id, e.g. BOB-26")],
) -> None:
    target_repo.main(premise)


@app.command(
    name="prime",
    help=(
        "Prime one Managed Repository's Foundation, or all of them if no prefix is "
        "given. Drives the two shared turns (Doctrine, project-docs) once into a "
        "Bedrock, then forks a Foundation per Managed Repository — each fork drives "
        "only the repo turn in that repo's main clone and records the new session id. "
        "Writes persist to two roots, both defaulting to the host: the data dir "
        "($VV_DATA_DIR, default ~/.vaudeville) holds foundations.toml and the Foundation "
        "store under foundations/ that later spawns fork from; the Claude config dir "
        "($CLAUDE_CONFIG_DIR, default ~/.claude) holds the primed session transcripts "
        "under projects/. Re-priming refreshes durable host state, not throwaway scratch, "
        "unless those env vars redirect the roots to a staged scaffold (the rehearse path). "
        "In the multi-prefix path the Bedrock and each fork stream to "
        f"{PRIME_LOG_DIR}/prime-<bedrock|prefix>.log so concurrent runs don't interleave."
    ),
)
def prime_command(
    prefix: Annotated[
        str | None,
        typer.Argument(help="Project prefix (e.g. BOB). Omit to prime every Managed Repository."),
    ] = None,
) -> None:
    data_files_root = data_dir()
    projects_root = claude_projects.projects_root()
    if prefix is not None:
        prime_mod.main(prefix, data_files_root, projects_root)
        return

    prefixes = list_projects()
    if not prefixes:
        print("No projects in ~/.vaudeville/projects.toml; nothing to prime.")
        return
    bedrock_session_id = prime_mod.prime_bedrock(
        data_files_root=data_files_root, log_path=_log_path_for("bedrock")
    )
    stdout_lines, stderr_lines, exit_code = prime_report(
        fork_every_foundation(
            prefixes,
            lambda fork_prefix: prime_mod.fork_foundation(
                bedrock_session_id,
                fork_prefix,
                data_files_root=data_files_root,
                projects_root=projects_root,
                log_path=_log_path_for(fork_prefix),
            ),
            _log_path_for,
            max_concurrency=MAX_PRIME_CONCURRENCY,
        )
    )
    for line in stdout_lines:
        print(line)
    for line in stderr_lines:
        print(line, file=sys.stderr)
    if exit_code != 0:
        sys.exit(exit_code)


def _log_path_for(prefix: str) -> Path:
    return PRIME_LOG_DIR / f"prime-{prefix.lower()}.log"


@app.command(
    name="foundations-verify",
    help=(
        "Verify every recorded Foundation is durable: that each session id in "
        "foundations.toml has its transcript present in the path-independent Foundation "
        "store (~/.vaudeville/foundations/), not stranded in a smoke's scratch. Exit 0 if "
        "all are durable; one-line report on stderr and exit 1 naming the stranded "
        "Foundations otherwise."
    ),
)
def foundations_verify_command() -> None:
    foundation_verify.verify(
        foundation.all_foundations(data_files_root=data_dir()),
        foundation.transcript_store(data_files_root=data_dir()),
    )


def main() -> None:
    app()
