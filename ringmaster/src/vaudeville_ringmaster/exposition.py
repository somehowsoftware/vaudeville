"""The Exposition: a for-reading rendering of the integrated source, committed beside a Release."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from vaudeville_ringmaster.provenance import PROVENANCE_FILENAME
from vaudeville_ringmaster.session_clone import SessionClone

# The Contributor whose readable material lives entirely under `scaffold/` rather than in a `src`,
# `docs`, and `README` of its own, so it takes the doctrine translation below rather than the
# default. The one editorial choice the Exposition still makes.
VAUDEVILLE_DOCTRINE_CONTRIBUTOR = "vaudeville-doctrine"

# The Exposition lifts each Contributor's readable material into a directory named for the
# Contributor, out of the source-side Contribution Layout (`scaffold/.claude/…`, `.vaudeville/…`)
# that files it for the build. Each pair below maps a source-relative path to where it lands under
# that directory. This whitelist is the reading copy's domain: a source path named by no pair is
# omitted by construction, so tests, tooling, lockfiles, history, hook scripts, and Data Files never
# leak in, and a skill is lifted to `skills/` rather than left buried under `scaffold/.claude/`.
_DEFAULT_READABLE_MATERIAL: tuple[tuple[Path, Path], ...] = (
    (Path("src"), Path("src")),
    (Path("packages"), Path("packages")),
    (Path("docs"), Path("docs")),
    (Path("README.md"), Path("README.md")),
    (Path("scaffold") / ".claude" / "skills", Path("skills")),
)

# The doctrine Contributor carries no top-level `src`/`docs`/`README`; its prose lives under
# `scaffold/`. Its readable slots are named the same way — never a blind copy of `scaffold/`, so
# future plumbing added there is omitted by construction like everyone else's. The `doctrine/` Doc
# Tree lands at `doctrine/doctrine/`, so a `doctrine/...` link from the prose beside it resolves
# unchanged, exactly as in the repo.
_DOCTRINE_READABLE_MATERIAL: tuple[tuple[Path, Path], ...] = (
    (Path("scaffold") / "doctrine", Path("doctrine")),
    (Path("scaffold") / "README.md", Path("README.md")),
    (Path("scaffold") / "map.md", Path("map.md")),
    (Path("scaffold") / "theory", Path("theory")),
    (Path("scaffold") / "diagrams", Path("diagrams")),
)


@dataclass(frozen=True)
class ReadablePart:
    # A piece of a Contributor's readable material and where it is presented in the reading copy:
    # `source` is an absolute path in the Session Clone, `reader_path` is relative to the Exposition
    # root (`<contributor>/<slot>`).
    source: Path
    reader_path: Path


@dataclass(frozen=True)
class Exposition:
    root: Path

    @property
    def provenance(self) -> Path:
        return self.root / PROVENANCE_FILENAME


def render_exposition(
    session_clones: list[SessionClone],
    into: Path,
    *,
    doctrine_contributor: str | None,
    provenance_text: str,
) -> Exposition:
    into.mkdir(parents=True, exist_ok=True)
    for clone in session_clones:
        for part in readable_parts_of(clone, doctrine_contributor=doctrine_contributor):
            _copy_readable_part(part, into)
    (into / PROVENANCE_FILENAME).write_text(provenance_text)
    return Exposition(root=into)


def readable_parts_of(
    clone: SessionClone, *, doctrine_contributor: str | None
) -> list[ReadablePart]:
    material = (
        _DOCTRINE_READABLE_MATERIAL
        if clone.name == doctrine_contributor
        else _DEFAULT_READABLE_MATERIAL
    )
    directory = Path(_display_name(clone.name))
    return [
        ReadablePart(source=clone.path / source_relative, reader_path=directory / reader_relative)
        for source_relative, reader_relative in material
    ]


def _copy_readable_part(part: ReadablePart, into: Path) -> None:
    # A named slot absent from a given Contributor (a Component with no `packages/`, say) is simply
    # not there to copy; only present material renders.
    source = part.source
    # `is_symlink` before `is_dir`/`is_file`, which follow the link: a slot that is itself a symlink
    # would otherwise have its target's contents copied into the rendering.
    if source.is_symlink():
        raise ExpositionContainsSymlink(source)
    destination = into / part.reader_path
    if source.is_dir():
        _refuse_symlinks_within(source)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, destination, symlinks=True)
    elif source.is_file():
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def _refuse_symlinks_within(root: Path) -> None:
    # The Exposition is committed to the Published Home. A committed symlink in a Contributor's
    # source would leak a host-local path (or, when followed, its target's contents) into the
    # release; refuse it loudly.
    for descendant in root.rglob("*"):
        if descendant.is_symlink():
            raise ExpositionContainsSymlink(descendant)


def _display_name(contributor_name: str) -> str:
    # The Contributor directory drops the federation's `vaudeville-` prefix: a reader browsing the
    # Exposition wants `bobiverse`, not `vaudeville-bobiverse`.
    return contributor_name.removeprefix("vaudeville-")


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
