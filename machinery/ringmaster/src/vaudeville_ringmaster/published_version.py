"""The Published Version: the versioned, downloadable install Artifact in the Published Home."""

from __future__ import annotations

import tarfile
from collections.abc import Iterable
from datetime import date
from pathlib import Path

from vaudeville_install.artifact import Artifact

# The Published Home — where Published Versions accumulate.
PUBLISHED_HOME = "somehowsoftware/vaudeville"


def next_published_version(today: date, existing_tags: Iterable[str]) -> str:
    # Pad month and day so the release list sorts chronologically — unpadded, an October–December
    # tag would sort lexically before a single-digit month. (PEP 440 strips the padding from the
    # wheels' own versions, which sorts numerically anyway; the padding is the tag's, not the
    # package's.) The counter disambiguates same-day releases.
    base = f"v{today.year}.{today.month:02d}.{today.day:02d}"
    taken = set(existing_tags)
    counter = 1
    while f"{base}.{counter}" in taken:
        counter += 1
    return f"{base}.{counter}"


def published_version_asset_for(artifact: Artifact, asset_path: Path) -> Path:
    # Pack the Artifact's children by name, not the root as ".": the root is a 0700
    # TemporaryDirectory, and a "." entry would carry that mode into the archive, where
    # `tar -xzf -C <dir>` applies it to the Tenant's extraction directory. Adding each child by name
    # keeps the layout with no root entry to mutate the target.
    with tarfile.open(asset_path, "w:gz") as archive:
        for member in sorted(artifact.root.iterdir()):
            archive.add(member, arcname=member.name)
    return asset_path
