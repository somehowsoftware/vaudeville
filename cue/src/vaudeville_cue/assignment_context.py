from __future__ import annotations

from vaudeville_core import get_assignment

from vaudeville_cue import first_turn


def main(assignment_id: str) -> None:
    assignment = get_assignment(assignment_id)
    body = first_turn.render(assignment)
    print(body, end="")
