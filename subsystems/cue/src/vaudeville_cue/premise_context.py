from __future__ import annotations

from vaudeville_core import get_premise

from vaudeville_cue import first_turn


def main(premise_id: str) -> None:
    premise = get_premise(premise_id)
    body = first_turn.render(premise)
    print(body, end="")
