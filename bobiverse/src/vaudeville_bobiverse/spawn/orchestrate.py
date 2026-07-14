from __future__ import annotations

from pathlib import Path

from vaudeville_core import component_from_assignment_id, get_assignment

from vaudeville_bobiverse import claude_projects
from vaudeville_bobiverse.data_dir import data_dir
from vaudeville_bobiverse.spawn import clearing, launcher, preflight, standup, trust
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
    standup.stand_up_session(
        ready.foundation_session,
        target=ready.target,
        worktree=worktree_name(assignment_id),
        prompt_file=launcher_path,
        config_file=claude_config_file,
        projects_root=projects_root,
        data_files_root=data_files_root,
    )


def spawn(assignment_id: str) -> None:
    # The single composition root for Spawn: `vv spawn` and `vaudeville spawn`
    # both enter here, so the host's real locations (its data dir, Claude
    # projects root, and folder-trust file) are resolved in one place rather than
    # re-derived per surface.
    orchestrate(
        assignment_id,
        data_dir(),
        claude_projects.projects_root(),
        trust.claude_config_file(),
    )
