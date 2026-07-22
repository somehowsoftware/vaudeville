from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path

from vaudeville_core import component_from_assignment_id, get_assignment

from vaudeville_bobiverse import claude_projects
from vaudeville_bobiverse.data_dir import data_dir
from vaudeville_bobiverse.spawn import agent, clearing, launcher, preflight, standup, trust
from vaudeville_bobiverse.spawn.refusal import Refusal, refuse, refuse_or_clear


def worktree_name(assignment_id: str) -> str:
    prefix = component_from_assignment_id(assignment_id)
    _, _, number = assignment_id.partition("-")
    return f"{prefix.lower()}-{number}"


def orchestrate(
    assignment_id: str,
    data_files_root: Path,
    projects_root: Path,
    claude_config_file: Path,
    model: str | None = None,
) -> None:
    prefix = component_from_assignment_id(assignment_id)
    # Preflight leads: refuse a claimed or blocked Assignment before the spawn does
    # any setup for work that cannot proceed.
    backlog_refusal = preflight.preflight_refusal(get_assignment(assignment_id), prefix)
    if backlog_refusal is not None:
        refuse(Refusal(backlog_refusal, preflight.PREFLIGHT_REFUSED_EXIT))
    outcome = refuse_or_clear(clearing.SPAWN_CLEARANCES, clearing.Clearing(prefix, data_files_root))
    if isinstance(outcome, Refusal):
        refuse(outcome)
    ready = outcome.cleared()
    launcher_path = launcher.spawn_launcher(assignment_id, repo_root=ready.target)
    launch = agent.Launch.compose(
        worktree=worktree_name(assignment_id),
        launch_turn=launcher_path,
        environment=agent.propagated_environment(),
        model=model,
    )
    standup.stand_up_session(
        ready.foundation_session,
        target=ready.target,
        launch=launch,
        config_file=claude_config_file,
        projects_root=projects_root,
        data_files_root=data_files_root,
    )


def spawn(assignment_id: str, model: str | None = None) -> None:
    # The single composition root for Spawn: `vv spawn` and `vaudeville spawn`
    # both enter here, so the host's real locations (its data dir, Claude
    # projects root, and folder-trust file) are resolved in one place rather than
    # re-derived per surface.
    orchestrate(
        assignment_id,
        data_dir(),
        claude_projects.projects_root(),
        trust.claude_config_file(),
        model,
    )


def canonical_assignment_id(assignment_id: str) -> str:
    # An Assignment id's namespace prefix is canonically uppercase, and the machine
    # `vv spawn` rejects any other case. `vaudeville spawn` takes ids in whatever case
    # is to hand, so the operator batch canonicalizes each before it Spawns -- resolving
    # `bob-197` to BOB-197 without widening the strict machine surface.
    return assignment_id.upper()


@dataclass(frozen=True)
class SpawnFailure:
    assignment_id: str
    reason: str


def spawn_each(
    assignment_ids: Iterable[str],
    model: str | None,
    spawn_one: Callable[[str, str | None], None] = spawn,
) -> list[SpawnFailure]:
    # Serial for legible per-id reporting, not for safety: each spawn cuts from an
    # immutable base commit it resolves for itself, so concurrent spawns share no
    # mutable state to race on. A failed id is caught and returned as a value rather
    # than printed, so the operator surface owns the rendering. A refusal reaches here
    # as the gate's SystemExit, its cause already on stderr, so the failure carries
    # only the exit code left to add; an ordinary exception has printed nothing, so
    # the failure carries its own text.
    failures: list[SpawnFailure] = []
    for assignment_id in assignment_ids:
        canonical = canonical_assignment_id(assignment_id)
        try:
            spawn_one(canonical, model)
        except SystemExit as spawn_exit:
            failures.append(
                SpawnFailure(
                    canonical,
                    f"exited with status {spawn_exit.code}; continuing with the rest.",
                )
            )
        except Exception as error:
            failures.append(SpawnFailure(canonical, str(error)))
    return failures
