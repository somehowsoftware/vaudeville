"""Resolve the target-repo path for a Premise id."""

from __future__ import annotations

import sys
from pathlib import Path

from vaudeville_core import managed_repository_for_project, project_from_premise_id


def resolve_target_repo(premise_id: str) -> Path:
    prefix = project_from_premise_id(premise_id)
    resolved = managed_repository_for_project(prefix).repo_path
    if not resolved.is_dir():
        # No auto-clone: surface the missing repo so the operator can clone it
        # explicitly rather than have spawn fan out cloning side effects.
        print(
            f"Error: target repo {resolved} for prefix {prefix!r} does not "
            f"exist on this host. Clone it before spawning a Bob on {premise_id}.",
            file=sys.stderr,
        )
        sys.exit(1)
    return resolved


def main(premise_id: str) -> None:
    print(resolve_target_repo(premise_id))
