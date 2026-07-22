# The reserved home for tenant `vaudeville.toml` schema migrations, run inside `vaudeville update`.
# A no-op today (one schema), named now and not built. The seam sits between acquiring the new
# Artifact and activating it, before the new tools are placed, so a migration that cannot apply
# aborts while the host still runs its old install. A real migration will hand judgment to an agent
# or abort loud — never silently rewrite the operator's version-controlled config, never a thicket
# of special cases. That is why this is a seam and not a migration engine.

from __future__ import annotations

from pathlib import Path


def migrate_tenant_config(config_dir: Path) -> None:
    return None
