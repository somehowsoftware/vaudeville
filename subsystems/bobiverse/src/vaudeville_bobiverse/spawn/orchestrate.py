from __future__ import annotations

import sys
from pathlib import Path

from vaudeville_core import component_from_assignment_id, get_assignment

from vaudeville_bobiverse import claude_projects, foundation, refresh
from vaudeville_bobiverse.data_dir import data_dir
from vaudeville_bobiverse.managed_clones import managed_clones
from vaudeville_bobiverse.spawn import launcher, preflight, standup, target_repo, trust
from vaudeville_bobiverse.spawn.decision import SpawnRefusal, spawn_decision


def worktree_name(assignment_id: str) -> str:
    prefix = component_from_assignment_id(assignment_id)
    _, _, number = assignment_id.partition("-")
    return f"{prefix.lower()}-{number}"


def orchestrate(
    assignment_id: str,
    data_files_root: Path,
    projects_root: Path,
    claude_config_file: Path,
    clones: list[Path],
) -> None:
    prefix = component_from_assignment_id(assignment_id)
    # Gate order: backlog → host repo → Foundation. Preflight refuses a claimed
    # or blocked Assignment before the operator is sent to repair host state for
    # work that can't proceed; target precedes Foundation so an unmanaged prefix
    # reads as "no such Component", not a misleading "no Foundation".
    refusal = preflight.preflight_refusal(get_assignment(assignment_id), prefix)
    if refusal is not None:
        print(refusal, file=sys.stderr)
        sys.exit(preflight.PREFLIGHT_REFUSED_EXIT)
    target = target_repo.resolve_target_repo(assignment_id)
    foundation_session = foundation.lookup(prefix, data_files_root=data_files_root)
    decided = spawn_decision(prefix, foundation_session)
    if isinstance(decided, SpawnRefusal):
        print(decided.message, file=sys.stderr)
        sys.exit(decided.exit_code)
    # Reset clones to clean origin/main before writing the launcher into the
    # target's .scratch/; a later `git clean` would otherwise wipe it.
    refresh.refresh_clones(clones)
    launcher_path = launcher.spawn_launcher(assignment_id, repo_root=target)
    standup.stand_up_session(
        decided.foundation_session,
        target=target,
        worktree=worktree_name(assignment_id),
        prompt_file=launcher_path,
        config_file=claude_config_file,
        projects_root=projects_root,
        data_files_root=data_files_root,
    )


def spawn(assignment_id: str) -> None:
    # The single composition root for Spawn: `vv spawn` and `vaudeville spawn`
    # both enter here, so the host's real locations (its data dir, Claude
    # projects root, folder-trust file, and managed clones) are resolved in one
    # place rather than re-derived per surface.
    orchestrate(
        assignment_id,
        data_dir(),
        claude_projects.projects_root(),
        trust.claude_config_file(),
        managed_clones(),
    )
