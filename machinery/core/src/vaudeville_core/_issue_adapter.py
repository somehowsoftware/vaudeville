"""YouTrack issue-dict accessors. CORE-internal.

The anti-corruption layer adapts raw YouTrack `/issues` payloads to
the Vaudeville `Premise` domain type. These accessors are the low-level
glue: one tier above the JSON shape, one tier below the consumer-facing
`Premise`. Consumers never import this module — they receive `Premise`
objects from `vaudeville_core.premises`.
"""

from __future__ import annotations

from typing import Any

# YouTrack `fields` query value: id, summary, custom fields, linked issues
# (with the resolved flag on their State), and the comment thread (text,
# author display, creation stamp). The Premise adapter in `queries.py`
# passes this to `_youtrack.search` / `_youtrack.request` so the returned
# dict matches what the accessors below assume.
FIELDS = (
    "idReadable,summary,description,"
    "customFields(name,value(name,isResolved)),"
    "links(direction,linkType(name),"
    "issues(idReadable,customFields(name,value(name,isResolved)))),"
    "comments(text,author(login,fullName),created)"
)


def field_value(issue: dict[str, Any], field: str) -> dict[str, Any]:
    for cf in issue.get("customFields", []):
        if cf.get("name") == field and cf.get("value"):
            return dict(cf["value"])
    return {}


def field_name(issue: dict[str, Any], field: str) -> str:
    return str(field_value(issue, field).get("name", ""))


def state_resolved(issue: dict[str, Any]) -> bool:
    return bool(field_value(issue, "State").get("isResolved"))


def linked(issue: dict[str, Any], link_type: str, direction: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for link in issue.get("links", []):
        if link.get("direction") != direction:
            continue
        if link.get("linkType", {}).get("name") != link_type:
            continue
        out.extend(link.get("issues", []))
    return out


def tag_names(issue: dict[str, Any]) -> list[str]:
    return [str(tag.get("name", "")) for tag in issue.get("tags", [])]


def comment_author(comment: dict[str, Any]) -> str:
    author = comment.get("author") or {}
    return str(author.get("fullName") or author.get("login") or "")
