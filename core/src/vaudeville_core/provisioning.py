"""Provision a tracker to the schema: stand up a Component's YouTrack project so
it presents the fields, values, defaults, and Depend link type a Vaudeville
tracker must have, from vaudeville-core's own data and with no reference project
to clone.

The decision is a pure core and the shell is dumb. ``plan`` is a transition
function: given the schema, the project to stand up, and what the instance
currently presents, it emits the Requests that close the gap and nothing else,
across the two scopes a tracker spans — instance-global (the custom field
definitions a fresh instance lacks, the Depend link type) and per-project (the
project, its value bundles, its attached fields, their defaults). The shell
observes, performs the plan, observes again, and re-plans until the plan is
empty; a server-minted id never threads through the logic, it re-enters the core
as part of the next observation. Idempotency is not a feature bolted on: it is
what planning against observed state *is*, so a re-run of a provisioned instance
plans nothing.
"""

from __future__ import annotations

import argparse
from collections.abc import Mapping
from typing import Any, NamedTuple

from vaudeville_core import _youtrack, essential_defaults
from vaudeville_core.backend import Request
from vaudeville_core.config_file import _abort
from vaudeville_core.tracker_schema import TRACKER_SCHEMA, SchemaField, TrackerSchema

_FIELD_TYPE_ID = {"enum": "enum[1]", "state": "state[1]"}
_BUNDLE_PATH = {
    "enum": "/admin/customFieldSettings/bundles/enum",
    "state": "/admin/customFieldSettings/bundles/state",
}
_BUNDLE_TYPE = {"enum": "EnumBundle", "state": "StateBundle"}
_BUNDLE_ELEMENT_TYPE = {"enum": "EnumBundleElement", "state": "StateBundleElement"}
_PROJECT_FIELD_TYPE = {"enum": "EnumProjectCustomField", "state": "StateProjectCustomField"}

_MAX_ROUNDS = 10


class TrackerProject(NamedTuple):
    """The project to stand up: its Assignment prefix and its display name."""

    short_name: str
    name: str


class Observed(NamedTuple):
    """What the instance currently presents, as a value the shell reads and the
    plan diffs against: the instance-global custom field definitions by name, the
    Depend link type, the project (its id once it exists, else ``None``), the
    leader's user id when the project must still be created, the value bundles
    that carry the schema's names, and the fields the project has attached."""

    global_field_definitions: Mapping[str, str]
    depend_present: bool
    project_id: str | None
    leader_id: str | None
    bundles: Mapping[str, dict[str, Any]]
    project_fields: Mapping[str, dict[str, Any]]


def bundle_name(short_name: str, field: SchemaField) -> str:
    return f"{short_name}-{field.name}"


def field_definition_requests(schema: TrackerSchema, observed: Observed) -> list[Request]:
    """Type and State are YouTrack built-ins present on every instance, so the
    schema's fields reduce to the custom definitions a fresh instance lacks."""
    return [
        Request(
            "POST",
            "/admin/customFieldSettings/customFields",
            {
                "$type": "CustomField",
                "name": field.name,
                "fieldType": {"$type": "FieldType", "id": _FIELD_TYPE_ID[field.kind]},
            },
        )
        for field in schema.fields
        if field.name not in observed.global_field_definitions
    ]


def depend_request(schema: TrackerSchema, observed: Observed) -> list[Request]:
    if observed.depend_present:
        return []
    depend = schema.depend
    return [
        Request(
            "POST",
            "/issueLinkTypes",
            {
                "$type": "IssueLinkType",
                "name": depend.name,
                "sourceToTarget": depend.outward,
                "targetToSource": depend.inward,
                "directed": True,
                "aggregation": False,
            },
        )
    ]


def project_request(project: TrackerProject, observed: Observed) -> list[Request]:
    if observed.project_id is not None:
        return []
    return [
        Request(
            "POST",
            "/admin/projects",
            {
                "name": project.name,
                "shortName": project.short_name,
                "leader": {"id": observed.leader_id},
            },
        )
    ]


def bundle_requests(
    schema: TrackerSchema, project: TrackerProject, observed: Observed
) -> list[Request]:
    """Bundles are instance-global, so unlike attachments their creation waits on
    no project; the deterministic name is what lets an existing one be recognised
    and left alone rather than duplicated."""
    requests: list[Request] = []
    for field in schema.fields:
        name = bundle_name(project.short_name, field)
        if name in observed.bundles:
            continue
        element_type = _BUNDLE_ELEMENT_TYPE[field.kind]
        values: list[dict[str, Any]] = []
        for ordinal, value in enumerate(field.values):
            element: dict[str, Any] = {
                "name": value.name,
                "ordinal": ordinal,
                "$type": element_type,
            }
            if field.kind == "state":
                element["isResolved"] = value.resolved
            values.append(element)
        requests.append(
            Request(
                "POST",
                _BUNDLE_PATH[field.kind],
                {"name": name, "$type": _BUNDLE_TYPE[field.kind], "values": values},
            )
        )
    return requests


