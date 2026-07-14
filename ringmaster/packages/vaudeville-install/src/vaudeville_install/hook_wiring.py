"""The Hook Wiring: the ``hooks`` block of the host ``settings.json``.

``hook_wiring_for`` materializes it every install from two sources of Hook Matchers — the
Contributor-sourced fragment merged into the [Artifact](artifact.py) and the tenant's own fragment
carried in its Tenant Config — with the deployed hooks-directory path substituted in.
``compose_hook_wiring`` is the pure fold of the two, mirroring how ``trust_declarations`` composes
an Owned settings block from a framework source and a tenant source: the tenant's matchers union
into the Contributor ones per event, so a tenant's own hooks go live alongside the stock hooks.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from vaudeville_install.artifact import Artifact
from vaudeville_install.hook_substitution import replace_hooks_dir_placeholder_in
from vaudeville_install.tenant_hooks import tenant_hook_matchers


def hook_wiring_for(artifact: Artifact, config_dir: Path, hooks_dir: Path) -> dict[str, list[Any]]:
    """Materialize the Hook Wiring for a deploy: fold the Artifact's Contributor-sourced matcher
    fragment with the tenant's own, then resolve the placeholder to the placed hooks directory."""
    composed = compose_hook_wiring(
        json.loads(artifact.hook_matchers.read_text()), tenant_hook_matchers(config_dir)
    )
    wired: dict[str, list[Any]] = replace_hooks_dir_placeholder_in(composed, hooks_dir)
    return wired


def compose_hook_wiring(
    artifact_matchers: dict[str, list[Any]], tenant_matchers: dict[str, list[Any]]
) -> dict[str, list[Any]]:
    composed: dict[str, list[Any]] = {
        event: list(entries) for event, entries in artifact_matchers.items()
    }
    for event, entries in tenant_matchers.items():
        composed.setdefault(event, []).extend(entries)
    return composed
