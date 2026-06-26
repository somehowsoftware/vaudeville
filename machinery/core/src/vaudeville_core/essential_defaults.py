"""Set the canonical Vaudeville-essential field defaults on a tracker project.

A hand-created tracker issue should open with the same initial fields in every
Vaudeville project: a Premise on the check-in Route, Submitted in both State
and Workflow, not yet signed off. YouTrack carries a field's default in the project custom field's
``defaultValues``; this module points each essential field's default at its
canonical value, resolving the value's id against that field's own bundle. A
project missing an essential field, or a field whose bundle holds no value of
the canonical name, is a violation the run aborts on rather than skips.

The decision is a pure core (a project's field catalog in, the write Requests
out, or a loud abort), and the shell only performs the catalog read and the
writes.
"""

from __future__ import annotations

import argparse
from typing import Any

from vaudeville_core import _youtrack, config_file
from vaudeville_core.backend import Request
from vaudeville_core.component import component_for_prefix
from vaudeville_core.config_file import _abort

ESSENTIAL_DEFAULTS: dict[str, str] = {
    "Type": "Premise",
    "Route": "check-in",
    "State": "Submitted",
    "Workflow": "Submitted",
    "Signed off": "No",
}

_BUNDLE_ELEMENT_TYPE = {
    "EnumBundle": "EnumBundleElement",
    "StateBundle": "StateBundleElement",
}


def project_fields_request(project_id: str) -> Request:
    return Request(
        "GET",
        f"/admin/projects/{project_id}/customFields",
        params={"fields": "id,$type,field(name),bundle($type,values(id,name))"},
    )


def canonical_default_element(
    field: dict[str, Any], field_name: str, value_name: str
) -> dict[str, str]:
    bundle = field.get("bundle") or {}
    bundle_type = bundle.get("$type")
    element_type = _BUNDLE_ELEMENT_TYPE.get(bundle_type) if isinstance(bundle_type, str) else None
    if element_type is None:
        _abort(f"field {field_name!r} has no enum or state bundle to default from")
    for value in bundle.get("values") or []:
        if value["name"] == value_name:
            return {"id": str(value["id"]), "$type": element_type}
    _abort(f"field {field_name!r} bundle has no value named {value_name!r}")


def essential_default_requests(project_id: str, fields: list[dict[str, Any]]) -> list[Request]:
    by_name = {field["field"]["name"]: field for field in fields}
    requests: list[Request] = []
    for field_name, value_name in ESSENTIAL_DEFAULTS.items():
        field = by_name.get(field_name)
        if field is None:
            _abort(f"project {project_id} has no {field_name!r} field")
        element = canonical_default_element(field, field_name, value_name)
        requests.append(
            Request(
                "POST",
                f"/admin/projects/{project_id}/customFields/{field['id']}",
                {"$type": field["$type"], "defaultValues": [element]},
            )
        )
    return requests


def apply_essential_defaults(project_id: str) -> None:
    fields = _youtrack.perform(project_fields_request(project_id))
    for request in essential_default_requests(project_id, fields):
        _youtrack.perform(request)


def apply_to_registered_components() -> list[str]:
    config = config_file.load_config()
    applied: list[str] = []
    for component in config.components.values():
        apply_essential_defaults(component.tracker_project_id)
        applied.append(component.prefix)
    return applied


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Set the canonical Vaudeville-essential field defaults on tracker projects."
    )
    parser.add_argument(
        "--project",
        help="Assignment prefix of one registered project (default: every registered project).",
    )
    args = parser.parse_args(argv)
    if args.project is None:
        applied = apply_to_registered_components()
        print(f"Set essential defaults on: {', '.join(applied)}")
        return
    component = component_for_prefix(config_file.load_config(), args.project)
    if component is None:
        _abort(f"Component {args.project!r} is not in the register")
    apply_essential_defaults(component.tracker_project_id)
    print(f"Set essential defaults on {component.prefix}")


if __name__ == "__main__":
    main()
