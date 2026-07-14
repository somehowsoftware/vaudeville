# The Artifact contract: the published shape Build writes and Install reads — the one definition
# both halves speak. It carries no behaviour and no I/O, so each half imports it without depending
# on the other's machinery.

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

# The distribution name of the Composed CLI the integrator carries in the Artifact and the
# installer installs from the carried wheels. Shared across the seam; the constant keeps the
# integrator's name for its Build-side Facade genus, which does not cross into installer voice.
FACADE_DISTRIBUTION = "vaudeville-vv"

# The distribution that carries the integrator's operator app (`vaudeville refresh`). The integrator
# is build-time tooling the Artifact never carries, so its operator code rides in this installer
# instead; the Composed CLI depends on this carried distribution, not on the uncarried integrator.
INSTALLER_DISTRIBUTION = "vaudeville-install"

# The doc-tree subtree names the integrator collects into the Artifact and the installer places
# (and owns wholesale) under the data dir. The universal doctrine is placed here.
DOC_TREE_NAMES = ("doctrine",)

# Per-tenant / integrator state that is never a Contributor Data File: the Registry filename
# the integrator ships as its own package data, the project map `vv` resolves repos from, and
# the YouTrack credentials the installer's host-wiring check and `vv` read at runtime.
REGISTRY_FILENAME = "ringmaster.toml"
PROJECT_MAP_FILENAME = "vaudeville.toml"
CREDENTIALS_FILENAME = "credentials.toml"

REQUIRED_TENANT_CONFIG_FILENAMES = (PROJECT_MAP_FILENAME, CREDENTIALS_FILENAME)

# Names the installer owns at the top of the data dir: operator-managed state (the project map)
# and the framework-owned doc-tree subtrees the installer rebuilds wholesale, plus the Registry's
# name. A Contributor shipping any of these as a flat Data File would clobber operator state, place
# a file where a doc-tree directory belongs, or shadow the Registry; discovery refuses them so the
# collision surfaces as an incomplete Contribution rather than a corrupted data dir.
RESERVED_FILENAMES = frozenset({REGISTRY_FILENAME, PROJECT_MAP_FILENAME, *DOC_TREE_NAMES})
_RESERVED_FILENAMES_CASEFOLDED = frozenset(name.casefold() for name in RESERVED_FILENAMES)

# The literal placeholder a Contributor writes in its hook commands for the deployed hooks
# directory; the installer substitutes the Destination's absolute hooks path at placement time.
HOOKS_DIR_PLACEHOLDER = "$VV_HOOKS_DIR"


def is_reserved_data_file_name(name: str) -> bool:
    # Case-folded: on a case-insensitive filesystem a name differing from a Reserved Name only in
    # case is the same file, so it must be refused too rather than slip through to clobber state.
    return name.casefold() in _RESERVED_FILENAMES_CASEFOLDED


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
