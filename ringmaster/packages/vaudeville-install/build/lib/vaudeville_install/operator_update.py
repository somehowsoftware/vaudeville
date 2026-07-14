from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from vaudeville_install.tenant_config_migration import migrate_tenant_config

# Acquire yields the unpacked Artifact root — the same `--artifact` root a first install is handed.
Acquire = Callable[[], Path]
# Activate installs that Artifact to the Host by activating its carried installer.
Activate = Callable[[Path], None]


def run_update(
    *,
    config_dir: Path,
    acquire: Acquire,
    activate: Activate,
    report: Callable[[str], None],
) -> None:
    artifact_root = acquire()
    migrate_tenant_config(config_dir)
    activate(artifact_root)
    report("The host now runs the newest framework Release.")
