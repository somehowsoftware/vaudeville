from __future__ import annotations

import sys
from pathlib import Path

from vaudeville_core import component_from_assignment_id, component_from_prefix

from vaudeville_bobiverse.spawn.origin_drift import observe_origin, origin_drift_refusal


def target_repo_for_prefix(prefix: str) -> Path:
    component = component_from_prefix(prefix)
    resolved = component.repo_path
    if not resolved.is_dir():
        # No auto-clone: surface the missing repo so the operator can clone it
        # explicitly rather than have a Bob fan out cloning side effects.
        print(
            f"Error: target repo {resolved} for prefix {prefix!r} does not "
            "exist on this host. Clone it before forking a Bob into it.",
            file=sys.stderr,
        )
        sys.exit(1)
    # Name origin drift here, against the registry, before the clone-refresh sweep
    # and workmux can turn a missing `origin` into an opaque exit-128.
    drift = origin_drift_refusal(resolved, component.remote, observe_origin(resolved))
    if drift is not None:
        print(drift, file=sys.stderr)
        sys.exit(1)
    return resolved


def resolve_target_repo(assignment_id: str) -> Path:
    return target_repo_for_prefix(component_from_assignment_id(assignment_id))


def main(assignment_id: str) -> None:
    print(resolve_target_repo(assignment_id))
