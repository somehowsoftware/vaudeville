"""The Release's Artifact in the Published Home: the versioned, downloadable Artifact."""

from __future__ import annotations

import tarfile
from pathlib import Path

from vaudeville_install.artifact import Artifact


def published_artifact_for(artifact: Artifact, asset_path: Path) -> Path:
    # Pack the Artifact's children by name, not the root as ".": the root is a 0700
    # TemporaryDirectory, and a "." entry would carry that mode into the archive, where
    # `tar -xzf -C <dir>` applies it to the Tenant's extraction directory. Adding each child by name
    # keeps the layout with no root entry to mutate the target.
    with tarfile.open(asset_path, "w:gz") as archive:
        for member in sorted(artifact.root.iterdir()):
            archive.add(member, arcname=member.name)
    return asset_path
