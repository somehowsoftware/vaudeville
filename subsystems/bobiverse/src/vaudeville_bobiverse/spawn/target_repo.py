from __future__ import annotations

from pathlib import Path

from vaudeville_core import component_from_assignment_id, component_from_prefix

from vaudeville_bobiverse.spawn.origin_drift import observe_origin, origin_drift_refusal
from vaudeville_bobiverse.spawn.refusal import Refusal, refuse

TARGET_UNRESOLVED_EXIT = 1


def target_repo_for_prefix(prefix: str) -> Path | Refusal:
    component = component_from_prefix(prefix)
    resolved = component.repo_path
    if not resolved.is_dir():
        # No auto-clone: surface the missing repo so the operator can clone it
        # explicitly rather than have a Bob fan out cloning side effects.
        return Refusal(
            message=(
                f"Error: target repo {resolved} for prefix {prefix!r} does not "
                "exist on this host. Clone it before forking a Bob into it."
            ),
            exit_code=TARGET_UNRESOLVED_EXIT,
        )
    # Name origin drift here, against the registry, before the base fetch or workmux
    # turns a missing or misconfigured `origin` into an opaque git failure downstream.
    drift = origin_drift_refusal(resolved, component.remote, observe_origin(resolved))
    if drift is not None:
        return Refusal(message=drift, exit_code=TARGET_UNRESOLVED_EXIT)
    return resolved


def resolve_target_repo(assignment_id: str) -> Path | Refusal:
    return target_repo_for_prefix(component_from_assignment_id(assignment_id))


def main(assignment_id: str) -> None:
    resolved = resolve_target_repo(assignment_id)
    if isinstance(resolved, Refusal):
        refuse(resolved)
    print(resolved)
