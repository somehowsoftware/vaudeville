from __future__ import annotations

from pathlib import Path

from vaudeville_bobiverse.data_dir import data_dir

CONFIG_ORIGIN_FILENAME = ".config-origin"


class ConfigOriginUnrecorded(Exception):
    def __init__(self, origin: Path) -> None:
        super().__init__(
            f"This host has no recorded config dir ({origin} is absent), so there is no config "
            "repo to register a Component in. Pass --config-dir <path to your config repo>."
        )


def config_origin(declared: Path | None) -> Path:
    if declared is not None:
        return declared
    origin = data_dir() / CONFIG_ORIGIN_FILENAME
    if not origin.is_file():
        raise ConfigOriginUnrecorded(origin)
    recorded = origin.read_text().strip()
    if not recorded:
        raise ConfigOriginUnrecorded(origin)
    return Path(recorded)
