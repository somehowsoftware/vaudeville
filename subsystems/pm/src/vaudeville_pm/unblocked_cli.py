"""CLI handler for the `unblocked` subcommand."""

from __future__ import annotations

import sys
from collections.abc import Callable

from vaudeville_core import Premise, project_from_premise_id, sort_key

from vaudeville_pm import unblocked


def show(premise_id: str, *, fetch: Callable[[str], Premise]) -> None:
    project_from_premise_id(premise_id)
    subject = fetch(premise_id)
    if not subject.state_resolved:
        sys.exit(
            f"{premise_id} is not resolved; its unblocked peers are undefined "
            f"until it is delivered or abandoned"
        )
    pickable = unblocked.unblocked_peers(subject, fetch=fetch)
    for peer in sorted(pickable, key=lambda peer: sort_key(peer.id)):
        print(peer.id)
