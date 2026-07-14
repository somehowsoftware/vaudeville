"""The settings.json write target: Install owns its ``hooks`` and ``autoMode`` keys.

Those two keys are Owned (rebuilt wholesale every install): ``hooks`` holds the Hook Wiring
materialized from the Hook Matchers, and ``autoMode`` holds the Trust Declarations. Every other
key is Curated, the operator's own and never touched. An operator's own ``autoMode`` rules live in
``settings.local.json``, a scope the classifier combines and Install never writes, so the Owned
``autoMode`` needs no merge with the operator's.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any


def owned_settings(
    base: Mapping[str, Any],
    *,
    hook_wiring: dict[str, list[Any]],
    trust_declarations: Mapping[str, Any],
) -> dict[str, Any]:
    settings = {**base, "hooks": hook_wiring}
    if trust_declarations:
        settings["autoMode"] = dict(trust_declarations)
    else:
        settings.pop("autoMode", None)
    return settings


def write_owned_settings(
    destination_path: Path,
    *,
    hook_wiring: dict[str, list[Any]],
    trust_declarations: Mapping[str, Any],
    base_settings_path: Path | None = None,
) -> None:
    base_path = base_settings_path if base_settings_path is not None else destination_path
    base = _curated_base(base_path)
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    with destination_path.open("w") as f:
        json.dump(
            owned_settings(base, hook_wiring=hook_wiring, trust_declarations=trust_declarations),
            f,
            indent=2,
        )


def _curated_base(base_path: Path) -> dict[str, Any]:
    # The operator's existing settings, read to preserve the Curated keys. A file that will not
    # parse must name itself, not surface a raw JSONDecodeError traceback out of the install.
    if not base_path.is_file():
        return {}
    try:
        curated: dict[str, Any] = json.loads(base_path.read_text())
    except json.JSONDecodeError as malformed:
        raise SettingsFileUnreadable(base_path, malformed) from malformed
    return curated


class SettingsFileUnreadable(RuntimeError):
    def __init__(self, path: Path, cause: Exception) -> None:
        super().__init__(path, cause)
        self.path = path
        self.cause = cause

    def __str__(self) -> str:
        return (
            f"The install cannot read the existing settings file {self.path} to preserve your "
            f"curated keys: {self.cause}. Fix the JSON (or move the file aside) and re-run the "
            "host install."
        )
