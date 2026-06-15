"""Clone a YouTrack project's schema (custom fields, bundles, defaults,
workflow attachments) to a new project.

The reference project (default `BOB`) is cloned to give every Vaudeville-pattern
subsystem a consistent tracker shape without a per-project manual audit.

YouTrack auto-attaches a fixed set of fields when a project is created:
Priority, Type, State, Subsystem, Fix versions, Affected versions, Fixed in
build, Assignee. For each enum/state field with a non-empty value list in the
template (Priority, Type, State), this module creates a fresh bundle on the
target project mirroring the template's values, then repoints the
auto-attached field at it. For fields not in the auto-set (Route in BOB), the
field is explicitly attached with a fresh bundle. Empty bundles
(Subsystem/Versions/Build/Assignee) are left as YouTrack auto-creates them.
"""

from __future__ import annotations

import argparse
import secrets
import sys
from typing import Any

from vaudeville_core import _youtrack as youtrack

_BUNDLE_PATH = {
    "EnumBundle": "/admin/customFieldSettings/bundles/enum",
    "StateBundle": "/admin/customFieldSettings/bundles/state",
}
_VALUE_TYPE = {
    "EnumBundle": "EnumBundleElement",
    "StateBundle": "StateBundleElement",
}


def lookup_project_id(short_name: str) -> str:
    """Fetch a project by shortName via the direct admin endpoint.

    `/admin/projects/{shortName}` returns the project record directly, so
    instances with more projects than the default page cap (42) can't
    silently mask a valid template behind missing pagination.
    """
    project = youtrack.request(
        "GET",
        f"/admin/projects/{short_name}",
        params={"fields": "id,shortName"},
        allow_404=True,
    )
    if project is None:
        print(f"Error: project {short_name!r} not found.", file=sys.stderr)
        sys.exit(1)
    return str(project["id"])


def lookup_user_id(login: str) -> str:
    """Fetch a user by login via the direct endpoint.

    `/users/{login}` resolves to a single user, sidestepping the user-list
    page cap that would otherwise hide valid logins on larger instances.
    """
    user = youtrack.request(
        "GET",
        f"/users/{login}",
        params={"fields": "id,login"},
        allow_404=True,
    )
    if user is None:
        print(f"Error: user {login!r} not found.", file=sys.stderr)
        sys.exit(1)
    return str(user["id"])


def fetch_template(project_id: str) -> tuple[list[dict[str, Any]], list[str]]:
    fields = youtrack.request(
        "GET",
        f"/admin/projects/{project_id}/customFields",
        params={
            "fields": (
                "id,canBeEmpty,emptyFieldText,$type,"
                "field(id,name,fieldType(id)),"
                "bundle(id,$type,values(name,description,ordinal,isResolved)),"
                "defaultValues(name)"
            )
        },
    )
    workflows = youtrack.request(
        "GET", f"/admin/projects/{project_id}/workflows", params={"fields": "id"}
    )
    return list(fields), [str(w["id"]) for w in workflows]


def create_project(short_name: str, name: str, leader: str) -> str:
    leader_id = lookup_user_id(leader)
    project = youtrack.request(
        "POST",
        "/admin/projects",
        json_body={
            "name": name,
            "shortName": short_name,
            "leader": {"id": leader_id},
        },
        params={"fields": "id,shortName"},
    )
    return str(project["id"])


def fetch_project_fields(project_id: str) -> list[dict[str, Any]]:
    return list(
        youtrack.request(
            "GET",
            f"/admin/projects/{project_id}/customFields",
            params={"fields": "id,$type,field(id,name)"},
        )
    )


