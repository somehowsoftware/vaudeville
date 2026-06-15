"""Pydantic schema for the Premise display projection.

Owns two things and nothing else:

- The shape of a Premise as `vv premise-show` and downstream skills see
  it (``PremiseView``, plus ``DepView`` for one Depend-link peer).
- The rule for projecting the shared-kernel ``Premise`` value object
  into that flat shape (``PremiseView.from_premise``).

Pydantic v2 carries validation and JSON serialization for free, which
keeps the CLI handler down to ``view.model_dump_json(indent=2)`` and
the test surface down to ``PremiseView.from_premise(fixture)``.

This module does not know how the ``Premise`` arrived and does not
issue any backend call.
"""

from __future__ import annotations

from typing import Self

from pydantic import BaseModel, ConfigDict
from vaudeville_core import Premise


class DepView(BaseModel):
    """One Depend-link peer's display-relevant projection."""

    model_config = ConfigDict(frozen=True)

    id: str
    state_resolved: bool


class PremiseView(BaseModel):
    """Display-relevant projection of a Premise value object."""

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
    def from_premise(cls, premise: Premise) -> Self:
        """Project a shared-kernel ``Premise`` into the view.

        Collapses empty enum strings to ``None`` (Vaudeville enum
        bundles do not admit empty names, so the collapse loses no
        information and gives the JSON surface a clean ``null``).
        """
        return cls(
            id=premise.id,
            summary=premise.summary,
            type=premise.type or None,
            route=premise.route or None,
            state=premise.state or None,
            workflow=premise.workflow or None,
            state_resolved=premise.state_resolved,
            deps_inward=tuple(
                DepView(id=ref.id, state_resolved=ref.state_resolved) for ref in premise.deps_inward
            ),
            deps_outward=tuple(
                DepView(id=ref.id, state_resolved=ref.state_resolved)
                for ref in premise.deps_outward
            ),
            description=premise.description,
        )