def attachment_requests(
    schema: TrackerSchema, project: TrackerProject, observed: Observed
) -> list[Request]:
    """YouTrack auto-attaches the built-in Type and State to their own default
    bundles but leaves the custom fields off, so a field is either added or
    repointed off its foreign bundle onto the schema's."""
    if observed.project_id is None:
        return []
    requests: list[Request] = []
    for field in schema.fields:
        bundle = observed.bundles.get(bundle_name(project.short_name, field))
        global_id = observed.global_field_definitions.get(field.name)
        if bundle is None or global_id is None:
            continue
        attached = observed.project_fields.get(field.name)
        if attached is not None and (attached.get("bundle") or {}).get("id") == bundle["id"]:
            continue
        body = {
            "$type": _PROJECT_FIELD_TYPE[field.kind],
            "field": {"id": global_id},
            "bundle": {"id": bundle["id"], "$type": _BUNDLE_TYPE[field.kind]},
            "canBeEmpty": field.can_be_empty,
        }
        base = f"/admin/projects/{observed.project_id}/customFields"
        path = base if attached is None else f"{base}/{attached['id']}"
        requests.append(Request("POST", path, body))
    return requests


def default_requests(
    schema: TrackerSchema, project: TrackerProject, observed: Observed
) -> list[Request]:
    """The shared defaults planner aborts on a field whose bundle lacks the
    canonical value, so defaults wait until every field points at its own schema
    bundle. Gating on presence alone would run the planner against a field still
    on a foreign bundle (a built-in's default, a stale attachment) and abort
    mid-plan, stranding the repoint that would have fixed it."""
    if observed.project_id is None:
        return []
    for field in schema.fields:
        attached = observed.project_fields.get(field.name)
        bundle = observed.bundles.get(bundle_name(project.short_name, field))
        if attached is None or bundle is None:
            return []
        if (attached.get("bundle") or {}).get("id") != bundle["id"]:
            return []
    fields = list(observed.project_fields.values())
    return essential_defaults.essential_default_requests(observed.project_id, fields)


def plan(schema: TrackerSchema, project: TrackerProject, observed: Observed) -> list[Request]:
    return [
        *field_definition_requests(schema, observed),
        *depend_request(schema, observed),
        *project_request(project, observed),
        *bundle_requests(schema, project, observed),
        *attachment_requests(schema, project, observed),
        *default_requests(schema, project, observed),
    ]


def _project_id(short_name: str) -> str | None:
    project = _youtrack.request(
        "GET", f"/admin/projects/{short_name}", params={"fields": "id"}, allow_404=True
    )
    return str(project["id"]) if project else None


def _leader_id(login: str) -> str:
    user = _youtrack.request("GET", f"/users/{login}", params={"fields": "id"}, allow_404=True)
    if user is None:
        _abort(f"leader {login!r} not found")
    return str(user["id"])


def _global_field_definitions() -> dict[str, str]:
    fields = _youtrack.request_all("/admin/customFieldSettings/customFields", fields="id,name")
    return {str(field["name"]): str(field["id"]) for field in fields}


def _depend_present() -> bool:
    links = _youtrack.request_all("/issueLinkTypes", fields="name")
    return any(link.get("name") == TRACKER_SCHEMA.depend.name for link in links)


def _bundles(short_name: str) -> dict[str, dict[str, Any]]:
    wanted = {bundle_name(short_name, field) for field in TRACKER_SCHEMA.fields}
    found: dict[str, dict[str, Any]] = {}
    for kind in ("enum", "state"):
        bundles = _youtrack.request_all(
            _BUNDLE_PATH[kind], fields="id,name,values(id,name,isResolved)"
        )
        for bundle in bundles:
            if bundle.get("name") in wanted:
                found[str(bundle["name"])] = bundle
    return found


def _project_fields(project_id: str | None) -> dict[str, dict[str, Any]]:
    if project_id is None:
        return {}
    fields = _youtrack.request_all(
        f"/admin/projects/{project_id}/customFields",
        fields="id,$type,field(name),bundle(id,$type,values(id,name)),defaultValues(name)",
    )
    return {field["field"]["name"]: field for field in fields}


def observe(project: TrackerProject, leader: str) -> Observed:
    project_id = _project_id(project.short_name)
    return Observed(
        global_field_definitions=_global_field_definitions(),
        depend_present=_depend_present(),
        project_id=project_id,
        leader_id=_leader_id(leader) if project_id is None else None,
        bundles=_bundles(project.short_name),
        project_fields=_project_fields(project_id),
    )


def provision(short_name: str, name: str, leader: str = "admin") -> str:
    """Stand a Component's tracker up to the schema and return the project id."""
    project = TrackerProject(short_name=short_name, name=name)
    for _ in range(_MAX_ROUNDS):
        observed = observe(project, leader)
        requests = plan(TRACKER_SCHEMA, project, observed)
        if not requests:
            if observed.project_id is None:
                _abort(f"provisioning {short_name} left no project")
            return observed.project_id
        for request in requests:
            _youtrack.perform(request)
    _abort(f"provisioning {short_name} did not converge in {_MAX_ROUNDS} rounds")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Provision a Vaudeville tracker project to the schema."
    )
    parser.add_argument("--short-name", required=True, help="e.g. CORE")
    parser.add_argument("--name", required=True, help="e.g. Vaudeville-Core")
    parser.add_argument("--leader", default="admin")
    args = parser.parse_args(argv)
    project_id = provision(args.short_name, args.name, args.leader)
    print(f"Provisioned {args.short_name} ({project_id})")


if __name__ == "__main__":
    main()
