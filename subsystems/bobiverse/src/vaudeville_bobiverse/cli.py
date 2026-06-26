from __future__ import annotations

import sys
from typing import Annotated

import typer
from vaudeville_core import component_from_cwd, list_components

from vaudeville_bobiverse import bob as bob_mod
from vaudeville_bobiverse import claude_projects, foundation, foundation_verify
from vaudeville_bobiverse import prime as prime_mod
from vaudeville_bobiverse import unclaim as unclaim_mod
from vaudeville_bobiverse.data_dir import data_dir
from vaudeville_bobiverse.prime_fanout import prime_report
from vaudeville_bobiverse.spawn import launcher, orchestrate, preflight, target_repo
from vaudeville_bobiverse.teardown import run as run_teardown

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
        "writes: sequence `vv resolve`/`vv return`/`vv unclaim` first if the "
        "Assignment needs a transition."
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
    name="unclaim",
    help=(
        "Re-pool an Assignment with no record it was claimed: State=Ready, "
        "Workflow=Submitted, Assignee cleared, no comment. The bobiverse-local "
        "sibling of `vv resolve`/`vv return`; does not tear down the worktree."
    ),
)
def unclaim_command(
    assignment: Annotated[str, typer.Argument(help="Assignment id, e.g. BOB-26")],
) -> None:
    unclaim_mod.unclaim_assignment(assignment)


@app.command(
    name="current-project",
    help="Print the Component short name whose main clone contains cwd.",
)
def current_project_command() -> None:
    print(component_from_cwd())


@app.command(
    name="spawn-preflight",
    help=(
        "Refuse `/spawn` on Assignments that fail the same predicate stack "
        "`/available` uses (Component, Workflow, Type, deps). "
        "Silent and exit 0 on pass; one-line refusal on stderr and exit 1 on fail."
    ),
)
def spawn_preflight_command(
    assignment: Annotated[str, typer.Argument(help="Assignment id, e.g. BOB-26")],
) -> None:
    preflight.main(assignment)


@app.command(
    name="spawn-launcher",
    help=(
        "Run the configured /spawn downstream, write the launcher file, "
        "and print its path. Skill bash captures stdout and passes it to "
        "`workmux add --prompt-file`."
    ),
)
def spawn_launcher_command(
    assignment: Annotated[str, typer.Argument(help="Assignment id, e.g. BOB-26")],
) -> None:
    launcher.main(assignment)


@app.command(
    name="spawn",
    help=(
        "Run the full /spawn pipeline: preflight, resolve target repo, generate "
        "launcher, invoke `workmux add` from the target repo. Composes the "
        "spawn-* subcommands so /file --spawn can spawn with one call. Before launching "
        "it resets every managed clone to a clean origin/main (discarding uncommitted "
        "changes in those clones) and records the new worktree's folder-trust in the "
        "Claude config ($CLAUDE_CONFIG_DIR, default ~/.claude)."
    ),
)
def spawn_command(
    assignment: Annotated[str, typer.Argument(help="Assignment id, e.g. BOB-26")],
) -> None:
    orchestrate.spawn(assignment)


@app.command(
    name="bob",
    help=(
        "Fork an Assignment-less ad-hoc Bob into a Component's primed "
        "Foundation. Like /spawn minus the backlog: no preflight and no Brief, just "
        "an orienting note telling the Bob to wait for the operator's first "
        "instruction. Resets every managed clone to a clean origin/main and records "
        "the new worktree's folder-trust, exactly as spawn does. Refuses with exit 2 "
        "when no Foundation exists for the prefix."
    ),
)
def bob_command(
    prefix: Annotated[str, typer.Argument(help="Component prefix (e.g. BOB)")],
) -> None:
    bob_mod.bob(prefix)


@app.command(
    name="spawn-target-repo",
    help=(
        "Resolve the absolute repo path /spawn should cd into for a given "
        "Assignment id, using the repo_path field of ~/.vaudeville/projects.toml. "
        "Prints the path on stdout; exits non-zero with a stderr message on "
        "unknown prefix or malformed id."
    ),
)
def spawn_target_repo_command(
    assignment: Annotated[str, typer.Argument(help="Assignment id, e.g. BOB-26")],
) -> None:
    target_repo.main(assignment)


@app.command(
    name="prime",
    help=(
        "Prime one Component's Foundation, or all of them if no prefix is "
        "given. Drives the two shared turns (Doctrine, project-docs) once into a "
        "Bedrock, then forks a Foundation per Component: each fork drives "
        "only the repo turn in that repo's main clone and records the new session id. "
        "Writes persist to two roots, both defaulting to the host: the data dir "
        "($VV_DATA_DIR, default ~/.vaudeville) holds foundations.toml and the Foundation "
        "store under foundations/ that later spawns fork from; the Claude config dir "
        "($CLAUDE_CONFIG_DIR, default ~/.claude) holds the primed session transcripts "
        "under projects/. Re-priming refreshes durable host state, not throwaway scratch, "
        "unless those env vars redirect the roots to a staged scaffold (the rehearse path). "
        "In the multi-prefix path the Bedrock and each fork stream to "
        f"{prime_mod.PRIME_LOG_DIR}/prime-<bedrock|prefix>.log so concurrent runs don't interleave."
    ),
)
def prime_command(
    prefix: Annotated[
        str | None,
        typer.Argument(help="Component prefix (e.g. BOB). Omit to prime every Component."),
    ] = None,
) -> None:
    data_files_root = data_dir()
    projects_root = claude_projects.projects_root()
    if prefix is not None:
        prime_mod.main(prefix, data_files_root, projects_root)
        return

    prefixes = list_components()
    if not prefixes:
        print("No Components in ~/.vaudeville/projects.toml; nothing to prime.")
        return
    stdout_lines, stderr_lines, exit_code = prime_report(
        prime_mod.prime_all(prefixes, data_files_root=data_files_root, projects_root=projects_root)
    )
    for line in stdout_lines:
        print(line)
    for line in stderr_lines:
        print(line, file=sys.stderr)
    if exit_code != 0:
        sys.exit(exit_code)


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
