"""The Exposition: a for-reading rendering of the assembled source, committed beside a Release."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from vaudeville_ringmaster.provenance import PROVENANCE_FILENAME
from vaudeville_ringmaster.registry import Registry
from vaudeville_ringmaster.session_clone import SessionClone

# The parts of a Contributor Repo the Exposition gathers — the source and prose that show the
# system, each copied only when present. `packages` carries workspace sub-packages a Contributor
# ships beyond its own `src`: vaudeville-ringmaster's carried installer (`vaudeville_install`) lives
# there and is built into every Artifact, so the rendering would omit shipped code without it. The
# whitelist is deliberate: it admits readable material and excludes everything else (tests, CI,
# lockfiles, caches, `.git`) by omission rather than blocklist, so new noise never leaks in.
RELEVANT_PARTS = ("src", "packages", "scaffold", "docs", "README.md")

# The doctrine Contributor's scaffold carries the agent doctrine as the `doctrine/` Doc Tree and its
# reading prose loose beside it.
_DOCTRINE_SCAFFOLD = "scaffold"
_DOCTRINE_DOC_TREE = "doctrine"


@dataclass(frozen=True)
class Section:
    name: str
    members: tuple[str, ...]


@dataclass(frozen=True)
class ExpositionLayout:
    subtree_sections: tuple[Section, ...]
    doctrine_contributor: str | None


@dataclass(frozen=True)
class Exposition:
    root: Path

    @property
    def provenance(self) -> Path:
        return self.root / PROVENANCE_FILENAME


VAUDEVILLE_EXPOSITION_LAYOUT = ExpositionLayout(
    subtree_sections=(
        Section(
            name="subsystems",
            members=("vaudeville-bobiverse", "vaudeville-pm", "vaudeville-cue"),
        ),
        Section(name="machinery", members=("vaudeville-ringmaster", "vaudeville-core")),
    ),
    doctrine_contributor="vaudeville-doctrine",
)


def render_exposition(
    layout: ExpositionLayout,
    registry: Registry,
    session_clones: list[SessionClone],
    into: Path,
    *,
    provenance_text: str,
) -> Exposition:
    _refuse_a_layout_that_does_not_cover_the_registry(layout, registry)
    clones_by_name = {clone.name: clone for clone in session_clones}
    into.mkdir(parents=True, exist_ok=True)
    for section in layout.subtree_sections:
        _place_section(section, clones_by_name, into)
    if layout.doctrine_contributor is not None:
        _place_doctrine(clones_by_name[layout.doctrine_contributor], into)
    (into / PROVENANCE_FILENAME).write_text(provenance_text)
    return Exposition(root=into)


def _place_section(section: Section, clones_by_name: dict[str, SessionClone], into: Path) -> None:
    for member in section.members:
        destination = into / section.name / _display_name(member)
        _gather_relevant_parts(clones_by_name[member].path, destination)


def _gather_relevant_parts(source_root: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for relative in RELEVANT_PARTS:
        source = source_root / relative
        # `is_symlink` before `is_dir`/`is_file`, which follow the link: a whitelisted entry that is
        # itself a symlink would otherwise have its target's contents copied into the rendering.
        if source.is_symlink():
            raise ExpositionContainsSymlink(source)
        if source.is_dir():
            _refuse_symlinks_within(source)
            shutil.copytree(source, destination / relative, symlinks=True)
        elif source.is_file():
            shutil.copy2(source, destination / relative)


def _place_doctrine(doctrine_clone: SessionClone, into: Path) -> None:
    scaffold = doctrine_clone.path / _DOCTRINE_SCAFFOLD
    doc_tree = scaffold / _DOCTRINE_DOC_TREE
    if doc_tree.is_symlink():
        raise ExpositionContainsSymlink(doc_tree)
    if not doc_tree.is_dir():
        raise DoctrineSourceMissing(doctrine_clone.name, doc_tree)
    _refuse_symlinks_within(doc_tree)
    shutil.copytree(doc_tree, into / _DOCTRINE_DOC_TREE, symlinks=True)
    # The reading prose loose beside the Doc Tree renders at the Exposition root, so its README is
    # the Published Home landing and a `doctrine/...` link from it resolves as it does in the repo.
    # Contribution slots (the dot-directories Build reads) are not prose and stay out of the root.
    for entry in sorted(scaffold.iterdir()):
        if entry.name == _DOCTRINE_DOC_TREE or entry.name.startswith("."):
            continue
        if entry.is_symlink():
            raise ExpositionContainsSymlink(entry)
        if entry.is_dir():
            _refuse_symlinks_within(entry)
            shutil.copytree(entry, into / entry.name, symlinks=True)
        else:
            shutil.copy2(entry, into / entry.name)


def _refuse_symlinks_within(root: Path) -> None:
    # The Exposition is committed to the Published Home. A committed symlink in a Contributor's
    # source would leak a host-local path (or, when followed, its target's contents) into the
    # release; refuse it loudly, the same discipline the Doc Tree copy enforces.
    for descendant in root.rglob("*"):
        if descendant.is_symlink():
            raise ExpositionContainsSymlink(descendant)


def _display_name(contributor_name: str) -> str:
    # The Section directory drops the federation's `vaudeville-` prefix: a reader browsing
    # `subsystems/` wants `bobiverse`, not `vaudeville-bobiverse`.
    return contributor_name.removeprefix("vaudeville-")


def _refuse_a_layout_that_does_not_cover_the_registry(
    layout: ExpositionLayout, registry: Registry
) -> None:
    placed = {member for section in layout.subtree_sections for member in section.members}
    if layout.doctrine_contributor is not None:
        placed.add(layout.doctrine_contributor)
    registered = set(registry.contributor_names())
    unplaced = registered - placed
    unknown = placed - registered
    if unplaced or unknown:
        raise ExpositionLayoutMismatch(unplaced, unknown)


class ExpositionLayoutMismatch(RuntimeError):
    def __init__(self, unplaced: set[str], unknown: set[str]) -> None:
        super().__init__(unplaced, unknown)
        self.unplaced = unplaced
        self.unknown = unknown

    def __str__(self) -> str:
        parts = []
        if self.unplaced:
            unplaced = ", ".join(sorted(self.unplaced))
            parts.append(f"registered Contributors left unplaced: {unplaced}")
        if self.unknown:
            unknown = ", ".join(sorted(self.unknown))
            parts.append(f"placed Contributors not in the Registry: {unknown}")
        detail = "; ".join(parts)
        return (
            f"The Exposition layout does not cover the Registry exactly ({detail}). "
            "Place every Contributor in exactly one Section."
        )


class DoctrineSourceMissing(RuntimeError):
    def __init__(self, name: str, source: Path) -> None:
        super().__init__(name, source)
        self.name = name
        self.source = source

    def __str__(self) -> str:
        return (
            f"The doctrine Contributor {self.name!r} carries no doctrine prose at {self.source}; "
            "the doctrine Section cannot be rendered."
        )


class ExpositionContainsSymlink(RuntimeError):
    def __init__(self, path: Path) -> None:
        super().__init__(path)
        self.path = path

    def __str__(self) -> str:
        return (
            f"A Contributor's source carries a symlink at {self.path}; refusing to render it into "
            "the Exposition. The Exposition is committed to the Published Home, so following the "
            "link would copy host-local files into the release. Remove the symlink or commit the "
            "real file."
        )
