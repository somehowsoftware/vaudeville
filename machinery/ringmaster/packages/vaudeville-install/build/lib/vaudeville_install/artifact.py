"""The Artifact contract: the published shape of the Unit Build writes and Install reads.

This is the single definition both halves of the deploy speak: the layout the integrator
writes a Unit into and the installer reads it back from, plus the names that cross the seam.
It carries no behaviour and no I/O, so the integrator imports it to write a self-installing
Artifact without depending on any of the installer's placement machinery, and the installer
reads it with no reference back to the integrator.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

# The distribution name of the composed Facade the integrator carries in the Unit and the
# installer installs from the carried wheels. Shared across the seam.
FACADE_DISTRIBUTION = "vaudeville-vv"

# The doc-tree subtree names the integrator collects into the Unit and the installer places
# (and owns wholesale) under the data dir. The universal doctrine is placed here.
DOC_TREE_NAMES = ("doctrine",)

# Per-tenant / integrator state that is never a Contributor Data File: the Registry filename
# the integrator ships as its own package data, the project map `vv` resolves repos from, and
# the YouTrack credentials the installer's host-wiring check and `vv` read at runtime.
REGISTRY_FILENAME = "ringmaster.toml"
PROJECT_MAP_FILENAME = "vaudeville.toml"
CREDENTIALS_FILENAME = "credentials.toml"

# Names the installer owns at the top of the data dir: operator-managed state (the project map)
# and the framework-owned doc-tree subtrees the installer rebuilds wholesale, plus the Registry's
# name. A Contributor shipping any of these as a flat Data File would clobber operator state, place
# a file where a doc-tree directory belongs, or shadow the Registry; discovery refuses them so the
# collision surfaces as an incomplete Contribution rather than a corrupted data dir.
RESERVED_FILENAMES = frozenset({REGISTRY_FILENAME, PROJECT_MAP_FILENAME, *DOC_TREE_NAMES})

# The literal placeholder a Contributor writes in its hook commands for the deployed hooks
# directory; the installer substitutes the Destination's absolute hooks path at placement time.
HOOKS_DIR_PLACEHOLDER = "$VV_HOOKS_DIR"


def is_reserved_data_file_name(name: str) -> bool:
    return name in RESERVED_FILENAMES


@dataclass(frozen=True)
class Artifact:
    root: Path

    @property
    def skills(self) -> Path:
        return self.root / "skills"

    @property
    def data_files(self) -> Path:
        return self.root / "data"

    @property
    def doc_trees(self) -> Path:
        return self.root / "doc-trees"

    @property
    def hooks(self) -> Path:
        return self.root / "hooks"

    @property
    def hook_matchers(self) -> Path:
        return self.root / "hook-matchers.json"

    @property
    def carried_cli(self) -> Path:
        return self.root / "cli"
