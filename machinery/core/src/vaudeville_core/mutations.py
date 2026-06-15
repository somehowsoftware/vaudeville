"""Write paths through the anti-corruption layer.

Consumers ask the kernel to create / transition / annotate Premises in
Vaudeville vocabulary. This module owns every backend write — the
private YouTrack client is reached only through helpers defined here.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from vaudeville_core import _youtrack
from vaudeville_core.config_file import (
    VAUDEVILLE_FILENAME,
    _abort,
    host_config_path,
    load_config,
)
from vaudeville_core.project import prefixes, tracker_project_id_for_prefix


def create_premise(
    project: str,
    *,
    summary: str,
    description: str,
    route: str,
    type: str = "Premise",
    workflow: str = "Submitted",
    host_config_dir: Path | None = None,
) -> str:
    """Create a Premise and return its idReadable.

    ``project`` is the Vaudeville short-name (e.g. ``BOB``). The
    consumer does not supply or see a YouTrack opaque project id —
    the kernel resolves the short-name internally.
    """
    tracker_id = _tracker_project_id(project, host_config_dir)
    response = _youtrack.request(
        "POST",
        "/issues",
        json_body={
            "project": {"id": tracker_id},
            "summary": summary,
            "description": description,
            "customFields": [
                _single_enum("Type", type),
                _single_enum("Route", route),
                _single_enum("Workflow", workflow),
            ],
        },
        params={"fields": "idReadable"},
    )
    if not isinstance(response, dict) or "idReadable" not in response:
        print(
            f"Error: backend returned unexpected payload on create: {response!r}",
            file=sys.stderr,
        )
        sys.exit(1)
    return str(response["idReadable"])


def claim_premise(premise_id: str) -> None:
    """Transition State→Active and Workflow→Claimed for ``premise_id``."""
    _run_command("state Active Workflow Claimed", premise_id)


def add_comment(premise_id: str, body: str) -> None:
    """Append a comment to ``premise_id``."""
    _youtrack.request("POST", f"/issues/{premise_id}/comments", json_body={"text": body})


def add_depend(source: str, target: str) -> None:
    """Make ``source`` depend on ``target``. Idempotent."""
    _run_command(f"depends on {target}", source)


def remove_depend(source: str, target: str) -> None:
    """Remove ``source``'s ``depends on `target`` edge. Idempotent."""
    _run_command(f"remove depends on {target}", source)


def attach_subtask(child: str, parent: str) -> None:
    """Make ``child`` a Subtask of ``parent``. Idempotent."""
    _run_command(f"subtask of {parent}", child)


def _tracker_project_id(short_name: str, host_config_dir: Path | None = None) -> str:
    """Resolve a Vaudeville short-name to the tracker's opaque project id.

    The opaque id is what the backend POST needs; it never leaves CORE.
    """
    config = load_config(host_config_dir)
    tracker_id = tracker_project_id_for_prefix(config, short_name)
    if tracker_id is None:
        known = ", ".join(prefixes(config)) or "<empty>"
        register = host_config_path(VAUDEVILLE_FILENAME, host_config_dir)
        _abort(f"project {short_name!r} not in {register} (known: {known})")
    return tracker_id


def _single_enum(name: str, value: str) -> dict[str, Any]:
    return {"name": name, "$type": "SingleEnumIssueCustomField", "value": {"name": value}}


def _run_command(query: str, premise_id: str) -> None:
    """POST to YouTrack's commands API for one Premise. Idempotent by design."""
    _youtrack.request(
        "POST",
        "/commands",
        json_body={"query": query, "issues": [{"idReadable": premise_id}]},
    )
