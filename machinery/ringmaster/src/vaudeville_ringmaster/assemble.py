"""The Assemble phase."""

from __future__ import annotations

from vaudeville_ringmaster.apply_plan import ApplyPlan, raise_if_apply_plan_has_collisions
from vaudeville_ringmaster.contribution import discover_contribution_in
from vaudeville_ringmaster.registry import Registry
from vaudeville_ringmaster.session_clone import SessionClone
from vaudeville_ringmaster.worktree import Worktree, clone_root_of, name_of_owning_repo_for


def assemble_apply_plan(
    registry: Registry,
    session_clones: list[SessionClone],
    worktree: Worktree | None = None,
) -> ApplyPlan:
    owning_name = name_of_owning_repo_for(worktree, registry) if worktree is not None else None
    contributions = []
    for session_clone in session_clones:
        if session_clone.name == owning_name and worktree is not None:
            source_root = clone_root_of(worktree)
        else:
            source_root = session_clone.path
        contributions.append(discover_contribution_in(session_clone.name, source_root))
    plan = ApplyPlan(contributions=tuple(contributions))
    raise_if_apply_plan_has_collisions(plan)
    return plan
