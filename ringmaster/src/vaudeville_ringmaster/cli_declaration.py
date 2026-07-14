"""The CLI Declaration: a Contributor's `[tool.vaudeville]` entry."""

from __future__ import annotations

import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class CLIDeclaration:
    binary: str | None = None
    operator_binary: str | None = None


class MalformedCLIDeclaration(ValueError):
    pass


def cli_declaration_declared_in(
    pyproject: Mapping[str, Any], source: Path
) -> CLIDeclaration | None:
    tool_section = pyproject.get("tool", {})
    if not isinstance(tool_section, dict):
        return None
    table = tool_section.get("vaudeville")
    if table is None:
        return None
    if not isinstance(table, dict):
        raise MalformedCLIDeclaration(f"{source}: [tool.vaudeville] must be a table")
    binary = _named_app(table, "binary", source)
    operator_binary = _named_app(table, "operator_binary", source)
    if binary is None and operator_binary is None:
        # A table marks the Contributor as part of the command Surface, so one naming neither app
        # claims a Surface it does not have.
        raise MalformedCLIDeclaration(
            f"{source}: [tool.vaudeville] must name at least one of `binary` (its `vv` app) or "
            "`operator_binary` (its operator app)"
        )
    return CLIDeclaration(binary=binary, operator_binary=operator_binary)


def _named_app(table: Mapping[str, Any], key: str, source: Path) -> str | None:
    value = table.get(key)
    if value is not None and not isinstance(value, str):
        raise MalformedCLIDeclaration(f"{source}: [tool.vaudeville].{key} must be a string")
    return value


def read_cli_declaration_at(source_root: Path) -> CLIDeclaration | None:
    pyproject = source_root / "pyproject.toml"
    if not pyproject.is_file():
        return None
    with pyproject.open("rb") as f:
        declaration = tomllib.load(f)
    return cli_declaration_declared_in(declaration, pyproject)
