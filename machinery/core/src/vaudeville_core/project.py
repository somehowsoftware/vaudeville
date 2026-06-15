"""The project register — the tenant's projects as values, and the pure
questions asked of them.

Data and pure functions only: no file, no environment, no git, no process
exit. Reading the register from the host config lives in ``config_file``;
resolving the current project from a git working tree lives in ``worktree``.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

_PREMISE_RE = re.compile(r"^([A-Z]+)-\d+$")


@dataclass(frozen=True)
class Project:
    """A registered project: its tracker prefix and where it lives.

    `remote` is the git URL of the project's canonical history — the
    coordinate a Fresh clone reads from, so a cross-repo read is current
    by construction rather than as current as a local clone happens to
    be. Optional: a project read only from its local clone need not
    carry one, and a Fresh clone of such a project aborts at the point of
    need rather than the register failing to load.
    """

    prefix: str
    tracker_project_id: str
    repo_path: Path
    description: str | None
    remote: str | None
    name: str
    short_name: str | None


@dataclass(frozen=True)
class VaudevilleConfig:
    """The tenant's project register plus the spawn downstream command."""

    projects: Mapping[str, Project]
    downstream_command: tuple[str, ...] | None


def make_project(
    prefix: str = "BOB",
    *,
    tracker_project_id: str = "0-1",
    repo_path: Path = Path("/repos/bob"),
    description: str | None = None,
    remote: str | None = None,
    name: str = "",
    short_name: str | None = None,
) -> Project:
    return Project(
        prefix=prefix,
        tracker_project_id=tracker_project_id,
        repo_path=repo_path,
        description=description,
        remote=remote,
        name=name,
        short_name=short_name,
    )


def make_config(
    *projects: Project,
    downstream_command: tuple[str, ...] | None = None,
) -> VaudevilleConfig:
    return VaudevilleConfig(
        projects={project.prefix: project for project in projects},
        downstream_command=downstream_command,
    )


def prefixes(config: VaudevilleConfig) -> list[str]:
    return sorted(config.projects)


def project_for_repo_root(config: VaudevilleConfig, repo_root: Path) -> Project | None:
    for project in config.projects.values():
        if project.repo_path == repo_root:
            return project
    return None


def managed_repository_for_prefix(config: VaudevilleConfig, prefix: str) -> Project | None:
    return config.projects.get(prefix)


def tracker_project_id_for_prefix(config: VaudevilleConfig, prefix: str) -> str | None:
    project = config.projects.get(prefix)
    return project.tracker_project_id if project is not None else None


def descriptions(config: VaudevilleConfig) -> dict[str, str]:
    """Each prefix mapped to its description, omitting any absent or blank."""
    result: dict[str, str] = {}
    for prefix, project in sorted(config.projects.items()):
        description = project.description
        if description is not None and description.strip():
            result[prefix] = description
    return result


def undescribed_prefixes(config: VaudevilleConfig) -> list[str]:
    """Prefixes whose project has no description, or only a blank one."""
    return sorted(
        prefix
        for prefix, project in config.projects.items()
        if not (project.description or "").strip()
    )


def prefix_from_premise_id(premise_id: str) -> str | None:
    match = _PREMISE_RE.match(premise_id)
    return match.group(1) if match is not None else None


def prefix_from_name(config: VaudevilleConfig, name: str) -> str | None:
    """Return the prefix of the project matching `name`, or None.

    Matches case-insensitively against both `name` and `short_name`.
    Returns the first match found; the caller is responsible for
    detecting duplicates before relying on uniqueness.
    """
    canonical = name.casefold()
    for prefix, p in config.projects.items():
        if p.name.casefold() == canonical or (
            p.short_name is not None and p.short_name.casefold() == canonical
        ):
            return prefix
    return None
