from __future__ import annotations

import tomllib
from pathlib import Path

from vaudeville_install.artifact import PROJECT_MAP_FILENAME, REQUIRED_TENANT_CONFIG_FILENAMES


def project_remotes(config_dir: Path) -> list[str]:
    project_map = config_dir / PROJECT_MAP_FILENAME
    if not project_map.is_file():
        # An absent Project Map is nothing to do here; placement reports the missing file where it
        # copies it. Only a present-but-malformed one raises.
        return []
    try:
        with project_map.open("rb") as handle:
            projects = tomllib.load(handle).get("projects", {})
    except tomllib.TOMLDecodeError as malformed:
        raise TenantConfigUnreadable(project_map, malformed) from malformed
    if not isinstance(projects, dict):
        # A wrong-shape ``projects`` (a TOML array or scalar, not a table) is malformed, not "no
        # remotes". Reading it as empty would skip the pre-Priming preflight and copy the broken
        # file to the Host, only to fail later with the opaque error this reader exists to pre-empt.
        shape = type(projects).__name__
        raise TenantConfigUnreadable(
            project_map,
            TypeError(f"its `projects` value is a {shape}, not a table of projects"),
        )
    return [
        table["remote"]
        for table in projects.values()
        if isinstance(table, dict) and isinstance(table.get("remote"), str)
    ]


def raise_if_required_tenant_config_missing(config_dir: Path) -> None:
    for name in REQUIRED_TENANT_CONFIG_FILENAMES:
        source = config_dir / name
        if not source.is_file():
            raise TenantConfigUnreadable(
                source, FileNotFoundError("no such file in the config dir")
            )


class TenantConfigUnreadable(RuntimeError):
    def __init__(self, path: Path, cause: Exception) -> None:
        super().__init__(path, cause)
        self.path = path
        self.cause = cause

    def __str__(self) -> str:
        return (
            f"The install cannot read the Tenant Config file {self.path}: {self.cause}. It holds "
            "the Project Map and Tracker Credentials `vv` resolves the tenant's repos and tracker "
            "from; provide a readable, well-formed file and re-run the host install."
        )
