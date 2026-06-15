"""The Registry."""

from __future__ import annotations

import tomllib
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Registry:
    repos: dict[str, str]
    index_url: str | None = None

    def contributor_names(self) -> Iterable[str]:
        return iter(self.repos)

    def remote_for(self, name: str) -> str:
        if name not in self.repos:
            raise UnknownContributor(name)
        return self.repos[name]


class UnknownContributor(KeyError):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.name = name

    def __str__(self) -> str:
        return f"Contributor Repo {self.name!r} is not in the Registry"


class MalformedRegistry(ValueError):
    pass


def registry_declared_in(declaration: Mapping[str, Any], source: Path) -> Registry:
    repos_table = declaration.get("repos", {})
    if not isinstance(repos_table, dict):
        raise MalformedRegistry(f"[repos] in {source} is not a table")
    if not repos_table:
        raise MalformedRegistry(
            f"[repos] in {source} is empty; a Registry must name at least one Contributor Repo"
        )
    repos: dict[str, str] = {}
    for name, remote in repos_table.items():
        if not isinstance(remote, str):
            raise MalformedRegistry(f"[repos].{name} in {source} is not a string")
        repos[name] = remote
    return Registry(repos=repos, index_url=_index_url_in(declaration))


def _index_url_in(declaration: Mapping[str, Any]) -> str | None:
    index_table = declaration.get("index", {})
    if isinstance(index_table, dict):
        url = index_table.get("url")
        if isinstance(url, str):
            return url
    return None


def load_registry(path: Path) -> Registry:
    with path.open("rb") as f:
        declaration = tomllib.load(f)
    return registry_declared_in(declaration, path)
