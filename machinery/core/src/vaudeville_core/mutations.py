"""Write paths through the anti-corruption layer.

Consumers ask vaudeville-core to create / transition / annotate Assignments
in Vaudeville vocabulary.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from vaudeville_core import _youtrack
from vaudeville_core.backend import Request
from vaudeville_core.component import prefixes, tracker_project_id_for_prefix
from vaudeville_core.config_file import (
    VAUDEVILLE_FILENAME,
    _abort,
    host_config_path,
    load_config,
)


def create_assignment_request(
    tracker_project_id: str,
    *,
    summary: str,
    description: str,
    route: str,
    type: str = "Premise",
    workflow: str = "Submitted",
) -> Request:
    return Request(
        "POST",
        "/issues",
        {
            "project": {"id": tracker_project_id},
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


def command_request(query: str, assignment_id: str) -> Request:
    return Request("POST", "/commands", {"query": query, "issues": [{"idReadable": assignment_id}]})


def claim_assignment_request(assignment_id: str) -> Request:
    return command_request("state Active Workflow Claimed", assignment_id)


def add_depend_request(source: str, target: str) -> Request:
    return command_request(f"depends on {target}", source)


def remove_depend_request(source: str, target: str) -> Request:
    return command_request(f"remove depends on {target}", source)


def attach_subtask_request(child: str, parent: str) -> Request:
    return command_request(f"subtask of {parent}", child)


def add_comment_request(assignment_id: str, body: str) -> Request:
    return Request("POST", f"/issues/{assignment_id}/comments", {"text": body})


def sign_off_request(assignment_id: str) -> Request:
    return Request(
        "POST",
        f"/issues/{assignment_id}",
        {"customFields": [_single_enum("Signed off", "Yes")]},
        params={"fields": "idReadable"},
    )


def create_assignment(
    component: str,
    *,
    summary: str,
    description: str,
    route: str,
    type: str = "Premise",
    workflow: str = "Submitted",
    host_config_dir: Path | None = None,
) -> str:
    """Create an Assignment and return its idReadable.

    ``component`` is the Vaudeville short-name (e.g. ``BOB``). The consumer
    does not supply or see a YouTrack opaque project id; vaudeville-core
    resolves the short-name internally.
    """
    tracker_id = _tracker_project_id(component, host_config_dir)
    response = _youtrack.perform(
        create_assignment_request(
            tracker_id,
            summary=summary,
            description=description,
            route=route,
            type=type,
            workflow=workflow,
        )
    )
    if not isinstance(response, dict) or "idReadable" not in response:
        print(
            f"Error: backend returned unexpected payload on create: {response!r}",
            file=sys.stderr,
        )
        sys.exit(1)
    return str(response["idReadable"])


def claim_assignment(assignment_id: str) -> None:
    """Transition State→Active and Workflow→Claimed for ``assignment_id``."""
    _youtrack.perform(claim_assignment_request(assignment_id))


def add_comment(assignment_id: str, body: str) -> None:
    """Append a comment to ``assignment_id``."""
    _youtrack.perform(add_comment_request(assignment_id, body))


def sign_off(assignment_id: str) -> None:
    """Mark ``assignment_id`` signed off: the operator's go-ahead that admits a
    Command or Manual to the pickup pool. Premise and Direction are pickable
    without it; for them sign-off is irrelevant, not required.
    """
    _youtrack.perform(sign_off_request(assignment_id))


def add_depend(source: str, target: str) -> None:
    """Make ``source`` depend on ``target``. Idempotent."""
    _youtrack.perform(add_depend_request(source, target))


def remove_depend(source: str, target: str) -> None:
    """Remove ``source``'s ``depends on `target`` edge. Idempotent."""
    _youtrack.perform(remove_depend_request(source, target))


def attach_subtask(child: str, parent: str) -> None:
    """Make ``child`` a Subtask of ``parent``. Idempotent."""
    _youtrack.perform(attach_subtask_request(child, parent))


def _tracker_project_id(short_name: str, host_config_dir: Path | None = None) -> str:
    """Resolve a Vaudeville short-name to the tracker's opaque project id.

    The opaque id is what the backend POST needs; it never leaves CORE.
    """
    config = load_config(host_config_dir)
    tracker_id = tracker_project_id_for_prefix(config, short_name)
    if tracker_id is None:
        known = ", ".join(prefixes(config)) or "<empty>"
        register = host_config_path(VAUDEVILLE_FILENAME, host_config_dir)
        _abort(f"Component {short_name!r} not in {register} (known: {known})")
    return tracker_id


def _single_enum(name: str, value: str) -> dict[str, Any]:
    return {"name": name, "$type": "SingleEnumIssueCustomField", "value": {"name": value}}
