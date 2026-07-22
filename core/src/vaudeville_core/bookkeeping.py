from __future__ import annotations

from vaudeville_core import _youtrack
from vaudeville_core.backend import Request
from vaudeville_core.profiles import ExitProfile


def comment_text(profile: ExitProfile, reason: str) -> str:
    return f"{profile.comment_header}\n\n{reason.strip()}\n"


def field_updates(profile: ExitProfile) -> list[dict[str, object]]:
    workflow_value: dict[str, str] | None = (
        {"name": profile.workflow_name} if profile.workflow_name is not None else None
    )
    return [
        {"name": "State", "$type": "StateIssueCustomField", "value": {"name": profile.state_name}},
        {"name": "Workflow", "$type": "SingleEnumIssueCustomField", "value": workflow_value},
    ]


def transition_request(assignment_id: str, profile: ExitProfile) -> Request:
    return Request("POST", f"/issues/{assignment_id}", {"customFields": field_updates(profile)})


def bookkeeping_requests(assignment_id: str, profile: ExitProfile, reason: str) -> list[Request]:
    requests: list[Request] = []
    if profile.comment_header:
        comment = {"text": comment_text(profile, reason)}
        requests.append(Request("POST", f"/issues/{assignment_id}/comments", comment))
    requests.append(transition_request(assignment_id, profile))
    return requests


def apply_bookkeeping(assignment_id: str, profile: ExitProfile, reason: str) -> None:
    for request in bookkeeping_requests(assignment_id, profile, reason):
        _youtrack.perform(request)


def apply_transition(assignment_id: str, profile: ExitProfile) -> None:
    _youtrack.perform(transition_request(assignment_id, profile))
