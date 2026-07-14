"""Read paths through the anti-corruption layer.

Consumers ask for Assignments in Vaudeville vocabulary; this module turns
those requests into backend queries, fetches raw payloads via the
private YouTrack client, and adapts them to ``Assignment`` value objects.
The dict shape never escapes the module.
"""

from __future__ import annotations

import sys
from collections.abc import Iterable
from typing import Any

from vaudeville_core import _issue_adapter, _youtrack
from vaudeville_core.assignments import Assignment, AssignmentRef, Comment
from vaudeville_core.backend import Request


def search_query(
    *,
    component: str | None = None,
    type: Iterable[str] | None = None,
    state: Iterable[str] | None = None,
    workflow: Iterable[str] | None = None,
    route: Iterable[str] | None = None,
    resolved: bool | None = None,
) -> str:
    """The backend search query for a Vaudeville-primitive filter.

    Each keyword constrains a single custom field. Multiple values
    within a keyword are an OR; multiple keywords AND together. The
    ``resolved`` keyword filters on the State's ``isResolved`` flag:
    True for closed (Delivered/Abandoned), False for open.
    """
    clauses: list[str] = []
    if component is not None:
        clauses.append(f"project: {component}")
    for field, values in (
        ("Type", type),
        ("State", state),
        ("Workflow", workflow),
        ("Route", route),
    ):
        if values is None:
            continue
        materialised = list(values)
        if not materialised:
            continue
        clauses.append(f"{field}: {', '.join(materialised)}")
    if resolved is True:
        clauses.append("#Resolved")
    elif resolved is False:
        clauses.append("#Unresolved")
    return " ".join(clauses)


def find_assignments(
    *,
    component: str | None = None,
    type: Iterable[str] | None = None,
    state: Iterable[str] | None = None,
    workflow: Iterable[str] | None = None,
    route: Iterable[str] | None = None,
    resolved: bool | None = None,
) -> list[Assignment]:
    """Enumerate Assignments matching the given Vaudeville-primitive filter."""
    query = search_query(
        component=component,
        type=type,
        state=state,
        workflow=workflow,
        route=route,
        resolved=resolved,
    )
    raw_issues = _youtrack.search(query, _issue_adapter.FIELDS)
    return [_assignment_from_issue(issue) for issue in raw_issues]


def get_assignment_request(assignment_id: str) -> Request:
    return Request(
        "GET",
        f"/issues/{assignment_id}",
        params={"fields": _issue_adapter.FIELDS},
        allow_404=True,
    )


def get_assignment(assignment_id: str) -> Assignment:
    """Fetch one Assignment by Vaudeville Assignment id (e.g. ``BOB-26``)."""
    issue = _youtrack.perform(get_assignment_request(assignment_id))
    if issue is None:
        print(f"Error: assignment {assignment_id!r} not found.", file=sys.stderr)
        sys.exit(1)
    return _assignment_from_issue(issue)


def _assignment_from_issue(issue: dict[str, Any]) -> Assignment:
    """Adapt a raw YouTrack issue dict to an Assignment. CORE-internal."""
    buckets: dict[tuple[str, str], list[AssignmentRef]] = {
        ("Depend", "INWARD"): [],
        ("Depend", "OUTWARD"): [],
        ("Subtask", "INWARD"): [],
        ("Subtask", "OUTWARD"): [],
        ("Duplicate", "INWARD"): [],
        ("Duplicate", "OUTWARD"): [],
    }
    for link in issue.get("links", []):
        key = (
            (link.get("linkType") or {}).get("name", ""),
            link.get("direction", ""),
        )
        bucket = buckets.get(key)
        if bucket is None:
            continue
        for ref in link.get("issues", []):
            bucket.append(
                AssignmentRef(
                    id=str(ref.get("idReadable", "")),
                    state_resolved=_issue_adapter.state_resolved(ref),
                )
            )
    return Assignment(
        id=str(issue.get("idReadable", "")),
        summary=str(issue.get("summary", "")),
        description=str(issue.get("description") or ""),
        type=_issue_adapter.field_name(issue, "Type"),
        state=_issue_adapter.field_name(issue, "State"),
        workflow=_issue_adapter.field_name(issue, "Workflow"),
        route=_issue_adapter.field_name(issue, "Route"),
        state_resolved=_issue_adapter.state_resolved(issue),
        signed_off=_issue_adapter.signed_off(issue),
        deps_inward=tuple(buckets[("Depend", "INWARD")]),
        deps_outward=tuple(buckets[("Depend", "OUTWARD")]),
        subtask_inward=tuple(buckets[("Subtask", "INWARD")]),
        subtask_outward=tuple(buckets[("Subtask", "OUTWARD")]),
        duplicates_inward=tuple(buckets[("Duplicate", "INWARD")]),
        duplicates_outward=tuple(buckets[("Duplicate", "OUTWARD")]),
        comments=tuple(
            Comment(
                author=_issue_adapter.comment_author(comment),
                text=str(comment.get("text") or ""),
                created=int(comment.get("created") or 0),
            )
            for comment in issue.get("comments", [])
        ),
    )
