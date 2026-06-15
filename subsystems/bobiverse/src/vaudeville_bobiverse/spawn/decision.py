"""The Foundation gate: whether a cleared Spawn has a session to fork, and which.

``spawn_decision`` is the last of the composition root's three gates — backlog
(preflight) and host-repo (target resolution) precede it. Given the session
looked up for the Premise's Managed Repository, it returns either the
``no_foundation_refusal`` or a ``SpawnClearance`` carrying that session. The
clearance carries the resolved session rather than leaving it ``Optional``, so a
cleared Spawn cannot reach the launch without a Foundation to fork.
"""

from __future__ import annotations

from dataclasses import dataclass

NO_FOUNDATION_EXIT = 2


@dataclass(frozen=True)
class SpawnRefusal:
    message: str
    exit_code: int


@dataclass(frozen=True)
class SpawnClearance:
    foundation_session: str


def no_foundation_refusal(prefix: str) -> SpawnRefusal:
    return SpawnRefusal(
        message=(
            f"Error: no Foundation for prefix {prefix!r}. "
            f"Run `vv prime {prefix}` before spawning into this Managed Repository."
        ),
        exit_code=NO_FOUNDATION_EXIT,
    )


def spawn_decision(prefix: str, foundation_session: str | None) -> SpawnRefusal | SpawnClearance:
    if foundation_session is None:
        return no_foundation_refusal(prefix)
    return SpawnClearance(foundation_session=foundation_session)
