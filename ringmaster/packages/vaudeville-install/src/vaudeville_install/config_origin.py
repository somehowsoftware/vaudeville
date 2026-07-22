from __future__ import annotations

from pathlib import Path

from vaudeville_install.destination import Layout

CONFIG_ORIGIN_FILENAME = ".config-origin"


class ConfigOriginUnrecorded(Exception):
    def __init__(self, data_dir: Path) -> None:
        super().__init__(
            f"This host has no recorded config dir ({data_dir / CONFIG_ORIGIN_FILENAME} is "
            "absent), so there is no safe source to sync from. Re-run with "
            "--config-dir <path to your config repo>; it is recorded for later runs."
        )


def config_origin(declared: Path | None, layout: Layout) -> Path:
    # A declared --config-dir stands (placement records it, so it answers for later runs); absent
    # one, the host's recorded origin answers. Neither is a refusal, never a guess: syncing a host
    # from a path no one on it ever named is the failure this abolishes.
    if declared is not None:
        return declared
    recorded = recorded_config_origin(layout)
    if recorded is None:
        raise ConfigOriginUnrecorded(layout.data_dir)
    return recorded


def record_config_origin(layout: Layout, config_dir: Path) -> None:
    layout.data_dir.mkdir(parents=True, exist_ok=True)
    (layout.data_dir / CONFIG_ORIGIN_FILENAME).write_text(f"{config_dir}\n")


def recorded_config_origin(layout: Layout) -> Path | None:
    origin = layout.data_dir / CONFIG_ORIGIN_FILENAME
    if not origin.is_file():
        return None
    recorded = origin.read_text().strip()
    return Path(recorded) if recorded else None
