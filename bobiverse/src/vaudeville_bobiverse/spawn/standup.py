from __future__ import annotations

from pathlib import Path

from vaudeville_bobiverse.spawn import agent, seed, trust, workmux
from vaudeville_bobiverse.spawn.agent import Launch


def worktree_path_under(target: Path, worktree: str) -> Path:
    # `workmux add` materializes the worktree in the sibling `<repo>__worktrees/`
    # directory, so the trust record must name that path: the directory the
    # spawned `claude` will actually open and check.
    return target.parent / f"{target.name}__worktrees" / worktree


def stand_up_session(
    foundation_session: str,
    *,
    target: Path,
    launch: Launch,
    config_file: Path,
    projects_root: Path,
    data_files_root: Path,
) -> None:
    # Seed must be in place before the fork: `workmux add --fork` resolves its source
    # conversation from the seeded clone, so an unseeded clone has nothing to fork.
    trust.record_worktree_trust(
        worktree_path_under(target, launch.worktree), config_file=config_file
    )
    seeded = seed.seed_foundation(
        foundation_session,
        into_clone=target,
        projects_root=projects_root,
        data_files_root=data_files_root,
    )
    agent_script = agent.write_agent_script(target, launch)
    workmux.run_workmux(workmux.workmux_invocation(seeded, launch.worktree, agent_script))
