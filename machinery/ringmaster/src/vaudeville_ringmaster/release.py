"""The Release: a Pinned Set published under a Release Name (the integrated whole, versioned)."""

from __future__ import annotations

from dataclasses import dataclass

from vaudeville_ringmaster.provenance import Provenance
from vaudeville_ringmaster.release_name import ReleaseName


@dataclass(frozen=True)
class Release:
    name: ReleaseName
    provenance: Provenance
    landed_commit: str
