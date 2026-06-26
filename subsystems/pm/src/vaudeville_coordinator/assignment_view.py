"""Pydantic schema for the Assignment display projection.

Owns two things and nothing else:

- The shape of an Assignment as `vv assignment-show` and downstream skills
  see it (``AssignmentView``, plus ``DepView`` for one Depend-link peer).
- The rule for projecting core's ``Assignment`` value object
  into that flat shape (``AssignmentView.from_assignment``).

Pydantic v2 carries validation and JSON serialization for free, which
keeps the CLI handler down to ``view.model_dump_json(indent=2)`` and
the test surface down to ``AssignmentView.from_assignment(fixture)``.

This module does not know how the ``Assignment`` arrived and does not
issue any backend call.
"""

from __future__ import annotations

from typing import Self

from pydantic import BaseModel, ConfigDict
from vaudeville_core import Assignment


class DepView(BaseModel):
    """One Depend-link peer's display-relevant projection."""

    model_config = ConfigDict(frozen=True)

    id: str
    state_resolved: bool


class AssignmentView(BaseModel):
    """Display-relevant projection of an Assignment value object."""

    model_config = ConfigDict(frozen=True)

    id: str
    summary: str
    type: str | None = None
    route: str | None = None
    state: str | None = None
    workflow: str | None = None
    state_resolved: bool = False
    deps_inward: tuple[DepView, ...] = ()
    deps_outward: tuple[DepView, ...] = ()
    description: str = ""

    @classmethod
    def from_assignment(cls, assignment: Assignment) -> Self:
        """Project core's ``Assignment`` into the view.

        Collapses empty enum strings to ``None`` (Vaudeville enum
        bundles do not admit empty names, so the collapse loses no
        information and gives the JSON surface a clean ``null``).
        """
        return cls(
            id=assignment.id,
            summary=assignment.summary,
            type=assignment.type or None,
            route=assignment.route or None,
            state=assignment.state or None,
            workflow=assignment.workflow or None,
            state_resolved=assignment.state_resolved,
            deps_inward=tuple(
                DepView(id=ref.id, state_resolved=ref.state_resolved)
                for ref in assignment.deps_inward
            ),
            deps_outward=tuple(
                DepView(id=ref.id, state_resolved=ref.state_resolved)
                for ref in assignment.deps_outward
            ),
            description=assignment.description,
        )