def clone_enum_bundle(
    short_name: str, field_name: str, template_bundle: dict[str, Any]
) -> tuple[str, dict[str, str]]:
    """Return (new bundle id, name→id map of the new bundle's values).

    Bundle names are globally unique in a YouTrack instance, so a short
    random suffix is appended to avoid collisions with bundles left over
    from prior runs (or other projects that share a shortName prefix).
    """
    btype = template_bundle["$type"]
    value_type = _VALUE_TYPE[btype]
    values = []
    for value in template_bundle.get("values") or []:
        entry: dict[str, Any] = {
            "name": value["name"],
            "ordinal": value["ordinal"],
            "$type": value_type,
        }
        if btype == "StateBundle":
            entry["isResolved"] = bool(value.get("isResolved"))
        values.append(entry)
    suffix = secrets.token_hex(2)
    body = {
        "name": f"{short_name}-{field_name}-{suffix}",
        "values": values,
        "$type": btype,
    }
    bundle = youtrack.request(
        "POST",
        _BUNDLE_PATH[btype],
        json_body=body,
        params={"fields": "id,values(id,name)"},
    )
    value_ids = {v["name"]: str(v["id"]) for v in bundle.get("values") or []}
    return str(bundle["id"]), value_ids


def attach_or_repoint_field(
    project_id: str,
    template_field: dict[str, Any],
    bundle_id: str | None,
    bundle_value_ids: dict[str, str],
    existing_field_id: str | None,
) -> None:
    body: dict[str, Any] = {
        "$type": template_field["$type"],
        "field": {"id": template_field["field"]["id"]},
        "canBeEmpty": template_field.get("canBeEmpty", True),
        "emptyFieldText": template_field.get("emptyFieldText"),
    }
    if bundle_id is not None:
        body["bundle"] = {"id": bundle_id, "$type": template_field["bundle"]["$type"]}
    defaults = template_field.get("defaultValues") or []
    if defaults and bundle_value_ids:
        value_type = _VALUE_TYPE.get(template_field["bundle"]["$type"], "")
        body["defaultValues"] = [
            {"id": bundle_value_ids[d["name"]], "$type": value_type}
            for d in defaults
            if d["name"] in bundle_value_ids
        ]
    if existing_field_id is None:
        path = f"/admin/projects/{project_id}/customFields"
    else:
        path = f"/admin/projects/{project_id}/customFields/{existing_field_id}"
    youtrack.request("POST", path, json_body=body)


def attach_workflow(project_id: str, workflow_id: str) -> None:
    youtrack.request(
        "POST",
        f"/admin/projects/{project_id}/workflows",
        json_body={"workflow": {"id": workflow_id}, "$type": "WorkflowUsage"},
    )


def bootstrap_project(short_name: str, name: str, leader: str, template: str) -> str:
    template_id = lookup_project_id(template)
    template_fields, workflows = fetch_template(template_id)
    new_id = create_project(short_name, name, leader)
    existing = {f["field"]["name"]: f["id"] for f in fetch_project_fields(new_id)}
    for tf in template_fields:
        field_name = tf["field"]["name"]
        bundle_type = tf.get("bundle", {}).get("$type")
        bundle_values = (tf.get("bundle") or {}).get("values") or []
        if bundle_type in _BUNDLE_PATH and bundle_values:
            new_bundle_id: str | None
            new_bundle_id, value_ids = clone_enum_bundle(short_name, field_name, tf["bundle"])
        else:
            new_bundle_id = None
            value_ids = {}
        attach_or_repoint_field(new_id, tf, new_bundle_id, value_ids, existing.get(field_name))
    for wf_id in workflows:
        attach_workflow(new_id, wf_id)
    return new_id


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Clone a YouTrack project's schema to a new project."
    )
    parser.add_argument("--short-name", required=True, help="e.g. CORE")
    parser.add_argument("--name", required=True, help="e.g. Bobiverse-Core")
    parser.add_argument("--leader", default="admin")
    parser.add_argument("--template", default="BOB")
    args = parser.parse_args(argv)
    project_id = bootstrap_project(args.short_name, args.name, args.leader, args.template)
    print(f"Created project {args.short_name} ({project_id})")


if __name__ == "__main__":
    main()
