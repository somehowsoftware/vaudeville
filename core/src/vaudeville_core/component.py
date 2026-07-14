"""The Component register: the tenant's Components as values, and the pure
questions asked of them.

Data and pure functions only: no file, no environment, no git, no process
exit. Reading the register from the host config lives in ``config_file``;
resolving the current Component from a git working tree lives in ``worktree``.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

_PREFIX_RE = re.compile(r"[A-Z]+")
_ASSIGNMENT_RE = re.compile(rf"^({_PREFIX_RE.pattern})-\d+$")


@dataclass(frozen=True)
class Component:
    """A registered Component: its tracker prefix and where it lives.

    `remote` is the git URL of the Component's canonical history: the
    coordinate a Fresh clone reads from, so a cross-repo read is current
    by construction rather than as current as a local clone happens to
    be. Optional: a Component read only from its local clone need not
    carry one, and a Fresh clone of such a Component aborts at the point of
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
    """The tenant's Component register plus the spawn downstream command."""

    components: Mapping[str, Component]
    downstream_command: tuple[str, ...] | None


def make_component(
    prefix: str = "BOB",
    *,
    tracker_project_id: str = "0-1",
    repo_path: Path = Path("/repos/bob"),
    description: str | None = None,
    remote: str | None = None,
    name: str = "",
    short_name: str | None = None,
) -> Component:
    return Component(
        prefix=prefix,
        tracker_project_id=tracker_project_id,
        repo_path=repo_path,
        description=description,
        remote=remote,
        name=name,
        short_name=short_name,
    )


def make_config(
    *components: Component,
    downstream_command: tuple[str, ...] | None = None,
) -> VaudevilleConfig:
    return VaudevilleConfig(
        components={component.prefix: component for component in components},
        downstream_command=downstream_command,
    )


def prefixes(config: VaudevilleConfig) -> list[str]:
    return sorted(config.components)


def component_for_repo_root(config: VaudevilleConfig, repo_root: Path) -> Component | None:
    for component in config.components.values():
        if component.repo_path == repo_root:
            return component
    return None


def component_for_prefix(config: VaudevilleConfig, prefix: str) -> Component | None:
    return config.components.get(prefix)


def tracker_project_id_for_prefix(config: VaudevilleConfig, prefix: str) -> str | None:
    component = config.components.get(prefix)
    return component.tracker_project_id if component is not None else None


def descriptions(config: VaudevilleConfig) -> dict[str, str]:
    """Each prefix mapped to its description, omitting any absent or blank."""
    result: dict[str, str] = {}
    for prefix, component in sorted(config.components.items()):
        description = component.description
        if description is not None and description.strip():
            result[prefix] = description
    return result


def undescribed_prefixes(config: VaudevilleConfig) -> list[str]:
    """Prefixes whose Component has no description, or only a blank one."""
    return sorted(
        prefix
        for prefix, component in config.components.items()
        if not (component.description or "").strip()
    )


def prefix_from_assignment_id(assignment_id: str) -> str | None:
    match = _ASSIGNMENT_RE.match(assignment_id)
    return match.group(1) if match is not None else None


def is_component_prefix(value: str) -> bool:
    return _PREFIX_RE.fullmatch(value) is not None


def prefix_from_name(config: VaudevilleConfig, name: str) -> str | None:
    """Return the prefix of the Component matching `name`, or None.

    Matches case-insensitively against both `name` and `short_name`.
    Returns the first match found; the caller is responsible for
    detecting duplicates before relying on uniqueness.
    """
    canonical = name.casefold()
    for prefix, c in config.components.items():
        if c.name.casefold() == canonical or (
            c.short_name is not None and c.short_name.casefold() == canonical
        ):
            return prefix
    return None
