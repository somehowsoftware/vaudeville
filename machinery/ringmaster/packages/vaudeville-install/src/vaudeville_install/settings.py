"""The Vaudeville-managed settings.json: Ringmaster owns the ``hooks`` block, merged into a base."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any


def settings_with_hooks(
    base: Mapping[str, Any], hooks_block: dict[str, list[Any]]
) -> dict[str, Any]:
    return {**base, "hooks": hooks_block}


def write_settings_with_hooks(
    destination_path: Path,
    hooks_block: dict[str, list[Any]],
    base_settings_path: Path | None = None,
) -> None:
    base_path = base_settings_path if base_settings_path is not None else destination_path
    base = json.loads(base_path.read_text()) if base_path.is_file() else {}
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    with destination_path.open("w") as f:
        json.dump(settings_with_hooks(base, hooks_block), f, indent=2)
