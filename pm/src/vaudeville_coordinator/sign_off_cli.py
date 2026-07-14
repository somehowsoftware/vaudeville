"""CLI handler for the `sign-off` subcommand.

Thin adapter between Typer dispatch in `cli.py` and "core"'s sign-off
operation. The handler carries the id-shape guard before the write and the
confirmation print; the sign-off op is injected. The composition root binds
the real "core" op, tests bind a fake.
"""

from __future__ import annotations

from collections.abc import Callable

from vaudeville_core import component_from_assignment_id


def sign_off(assignment_id: str, *, sign_off: Callable[[str], None]) -> None:
    component_from_assignment_id(assignment_id)  # validates id shape; exits on malformed
    sign_off(assignment_id)
    print(f"Signed off {assignment_id}")
