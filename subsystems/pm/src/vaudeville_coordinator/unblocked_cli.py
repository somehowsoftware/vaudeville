from __future__ import annotations

import sys
from collections.abc import Callable

from vaudeville_core import Assignment, component_from_assignment_id, sort_key

from vaudeville_coordinator import unblocked


def show(assignment_id: str, *, fetch: Callable[[str], Assignment]) -> None:
    subject = _resolved_subject_or_exit(assignment_id, fetch)
    _print_ids(unblocked.unblocked_peers(subject, fetch=fetch))


def show_awaiting_sign_off(assignment_id: str, *, fetch: Callable[[str], Assignment]) -> None:
    subject = _resolved_subject_or_exit(assignment_id, fetch)
    _print_ids(unblocked.awaiting_sign_off_peers(subject, fetch=fetch))


def _resolved_subject_or_exit(assignment_id: str, fetch: Callable[[str], Assignment]) -> Assignment:
    component_from_assignment_id(assignment_id)
    subject = fetch(assignment_id)
    if not subject.state_resolved:
        sys.exit(
            f"{assignment_id} is not resolved; its unblocked peers are undefined "
            f"until it is delivered or abandoned"
        )
    return subject


def _print_ids(peers: list[Assignment]) -> None:
    for peer in sorted(peers, key=lambda peer: sort_key(peer.id)):
        print(peer.id)
