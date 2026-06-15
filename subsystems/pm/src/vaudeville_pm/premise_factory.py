"""Factory for new Premise aggregates.

Owns the one operation whose result is a Premise id that did not exist
before the call: ``create``. The decision this module holds — distinct
from a bare kernel call — is the Premise-creation policy: the default
Type (``Premise``) and Workflow (``Submitted``), and the mapping of the
domain's ``type_name`` onto the kernel's ``type`` field. The kernel
writer is injected so that policy is exercised against a recorded call
rather than a live tracker write.

The factory returns the new ``idReadable`` rather than a hydrated
aggregate because every downstream caller composes the new id into a
further shell pipeline; hydrating would force a second fetch every
caller would have to skip.
"""

from __future__ import annotations

from collections.abc import Callable

CreatePremise = Callable[..., str]


def create(
    project: str,
    *,
    summary: str,
    description: str,
    route: str,
    type_name: str = "Premise",
    workflow: str = "Submitted",
    create_premise: CreatePremise,
) -> str:
    """Create a Premise in ``project`` and return its idReadable."""
    return create_premise(
        project,
        summary=summary,
        description=description,
        route=route,
        type=type_name,
        workflow=workflow,
    )
