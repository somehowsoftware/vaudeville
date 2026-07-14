from __future__ import annotations

import os
import shutil
import sys
import tomllib
from dataclasses import replace
from pathlib import Path
from typing import Any, NoReturn

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from vaudeville_core.component import (
    Component,
    VaudevilleConfig,
    component_for_prefix,
    descriptions,
    is_component_prefix,
    prefix_from_assignment_id,
    prefixes,
    undescribed_prefixes,
)

VAUDEVILLE_FILENAME = "vaudeville.toml"


def host_config_path(filename: str, host_config_dir: Path | None = None) -> Path:
    base = host_config_dir if host_config_dir is not None else _default_data_dir()
    return base / filename


def _default_data_dir() -> Path:
    # The register lives in the data dir, so VV_DATA_DIR redirects it the same way
    # vaudeville-bobiverse's data_dir honors it; a rehearse pointed at a Rehearsal
    # Installation then reads the candidate's register, not the host's. Empty is unset.
    override = os.environ.get("VV_DATA_DIR")
    base = Path(override) if override else Path.home() / ".vaudeville"
    return base.expanduser().resolve()


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


def _canonical_repo_path(repo_path: Path) -> Path:
    return repo_path.expanduser().resolve()


def _config_from_toml(raw: dict[str, Any]) -> VaudevilleConfig:
    parsed = _ConfigFile.model_validate(raw)
    components = {
        prefix: Component(
            prefix=prefix,
            tracker_project_id=entry.yt_id,
            repo_path=_canonical_repo_path(Path(entry.repo_path)),
            description=entry.description,
            remote=entry.remote,
            name=entry.name,
            short_name=entry.short_name,
        )
        for prefix, entry in parsed.projects.items()
    }
    command = tuple(parsed.spawn.downstream.command) if parsed.spawn.downstream else None
    return VaudevilleConfig(components=components, downstream_command=command)


_PROBE_PREFIX = "__vaudeville_appendability_probe__"

_NON_APPENDABLE_REMEDY = (
    "its projects table is written in a form that cannot be extended in place "
    "(e.g. an inline table). Rewrite it as [projects.<PREFIX>] section tables."
)


def _projects_table_is_appendable(raw_text: str) -> bool:
    # tomllib is the oracle for whether a new [projects.<PREFIX>] table can be appended: an
    # inline or otherwise closed projects table rejects the probe. The probe key sits outside
    # the [A-Z]+ Component-prefix grammar so it can never collide with a prefix already there.
    probed = raw_text.rstrip("\n") + "\n\n[projects." + _PROBE_PREFIX + "]\n"
    try:
        tomllib.loads(probed)
    except tomllib.TOMLDecodeError:
        return False
    return True


def load_config(host_config_dir: Path | None = None) -> VaudevilleConfig:
    path = host_config_path(VAUDEVILLE_FILENAME, host_config_dir)
    if not path.is_file():
        _abort(f"{path} not found. Run the Vaudeville install to create it.")
    raw_text = path.read_text(encoding="utf-8")
    try:
        raw = tomllib.loads(raw_text)
    except tomllib.TOMLDecodeError as exc:
        _abort(f"{path} is malformed: {exc}")
    if not _projects_table_is_appendable(raw_text):
        _abort(f"{path}: {_NON_APPENDABLE_REMEDY}")
    try:
        return _config_from_toml(raw)
    except ValidationError as exc:
        _abort(f"{path} is malformed: {exc}")


def list_components(*, host_config_dir: Path | None = None) -> list[str]:
    return prefixes(load_config(host_config_dir))


def component_from_prefix(prefix: str, *, host_config_dir: Path | None = None) -> Component:
    config = load_config(host_config_dir)
    component = component_for_prefix(config, prefix)
    if component is None:
        known = ", ".join(prefixes(config)) or "(none)"
        _abort(
            f"no {VAUDEVILLE_FILENAME} entry for Component prefix {prefix!r}. "
            f"Known prefixes: {known}."
        )
    return component


def repo_descriptions(*, host_config_dir: Path | None = None) -> dict[str, str]:
    config = load_config(host_config_dir)
    missing = undescribed_prefixes(config)
    if missing:
        register = host_config_path(VAUDEVILLE_FILENAME, host_config_dir)
        _abort(
            f"{register}: Components {missing!r} "
            "have no `description` field. `vv fork` needs a one-sentence "
            "bounded-context summary per Component."
        )
    return descriptions(config)


