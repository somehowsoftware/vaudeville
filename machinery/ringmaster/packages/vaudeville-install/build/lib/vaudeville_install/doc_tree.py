"""Placing a Doc Tree at a Destination: copy the tree, refusing any symlink within it.

The doc-tree slot names live in the [artifact contract](artifact.py); this module is the
placement side both Build (collecting a tree into the Unit) and Install (placing it at the
data dir) use to copy one, with the symlink refusal that a tree of prose should never trip.
"""

from __future__ import annotations

import shutil
from pathlib import Path


def install_doc_tree_at(source_path: Path, destination: Path) -> None:
    _refuse_symlinks_within(source_path)
    if destination.exists():
        shutil.rmtree(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_path, destination)


def _refuse_symlinks_within(root: Path) -> None:
    # A doc tree is prose for priming; copytree follows symlinks by default, so a committed link
    # (scaffold/doctrine/secret -> ~/.ssh/id_rsa, or a symlinked subdirectory) would read files from
    # outside the Contribution into the Artifact and on to every Destination. Refuse loudly instead.
    if root.is_symlink():
        raise DocTreeContainsSymlink(root)
    for path in root.rglob("*"):
        if path.is_symlink():
            raise DocTreeContainsSymlink(path)


class DocTreeContainsSymlink(RuntimeError):
    def __init__(self, path: Path) -> None:
        super().__init__(path)
        self.path = path

    def __str__(self) -> str:
        return (
            f"Doc Tree contains a symlink at {self.path}; refusing to follow it. A Doc Tree is "
            "prose for priming; following a symlink would copy files from outside the "
            "Contribution into the Artifact. Remove the symlink or commit the real file."
        )
