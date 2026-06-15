"""Reading the tenant's project register from the host config file.

The anti-corruption layer over ``~/.vaudeville/vaudeville.toml``: a private
pydantic grammar validates the file, ``_config_from_toml`` adapts it to the
domain ``VaudevilleConfig``, and the public functions answer the kernel's
project-register queries. The pydantic grammar never escapes this module;
the file's ``yt_id`` spelling is translated to the domain's
``tracker_project_id`` at the boundary.
"""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path
from typing import Any, NoReturn

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from vaudeville_core.project import (
    Project,
    VaudevilleConfig,
    descriptions,
    managed_repository_for_prefix,
    prefix_from_premise_id,
    prefixes,
    undescribed_prefixes,
)

VAUDEVILLE_FILENAME = "vaudeville.toml"


def host_config_path(filename: str, host_config_dir: Path | None = None) -> Path:
    base = host_config_dir if host_config_dir is not None else Path.home() / ".vaudeville"
    return base / filename


def _abort(message: str) -> NoReturn:
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(1)


class _ProjectEntry(BaseModel):
    model_config = ConfigDict(extra="ignore")

    yt_id: str
    repo_path: str
    name: str
    short_name: str | None = None
    description: str | None = None
    remote: str | None = None


class _Downstream(BaseModel):
    model_config = ConfigDict(extra="ignore")

    command: list[str] = Field(min_length=1)


class _Spawn(BaseModel):
    model_config = ConfigDict(extra="ignore")

    downstream: _Downstream | None = None


class _ConfigFile(BaseModel):
    """The TOML grammar of ``~/.vaudeville/vaudeville.toml``. A parse-target only."""

    model_config = ConfigDict(extra="ignore")

    projects: dict[str, _ProjectEntry] = Field(min_length=1)
    spawn: _Spawn = Field(default_factory=_Spawn)


def _config_from_toml(raw: dict[str, Any]) -> VaudevilleConfig:
    parsed = _ConfigFile.model_validate(raw)
    projects = {
        prefix: Project(
            prefix=prefix,
            tracker_project_id=entry.yt_id,
            repo_path=Path(entry.repo_path).expanduser().resolve(),
            description=entry.description,
            remote=entry.remote,
            name=entry.name,
            short_name=entry.short_name,
        )
        for prefix, entry in parsed.projects.items()
    }
    command = tuple(parsed.spawn.downstream.command) if parsed.spawn.downstream else None
    return VaudevilleConfig(projects=projects, downstream_command=command)


def load_config(host_config_dir: Path | None = None) -> VaudevilleConfig:
    path = host_config_path(VAUDEVILLE_FILENAME, host_config_dir)
    if not path.is_file():
        _abort(f"{path} not found. Run the Vaudeville install to create it.")
    with path.open("rb") as handle:
        raw = tomllib.load(handle)
    try:
        return _config_from_toml(raw)
    except ValidationError as exc:
        _abort(f"{path} is malformed: {exc}")


def list_projects(*, host_config_dir: Path | None = None) -> list[str]:
    return prefixes(load_config(host_config_dir))


def managed_repository_for_project(prefix: str, *, host_config_dir: Path | None = None) -> Project:
    config = load_config(host_config_dir)
    repository = managed_repository_for_prefix(config, prefix)
    if repository is None:
        known = ", ".join(prefixes(config)) or "(none)"
        _abort(
            f"no {VAUDEVILLE_FILENAME} entry for project prefix {prefix!r}. "
            f"Known prefixes: {known}."
        )
    return repository


def repo_descriptions(*, host_config_dir: Path | None = None) -> dict[str, str]:
    config = load_config(host_config_dir)
    missing = undescribed_prefixes(config)
    if missing:
        register = host_config_path(VAUDEVILLE_FILENAME, host_config_dir)
        _abort(
            f"{register}: projects {missing!r} "
            "have no `description` field. `vv fork` needs a one-sentence "
            "bounded-context summary per project."
        )
    return descriptions(config)


def downstream_command(*, host_config_dir: Path | None = None) -> list[str]:
    config = load_config(host_config_dir)
    if config.downstream_command is None:
        register = host_config_path(VAUDEVILLE_FILENAME, host_config_dir)
        _abort(
            f"{register} has no [spawn.downstream] command. "
            'Add an argv array, e.g. [spawn.downstream] command = ["vv", "premise-context"].'
        )
    return list(config.downstream_command)


def project_from_premise_id(premise_id: str) -> str:
    prefix = prefix_from_premise_id(premise_id)
    if prefix is None:
        _abort(f"{premise_id!r} is not a Premise id of the form PREFIX-NUMBER.")
    return prefix


def project_from_name(name: str, *, host_config_dir: Path | None = None) -> str:
    config = load_config(host_config_dir)
    canonical = name.casefold()
    matching = [
        prefix
        for prefix, p in config.projects.items()
        if p.name.casefold() == canonical
        or (p.short_name is not None and p.short_name.casefold() == canonical)
    ]
    if len(matching) > 1:
        _abort(f"name {name!r} is ambiguous: matches projects {', '.join(sorted(matching))}.")
    if not matching:
        known = sorted(
            n
            for p in config.projects.values()
            for n in ([p.name] + ([p.short_name] if p.short_name is not None else []))
        )
        _abort(f"no project named {name!r}. Known names: {', '.join(known) or '(none)'}.")
    return matching[0]
