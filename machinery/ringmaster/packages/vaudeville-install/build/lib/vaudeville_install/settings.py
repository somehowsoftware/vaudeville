"""The Vaudeville-managed settings.json envelope: Ringmaster owns the ``hooks`` and ``autoMode``.

An operator's own ``autoMode`` rules live in ``settings.local.json``, a scope the classifier
combines and Install never writes, so the wholesale-owned key needs no merge with the operator's.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any


def vaudeville_managed_settings(
    base: Mapping[str, Any],
    *,
    hooks: dict[str, list[Any]],
    auto_mode: Mapping[str, Any],
) -> dict[str, Any]:
    managed = {**base, "hooks": hooks}
    if auto_mode:
        managed["autoMode"] = dict(auto_mode)
    else:
        managed.pop("autoMode", None)
    return managed


def write_vaudeville_managed_settings(
    destination_path: Path,
    *,
    hooks: dict[str, list[Any]],
    auto_mode: Mapping[str, Any],
    base_settings_path: Path | None = None,
) -> None:
    base_path = base_settings_path if base_settings_path is not None else destination_path
    base = json.loads(base_path.read_text()) if base_path.is_file() else {}
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    with destination_path.open("w") as f:
        json.dump(vaudeville_managed_settings(base, hooks=hooks, auto_mode=auto_mode), f, indent=2)
