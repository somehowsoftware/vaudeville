"""The Priming Watermark: the priming inputs — the project-docs tree and the project map — the
Foundations were last successfully primed from, recorded as host state and advanced only when a
prime succeeds.

Deriving the reprime decision from the placed copy instead is the trap this file exists to close:
apply places the inputs before it primes, so a prime that then fails leaves the placed copy equal to
the incoming inputs, and the next Refresh would see an empty delta and report success over stale
Foundations. Comparing against the watermark, which a failed prime leaves stale, keeps the reprime
owing until one takes.

A dotfile in the data dir: host-only installer bookkeeping, never a Contributor artifact and never
tenant config an operator edits.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from vaudeville_install.artifact import PROJECT_MAP_FILENAME
from vaudeville_install.destination import Layout
from vaudeville_install.placement import PROJECT_DOCS_DIRNAME

PRIMING_WATERMARK_FILENAME = ".priming-watermark.json"

_PROJECT_DOCS_KEY = "project-docs"
_PROJECT_MAP_KEY = "project-map"


@dataclass(frozen=True)
class PrimingWatermark:
    project_docs: dict[str, str]
    project_map: str | None


def project_docs_fingerprint(docs_root: Path) -> dict[str, str]:
    if not docs_root.is_dir():
        return {}
    return {
        str(path.relative_to(docs_root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(docs_root.rglob("*"))
        if path.is_file()
    }


def project_map_fingerprint(map_file: Path) -> str | None:
    # One opaque digest of the map's bytes, or None when absent — not a parse: the map's schema is
    # the tenant's, and Refresh needs only whether it changed, so any edit reprimes.
    if not map_file.is_file():
        return None
    return hashlib.sha256(map_file.read_bytes()).hexdigest()


def read_priming_watermark(layout: Layout) -> PrimingWatermark:
    watermark = layout.data_dir / PRIMING_WATERMARK_FILENAME
    if not watermark.is_file():
        return PrimingWatermark(project_docs={}, project_map=None)
    recorded = json.loads(watermark.read_text())
    docs = recorded.get(_PROJECT_DOCS_KEY, {})
    recorded_map = recorded.get(_PROJECT_MAP_KEY)
    return PrimingWatermark(
        project_docs={str(relpath): str(digest) for relpath, digest in docs.items()},
        project_map=str(recorded_map) if recorded_map is not None else None,
    )


def record_priming_watermark(layout: Layout) -> None:
    fingerprint = {
        _PROJECT_DOCS_KEY: project_docs_fingerprint(layout.data_dir / PROJECT_DOCS_DIRNAME),
        _PROJECT_MAP_KEY: project_map_fingerprint(layout.data_dir / PROJECT_MAP_FILENAME),
    }
    layout.data_dir.mkdir(parents=True, exist_ok=True)
    watermark = layout.data_dir / PRIMING_WATERMARK_FILENAME
    watermark.write_text(json.dumps(fingerprint, indent=2, sort_keys=True) + "\n")
