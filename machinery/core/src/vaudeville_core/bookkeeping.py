from __future__ import annotations

from collections.abc import Mapping
from typing import NamedTuple

from vaudeville_core import _youtrack
from vaudeville_core.profiles import ExitProfile


class Request(NamedTuple):
    method: str
    path: str
    json_body: Mapping[str, object]


def comment_text(profile: ExitProfile, reason: str) -> str:
    return f"{profile.comment_header}\n\n{reason.strip()}\n"


def field_updates(profile: ExitProfile) -> list[dict[str, object]]:
    workflow_value: dict[str, str] | None = (
        {"name": profile.workflow_name} if profile.workflow_name is not None else None
    )
    fields: list[dict[str, object]] = [
        {"name": "State", "$type": "StateIssueCustomField", "value": {"name": profile.state_name}},
        {"name": "Workflow", "$type": "SingleEnumIssueCustomField", "value": workflow_value},
    ]
    if profile.unassign:
        fields.append({"name": "Assignee", "$type": "SingleUserIssueCustomField", "value": None})
    return fields


def bookkeeping_requests(premise_id: str, profile: ExitProfile, reason: str) -> list[Request]:
    requests: list[Request] = []
    if profile.comment_header:
        comment = {"text": comment_text(profile, reason)}
        requests.append(Request("POST", f"/issues/{premise_id}/comments", comment))
    requests.append(
        Request("POST", f"/issues/{premise_id}", {"customFields": field_updates(profile)})
    )
    return requests


def apply_bookkeeping(premise_id: str, profile: ExitProfile, reason: str) -> None:
    for request in bookkeeping_requests(premise_id, profile, reason):
        _youtrack.request(request.method, request.path, json_body=request.json_body)


def apply_transition(premise_id: str, profile: ExitProfile) -> None:
    _youtrack.request(
        "POST", f"/issues/{premise_id}", json_body={"customFields": field_updates(profile)}
    )
