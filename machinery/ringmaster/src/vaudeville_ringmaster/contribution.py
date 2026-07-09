"""The Contribution: what a Contributor Repo offers to the Host Installation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from vaudeville_ringmaster.cli_declaration import CLIDeclaration, read_cli_declaration_at
from vaudeville_ringmaster.console_script import (
    ConsoleScript,
    discover_each_console_script_in,
)
from vaudeville_ringmaster.data_file import DataFile, discover_each_data_file_in
from vaudeville_ringmaster.doc_tree import DocTree, discover_each_doc_tree_in
from vaudeville_ringmaster.hook_matchers import HookMatchers, read_hook_matchers_at
from vaudeville_ringmaster.hook_script import HookScript, discover_each_hook_script_in
from vaudeville_ringmaster.package import discover_distribution_in
from vaudeville_ringmaster.skill import Skill, discover_each_skill_in


@dataclass(frozen=True)
class Contribution:
    name: str
    source_root: Path
    skills: tuple[Skill, ...]
    data_files: tuple[DataFile, ...]
    doc_trees: tuple[DocTree, ...]
    hook_scripts: tuple[HookScript, ...]
    hook_matchers: HookMatchers | None
    console_scripts: tuple[ConsoleScript, ...]
    cli_declaration: CLIDeclaration | None
    distribution: str | None = None


def discover_contribution_in(name: str, source_root: Path) -> Contribution:
    return Contribution(
        name=name,
        source_root=source_root,
        skills=tuple(discover_each_skill_in(source_root)),
        data_files=tuple(discover_each_data_file_in(source_root)),
        doc_trees=tuple(discover_each_doc_tree_in(source_root)),
        hook_scripts=tuple(discover_each_hook_script_in(source_root)),
        hook_matchers=read_hook_matchers_at(source_root),
        console_scripts=tuple(discover_each_console_script_in(source_root)),
        cli_declaration=read_cli_declaration_at(source_root),
        distribution=discover_distribution_in(source_root),
    )
