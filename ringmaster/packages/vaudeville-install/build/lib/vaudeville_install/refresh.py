"""Refresh: reconcile the tenant's data-dir config after install, repriming only when it must.

It exists because the config drifts between deploys — a tenant edits its project docs, adds a repo,
rotates a token — and reinstalling the whole framework to carry those edits across is the heavy path
(``vaudeville update``); Refresh is the light one, touching only the placed Tenant Config with no
Artifact present.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from vaudeville_install.artifact import CREDENTIALS_FILENAME, PROJECT_MAP_FILENAME
from vaudeville_install.destination import Layout
from vaudeville_install.host_vv import RunVv
from vaudeville_install.host_wiring import read_youtrack_credentials
from vaudeville_install.placement import PROJECT_DOCS_DIRNAME, place_config
from vaudeville_install.prime_foundations import prime_foundations
from vaudeville_install.priming_watermark import (
    PrimingWatermark,
    project_docs_fingerprint,
    project_map_fingerprint,
    read_priming_watermark,
)
from vaudeville_install.tenant_config import TenantConfigUnreadable, project_remotes


@dataclass(frozen=True)
class RefreshPlan:
    changed_project_docs: frozenset[str]
    project_map_changed: bool

    @property
    def reprime_needed(self) -> bool:
        # ``vv prime`` reads the project map (to enumerate the Components it primes) and the
        # project-docs (to prime each), and nothing else Refresh places — so a changed doc or a map
        # that gained or dropped a Component leaves the Foundations stale, while a rotated
        # credential never does. (vv prime's read-set is bobiverse's contract, verified at origin.)
        return bool(self.changed_project_docs) or self.project_map_changed


def refresh_plan_for(config_dir: Path, layout: Layout) -> RefreshPlan:
    _require_config_sources(config_dir)
    watermark = read_priming_watermark(layout)
    return RefreshPlan(
        changed_project_docs=_docs_changed_since_priming(
            config_dir / PROJECT_DOCS_DIRNAME, watermark
        ),
        project_map_changed=_map_changed_since_priming(
            config_dir / PROJECT_MAP_FILENAME, watermark
        ),
    )


def _require_config_sources(config_dir: Path) -> None:
    # place_config copies the project map and credentials wholesale without parsing, so a missing or
    # malformed one would half-apply the Refresh or place config `vv` cannot read. Validate both
    # here — the one gate a dry run and an apply share — through the install's own readers, so a bad
    # file raises a legible TenantConfigUnreadable before any write.
    _require_readable(config_dir / PROJECT_MAP_FILENAME, lambda: project_remotes(config_dir))
    _require_readable(
        config_dir / CREDENTIALS_FILENAME,
        lambda: read_youtrack_credentials(config_dir / CREDENTIALS_FILENAME),
    )


def _require_readable(source: Path, read: Callable[[], object]) -> None:
    if not source.is_file():
        # The shared readers treat an absent file as nothing to read; a Refresh requires it, so name
        # the missing file here rather than let it fall through to the writer.
        raise TenantConfigUnreadable(source, FileNotFoundError("no such file"))
    try:
        read()
    except OSError as unreadable:
        # The shared reader wraps a decode error but lets an OS read error (an unreadable file)
        # escape; make it legible here too, still before any write.
        raise TenantConfigUnreadable(source, unreadable) from unreadable


def apply_refresh_plan(
    plan: RefreshPlan, config_dir: Path, layout: Layout, prime_vv: RunVv
) -> None:
    place_config(config_dir, layout)
    if plan.reprime_needed:
        prime_foundations(prime_vv, layout)


def _docs_changed_since_priming(config_docs: Path, watermark: PrimingWatermark) -> frozenset[str]:
    incoming = project_docs_fingerprint(config_docs)
    primed = watermark.project_docs
    return frozenset(
        relpath
        for relpath in incoming.keys() | primed.keys()
        if incoming.get(relpath) != primed.get(relpath)
    )


def _map_changed_since_priming(config_map: Path, watermark: PrimingWatermark) -> bool:
    return project_map_fingerprint(config_map) != watermark.project_map