def downstream_command(*, host_config_dir: Path | None = None) -> list[str]:
    config = load_config(host_config_dir)
    if config.downstream_command is None:
        register = host_config_path(VAUDEVILLE_FILENAME, host_config_dir)
        _abort(
            f"{register} has no [spawn.downstream] command. "
            'Add an argv array, e.g. [spawn.downstream] command = ["vv", "assignment-context"].'
        )
    return list(config.downstream_command)


def component_from_assignment_id(assignment_id: str) -> str:
    prefix = prefix_from_assignment_id(assignment_id)
    if prefix is None:
        _abort(f"{assignment_id!r} is not an Assignment id of the form PREFIX-NUMBER.")
    return prefix


def component_from_name(name: str, *, host_config_dir: Path | None = None) -> str:
    config = load_config(host_config_dir)
    canonical = name.casefold()
    matching = [
        prefix
        for prefix, c in config.components.items()
        if c.name.casefold() == canonical
        or (c.short_name is not None and c.short_name.casefold() == canonical)
    ]
    if len(matching) > 1:
        _abort(f"name {name!r} is ambiguous: matches Components {', '.join(sorted(matching))}.")
    if not matching:
        known = sorted(
            n
            for c in config.components.values()
            for n in ([c.name] + ([c.short_name] if c.short_name is not None else []))
        )
        _abort(f"no Component named {name!r}. Known names: {', '.join(known) or '(none)'}.")
    return matching[0]


def register_component(component: Component, *, host_config_dir: Path | None = None) -> None:
    canonical = _canonical(component)
    already = component_for_prefix(load_config(host_config_dir), canonical.prefix)
    if already == canonical:
        return
    path = host_config_path(VAUDEVILLE_FILENAME, host_config_dir)
    if already is not None:
        _abort(
            f"{path}: Component prefix {canonical.prefix!r} is already registered with "
            f"different coordinates. Refusing to overwrite; edit the entry by hand to change it."
        )
    if not is_component_prefix(canonical.prefix):
        _abort(
            f"{path}: Component prefix {canonical.prefix!r} is not a valid Component prefix "
            f"(uppercase letters only); its assignment ids could not be read back. Fix the "
            f"prefix and register again."
        )
    _splice_entry(path, _project_table(canonical))


def _canonical(component: Component) -> Component:
    return replace(component, repo_path=_canonical_repo_path(component.repo_path))


_TOML_ESCAPES = {
    "\\": "\\\\",
    '"': '\\"',
    "\b": "\\b",
    "\t": "\\t",
    "\n": "\\n",
    "\f": "\\f",
    "\r": "\\r",
}


def _toml_basic_string(value: str) -> str:
    rendered = []
    for char in value:
        if char in _TOML_ESCAPES:
            rendered.append(_TOML_ESCAPES[char])
        elif char < "\x20" or char == "\x7f":
            rendered.append(f"\\u{ord(char):04x}")
        else:
            rendered.append(char)
    return '"' + "".join(rendered) + '"'


def _project_table(component: Component) -> str:
    optional = {
        "short_name": component.short_name,
        "description": component.description,
        "remote": component.remote,
    }
    lines = [
        f"[projects.{component.prefix}]",
        f"yt_id = {_toml_basic_string(component.tracker_project_id)}",
        f"repo_path = {_toml_basic_string(str(component.repo_path))}",
        f"name = {_toml_basic_string(component.name)}",
        *(
            f"{key} = {_toml_basic_string(value)}"
            for key, value in optional.items()
            if value is not None
        ),
    ]
    return "\n".join(lines)


def _splice_entry(path: Path, table: str) -> None:
    # Append rather than parse-and-reserialize: a TOML round-trip would reorder the tables
    # and strip the operator's comments. The temp file is born under the process umask, so
    # its mode is copied from the register to keep the file's permissions across the replace.
    text = path.read_text(encoding="utf-8")
    if not _projects_table_is_appendable(text):
        _abort(f"{path}: {_NON_APPENDABLE_REMEDY}")
    spliced = text.rstrip("\n") + "\n\n" + table + "\n"
    temporary = path.parent / (path.name + ".tmp")
    temporary.write_text(spliced, encoding="utf-8")
    shutil.copymode(path, temporary)
    temporary.replace(path)
