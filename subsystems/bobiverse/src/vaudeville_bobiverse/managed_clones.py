from __future__ import annotations

from pathlib import Path

from vaudeville_core import component_from_prefix, list_components


def managed_clones() -> list[Path]:
    # The host's every Component clone. Spawn and bob both reset this set
    # to clean origin/main before forking, so it is a shared host-resolution piece
    # like data_dir: owned by neither pipeline.
    return [component_from_prefix(prefix).repo_path for prefix in list_components()]
