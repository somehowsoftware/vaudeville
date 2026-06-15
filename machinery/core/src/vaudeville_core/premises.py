"""Vaudeville-primitive Premise value type plus the pure sort helper.

This module is data only — no backend imports, no I/O. Queries
(`find_premises`, `get_premise`) live in `vaudeville_core.queries`;
mutations (`create_premise`, `claim_premise`, `add_comment`, the link
operations) live in `vaudeville_core.mutations`. The public surface
of the kernel re-exports the relevant names from each module via
`vaudeville_core.__init__`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_PREMISE_RE = re.compile(r"([A-Z]+)-(\d+)")


@dataclass(frozen=True)
class PremiseRef:
    """Pointer to another Premise. Surfaced from Premise's link fields.

    `state_resolved` is denormalised onto the ref so dependency
    predicates do not require a second fetch per ref.
    """

    id: str
    state_resolved: bool


@dataclass(frozen=True)
class Comment:
    """A comment that accumulated on a Premise's thread.

    The fields are deliberately thin — `author` is a display name, not a
    user record, and `created` is the backend's epoch-millisecond stamp —
    enough to attribute the discussion to a reader, no more.
    """

    author: str
    text: str
    created: int


@dataclass(frozen=True)
class Premise:
    """A Vaudeville Premise. The single domain type consumers see.

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
    deps_inward: tuple[PremiseRef, ...]
    deps_outward: tuple[PremiseRef, ...]
    subtask_inward: tuple[PremiseRef, ...]
    subtask_outward: tuple[PremiseRef, ...]
    duplicates_inward: tuple[PremiseRef, ...]
    duplicates_outward: tuple[PremiseRef, ...]
    comments: tuple[Comment, ...]


def sort_key(premise_id: str) -> tuple[str, int]:
    """Stable sort key for Vaudeville Premise ids (`BOB-2` < `BOB-10`)."""
    match = _PREMISE_RE.match(premise_id)
    return (match.group(1), int(match.group(2))) if match else (premise_id, 0)


def make_premise(
    id: str = "BOB-1",
    *,
    summary: str = "",
    description: str = "",
    type: str = "Premise",
    state: str = "Submitted",
    workflow: str = "Submitted",
    route: str = "check-in",
    state_resolved: bool = False,
    deps_inward: tuple[PremiseRef, ...] = (),
    deps_outward: tuple[PremiseRef, ...] = (),
    subtask_inward: tuple[PremiseRef, ...] = (),
    subtask_outward: tuple[PremiseRef, ...] = (),
    duplicates_inward: tuple[PremiseRef, ...] = (),
    duplicates_outward: tuple[PremiseRef, ...] = (),
    comments: tuple[Comment, ...] = (),
) -> Premise:
    """Construct a Premise value object with defaults for every field.

    A local-only constructor — no I/O, no backend call. Distinct from
    ``vaudeville_core.create_premise``, which performs a backend write
    and returns a new tracker id. Use ``make_premise`` when a Premise
    instance is needed for tests, in-memory fixtures, or any other
    case where the data already exists and only needs to be shaped.
    """
    return Premise(
        id=id,
        summary=summary,
        description=description,
        type=type,
        state=state,
        workflow=workflow,
        route=route,
        state_resolved=state_resolved,
        deps_inward=deps_inward,
        deps_outward=deps_outward,
        subtask_inward=subtask_inward,
        subtask_outward=subtask_outward,
        duplicates_inward=duplicates_inward,
        duplicates_outward=duplicates_outward,
        comments=comments,
    )
