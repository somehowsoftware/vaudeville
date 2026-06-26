"""The doc-tree slot discovery: which subtrees a Contributor offers for the host data dir.

A doc tree is a directory a Contributor ships under ``scaffold/<name>/`` for a known, hardcoded
name: the universal doctrine every tenant primes against (``doctrine/``). Discovery here finds
which the Contributor offers; the installer owns placing one (and the symlink refusal), and the
[artifact contract](../../packages/vaudeville-install) owns the slot names.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from vaudeville_install.artifact import DOC_TREE_NAMES


@dataclass(frozen=True)
class DocTree:
    name: str
    source_path: Path


def discover_each_doc_tree_in(source_root: Path) -> list[DocTree]:
    scaffold = source_root / "scaffold"
    return [
        DocTree(name=name, source_path=scaffold / name)
        for name in DOC_TREE_NAMES
        if (scaffold / name).is_dir()
    ]
