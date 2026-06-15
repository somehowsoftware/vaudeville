"""The Spawn composition: clear the gates a refusal turns on, then launch.

``orchestrate`` is a straight-line composition of independently-tested pieces. It
clears three gates in order — backlog (``preflight``), host repo
(``resolve_target_repo``), then Foundation (``spawn_decision``) — and on the
clearance prepares the substrate and hands the launch to ``workmux``. The order
is the contract: a Premise that can't be worked refuses before the operator is
told to repair host state. The seed returns the ``SeededClone`` the workmux fork
is built from, so the substrate is prepared before the launch by data dependency
rather than by call order. ``spawn`` is the single root where the host's real
locations are resolved and threaded in; both it and ``orchestrate`` are
composition roots — the gate sequencing among them is left untested by design.
"""

from __future__ import annotations

import sys
from pathlib import Path

from vaudeville_core import (
    get_premise,
    list_projects,
    managed_repository_for_project,
    project_from_premise_id,
)

from vaudeville_bobiverse import claude_projects, foundation, refresh
from vaudeville_bobiverse.data_dir import data_dir
from vaudeville_bobiverse.spawn import agent, launcher, preflight, seed, target_repo, trust, workmux
from vaudeville_bobiverse.spawn.decision import SpawnRefusal, spawn_decision


def worktree_name(premise_id: str) -> str:
    prefix = project_from_premise_id(premise_id)
    _, _, number = premise_id.partition("-")
    return f"{prefix.lower()}-{number}"


def worktree_path_under(target: Path, worktree: str) -> Path:
    # `workmux add` materializes the worktree in the sibling `<repo>__worktrees/`
    # directory, so the trust record must name that path — the directory the
    # spawned `claude` will actually open and check.
    return target.parent / f"{target.name}__worktrees" / worktree


def orchestrate(
    premise_id: str,
    data_files_root: Path,
    projects_root: Path,
    claude_config_file: Path,
    clones: list[Path],
) -> None:
    prefix = project_from_premise_id(premise_id)
    # Gate order: backlog → host repo → Foundation. Preflight refuses a claimed
    # or blocked Premise before the operator is sent to repair host state for
    # work that can't proceed; target precedes Foundation so an unmanaged prefix
    # reads as "no such Managed Repository", not a misleading "no Foundation".
    refusal = preflight.preflight_refusal(get_premise(premise_id), prefix)
    if refusal is not None:
        print(refusal, file=sys.stderr)
        sys.exit(preflight.PREFLIGHT_REFUSED_EXIT)
    target = target_repo.resolve_target_repo(premise_id)
    foundation_session = foundation.lookup(prefix, data_files_root=data_files_root)
    decided = spawn_decision(prefix, foundation_session)
    if isinstance(decided, SpawnRefusal):
        print(decided.message, file=sys.stderr)
        sys.exit(decided.exit_code)
    # Reset clones to clean origin/main before writing the launcher into the
    # target's .scratch/ — a later `git clean` would otherwise wipe it.
    refresh.refresh_clones(clones)
    launcher_path = launcher.spawn_launcher(premise_id, repo_root=target)
    worktree = worktree_name(premise_id)
    trust.record_worktree_trust(
        worktree_path_under(target, worktree), config_file=claude_config_file
    )
    # `--fork` resolves its source conversation from `workmux add`'s cwd — the
    # clone (`target`) — so the Foundation is seeded into the clone's project
    # directory, not the worktree path the trust entry names (the fork's
    # destination, where the Bob's new session lands).
    seeded = seed.seed_foundation(
        decided.foundation_session,
        into_clone=target,
        projects_root=projects_root,
        data_files_root=data_files_root,
    )
    workmux.run_workmux(
        workmux.workmux_invocation(seeded, worktree, launcher_path, agent.propagated_environment())
    )


def managed_clones() -> list[Path]:
    return [managed_repository_for_project(prefix).repo_path for prefix in list_projects()]


def spawn(premise_id: str) -> None:
    # The single composition root for Spawn: `vv spawn` and `vaudeville spawn`
    # both enter here, so the host's real locations — its data dir, Claude
    # projects root, folder-trust file, and managed clones — are resolved in one
    # place rather than re-derived per surface.
    orchestrate(
        premise_id,
        data_dir(),
        claude_projects.projects_root(),
        trust.claude_config_file(),
        managed_clones(),
    )
