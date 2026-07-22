"""Substituting the deployed hooks-directory path into a Contributor's hook commands.

Build writes the merged Hook-Matcher fragment into the Artifact carrying the literal
``$VV_HOOKS_DIR`` placeholder; the installer substitutes the Destination's absolute hooks path
here as it materializes the Hook Wiring into the ``settings.json``. The placeholder spelling is the
shared one in the [artifact contract](artifact.py).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from vaudeville_install.artifact import HOOKS_DIR_PLACEHOLDER


def replace_hooks_dir_placeholder_in(content: Any, hooks_dir: Path) -> Any:
    if isinstance(content, dict):
        return {
            key: replace_hooks_dir_placeholder_in(value, hooks_dir)
            for key, value in content.items()
        }
    if isinstance(content, list):
        return [replace_hooks_dir_placeholder_in(item, hooks_dir) for item in content]
    if isinstance(content, str):
        return content.replace(HOOKS_DIR_PLACEHOLDER, str(hooks_dir))
    return content
