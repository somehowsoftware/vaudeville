"""The Tracker schema: the authoritative shape a Vaudeville tracker must present,
carried as vaudeville-core's own data rather than read off a reference project.

The schema names, in Vaudeville's own words, what a tracker has to say for an
Assignment to carry a Type, State, Route, Workflow, and Signed-off mark, and for
one Assignment to Depend on another: each field, its ordered values, the value
that is a resolved State, and the canonical default a fresh Assignment opens
with. The values are Vaudeville primitives (Premise, Ready, check-in, Submitted,
"depends on"); the records that hold them (a field, a value, the link type) are
literate plumbing, not domain terms.

Because a real tenant provisions from this literal and never from a reference
project, the literal is the single source of truth: the essential defaults are a
projection of it, and a load-time predicate rejects a schema that could not be
provisioned (a default naming no value, a resolved enum value) so a mistake in
the literal fails at import rather than mid-provision.
"""

from __future__ import annotations

from typing import Literal, NamedTuple

FieldKind = Literal["enum", "state"]


class SchemaValue(NamedTuple):
    """One value a field may take. ``resolved`` marks a State value that closes
    an Assignment; it is meaningful only on a ``state`` field and false elsewhere."""

    name: str
    resolved: bool = False


class SchemaField(NamedTuple):
    """One tracker field: its kind, whether it may be left empty, its values in
    display order, and the value a fresh Assignment defaults to."""

    name: str
    kind: FieldKind
    can_be_empty: bool
    values: tuple[SchemaValue, ...]
    default: str


class LinkType(NamedTuple):
    """A directed link one Assignment bears on another. The schema carries one:
    Depend, whose source ``is required for`` its target and target ``depends on``
    its source."""

    name: str
    outward: str
    inward: str


class TrackerSchema(NamedTuple):
    """The whole authoritative shape: every field a tracker carries and the link
    type between Assignments."""

    fields: tuple[SchemaField, ...]
    depend: LinkType


TRACKER_SCHEMA = TrackerSchema(
    fields=(
        SchemaField(
            name="Type",
            kind="enum",
            can_be_empty=False,
            values=(
                SchemaValue("Premise"),
                SchemaValue("Command"),
                SchemaValue("Direction"),
                SchemaValue("Manual"),
            ),
            default="Premise",
        ),
        SchemaField(
            name="State",
            kind="state",
            can_be_empty=False,
            values=(
                SchemaValue("Ready"),
                SchemaValue("Active"),
                SchemaValue("Delivered", resolved=True),
                SchemaValue("Abandoned", resolved=True),
                SchemaValue("Deferred"),
                SchemaValue("Submitted"),
            ),
            default="Submitted",
        ),
        SchemaField(
            name="Route",
            kind="enum",
            can_be_empty=True,
            values=(
                SchemaValue("direct"),
                SchemaValue("check-in"),
                SchemaValue("plan"),
                SchemaValue("manual"),
                SchemaValue("explore"),
            ),
            default="check-in",
        ),
        SchemaField(
            name="Workflow",
            kind="enum",
            can_be_empty=True,
            values=(
                SchemaValue("Submitted"),
                SchemaValue("Claimed"),
                SchemaValue("Returned"),
            ),
            default="Submitted",
        ),
        SchemaField(
            name="Signed off",
            kind="enum",
            can_be_empty=True,
            values=(
                SchemaValue("No"),
                SchemaValue("Yes"),
            ),
            default="No",
        ),
    ),
    depend=LinkType(name="Depend", outward="is required for", inward="depends on"),
)


def _validate(schema: TrackerSchema) -> None:
    """Reject a schema that could not be provisioned. Runs at import so a bad
    literal fails loudly here, never mid-provision against a live instance."""
    for field in schema.fields:
        names = [value.name for value in field.values]
        if not names:
            raise ValueError(f"field {field.name!r} carries no values")
        if len(names) != len(set(names)):
            raise ValueError(f"field {field.name!r} repeats a value name")
        if field.default not in names:
            raise ValueError(
                f"field {field.name!r} defaults to {field.default!r}, not one of its values"
            )
        if field.kind != "state" and any(value.resolved for value in field.values):
            raise ValueError(f"non-state field {field.name!r} carries a resolved value")
    if not (schema.depend.name and schema.depend.outward and schema.depend.inward):
        raise ValueError("the Depend link type is missing a name or direction phrase")


_validate(TRACKER_SCHEMA)
