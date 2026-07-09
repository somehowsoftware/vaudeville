"""The CLI Declaration: a Contributor's `[tool.vaudeville]` entry."""

from __future__ import annotations

import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class CLIDeclaration:
    binary: str
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
    binary = table.get("binary")
    if not isinstance(binary, str):
        raise MalformedCLIDeclaration(
            f"{source}: [tool.vaudeville].binary is required and must be a string"
        )
    operator_binary = table.get("operator_binary")
    if operator_binary is not None and not isinstance(operator_binary, str):
        raise MalformedCLIDeclaration(
            f"{source}: [tool.vaudeville].operator_binary must be a string"
        )
    return CLIDeclaration(binary=binary, operator_binary=operator_binary)


def read_cli_declaration_at(source_root: Path) -> CLIDeclaration | None:
    pyproject = source_root / "pyproject.toml"
    if not pyproject.is_file():
        return None
    with pyproject.open("rb") as f:
        declaration = tomllib.load(f)
    return cli_declaration_declared_in(declaration, pyproject)
