"""Vaudeville-primitive Assignment value type plus the pure sort helper.

This module is data only: no backend imports, no I/O. Queries
(`find_assignments`, `get_assignment`) live in `vaudeville_core.queries`;
mutations (`create_assignment`, `claim_assignment`, `add_comment`, the link
operations) live in `vaudeville_core.mutations`. The public surface
of vaudeville-core re-exports the relevant names from each module via
`vaudeville_core.__init__`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_ASSIGNMENT_RE = re.compile(r"([A-Z]+)-(\d+)")


@dataclass(frozen=True)
class AssignmentRef:
    """Pointer to another Assignment. Surfaced from an Assignment's link fields.

    `state_resolved` is denormalised onto the ref so dependency
    predicates do not require a second fetch per ref.
    """

    id: str
    state_resolved: bool


@dataclass(frozen=True)
class Comment:
    """A comment that accumulated on an Assignment's thread.

    The fields are deliberately thin (`author` is a display name, not a
    user record, and `created` is the backend's epoch-millisecond stamp),
    enough to attribute the discussion to a reader, no more.
    """

    author: str
    text: str
    created: int


@dataclass(frozen=True)
class Assignment:
    """A Vaudeville Assignment. The single domain type consumers see.

    Field names and values are Vaudeville primitives. Construction
    from a backend response is the responsibility of
    `vaudeville_core.queries`; consumers read the dataclass attributes
    directly.
    """

    id: str
    summary: str
    description: str
    type: str
    state: str
    workflow: str
    route: str
    state_resolved: bool
    signed_off: bool
    deps_inward: tuple[AssignmentRef, ...]
    deps_outward: tuple[AssignmentRef, ...]
    subtask_inward: tuple[AssignmentRef, ...]
    subtask_outward: tuple[AssignmentRef, ...]
    duplicates_inward: tuple[AssignmentRef, ...]
    duplicates_outward: tuple[AssignmentRef, ...]
    comments: tuple[Comment, ...]


def sort_key(assignment_id: str) -> tuple[str, int]:
    """Stable sort key for Vaudeville Assignment ids (`BOB-2` < `BOB-10`)."""
    match = _ASSIGNMENT_RE.match(assignment_id)
    return (match.group(1), int(match.group(2))) if match else (assignment_id, 0)


def make_assignment(
    id: str = "BOB-1",
    *,
    summary: str = "",
    description: str = "",
    type: str = "Premise",
    state: str = "Submitted",
    workflow: str = "Submitted",
    route: str = "check-in",
    state_resolved: bool = False,
    signed_off: bool = False,
    deps_inward: tuple[AssignmentRef, ...] = (),
    deps_outward: tuple[AssignmentRef, ...] = (),
    subtask_inward: tuple[AssignmentRef, ...] = (),
    subtask_outward: tuple[AssignmentRef, ...] = (),
    duplicates_inward: tuple[AssignmentRef, ...] = (),
    duplicates_outward: tuple[AssignmentRef, ...] = (),
    comments: tuple[Comment, ...] = (),
) -> Assignment:
    """Construct an Assignment value object with defaults for every field.

    A local-only constructor: no I/O, no backend call. Distinct from
    ``vaudeville_core.create_assignment``, which performs a backend write
    and returns a new tracker id. Use ``make_assignment`` when an Assignment
    instance is needed for tests, in-memory fixtures, or any other
    case where the data already exists and only needs to be shaped.
    """
    return Assignment(
        id=id,
        summary=summary,
        description=description,
        type=type,
        state=state,
        workflow=workflow,
        route=route,
        state_resolved=state_resolved,
        signed_off=signed_off,
        deps_inward=deps_inward,
        deps_outward=deps_outward,
        subtask_inward=subtask_inward,
        subtask_outward=subtask_outward,
        duplicates_inward=duplicates_inward,
        duplicates_outward=duplicates_outward,
        comments=comments,
    )
