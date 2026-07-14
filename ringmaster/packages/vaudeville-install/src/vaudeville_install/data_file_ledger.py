"""The data-file ledger: what a prior Host Install placed, so the next prunes only its own files."""

from __future__ import annotations

from pathlib import Path

_MARKER_FILENAME = ".apply-installed-data-files"


def data_files_to_prune(previously_placed: set[str], keeping: set[str]) -> set[str]:
    return previously_placed - keeping


def prune_data_files_a_prior_install_placed(data_dir: Path, keeping: set[str]) -> None:
    # A file not named in the marker is operator-curated and never touched.
    marker = data_dir / _MARKER_FILENAME
    if not marker.is_file():
        return
    previously_placed = {line for line in marker.read_text().splitlines() if line}
    for name in data_files_to_prune(previously_placed, keeping):
        stale = data_dir / name
        if stale.is_file():
            stale.unlink()


def record_placed_data_files(data_dir: Path, placed: list[str]) -> None:
    (data_dir / _MARKER_FILENAME).write_text("\n".join(placed) + "\n")
