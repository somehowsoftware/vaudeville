"""YouTrack issue-dict accessors. CORE-internal.

The anti-corruption layer adapts raw YouTrack `/issues` payloads to
the Vaudeville `Assignment` domain type. These accessors are the low-level
glue: one tier above the JSON shape, one tier below the consumer-facing
`Assignment`. Consumers never import this module; they receive `Assignment`
objects from `vaudeville_core.assignments`.
"""

from __future__ import annotations

from typing import Any

FIELDS = (
    "idReadable,summary,description,reporter(login),"
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


def signed_off(issue: dict[str, Any]) -> bool:
    return field_name(issue, "Signed off") == "Yes"


def reporter_login(issue: dict[str, Any]) -> str:
    reporter = issue.get("reporter") or {}
    return str(reporter.get("login") or "")


def authored_by_operator(issue: dict[str, Any], token_account: str) -> bool:
    # Every agent-driven tracker write authenticates with one API token, so an
    # agent-filed issue reports as that token's own account. A reporter absent or
    # equal to it fails safe to False, so unknown authorship reads as agent-authored
    # rather than being mistaken for the operator's.
    reporter = reporter_login(issue)
    return bool(reporter) and bool(token_account) and reporter != token_account


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
