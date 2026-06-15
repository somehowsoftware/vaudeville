"""CLI handlers for Link subcommands.

Adapter between Typer dispatch and the kernel's Depend-edge operations.
Each handler validates the Premise-id shape on both sides of an edge
before mutating, so a malformed argument exits early without producing a
half-applied state on the tracker side. The edge operation is injected;
the composition root binds the real kernel op, tests bind a fake.
"""

from __future__ import annotations

from collections.abc import Callable

from vaudeville_core import project_from_premise_id

DependEdge = Callable[[str, str], None]


def depend_add(source: str, target: str, *, add_depend: DependEdge) -> None:
    project_from_premise_id(source)
    project_from_premise_id(target)
    add_depend(source, target)


def depend_remove(source: str, target: str, *, remove_depend: DependEdge) -> None:
    project_from_premise_id(source)
    project_from_premise_id(target)
    remove_depend(source, target)
