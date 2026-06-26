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
            f"Run `vv prime {prefix}` before spawning into this Component."
        ),
        exit_code=NO_FOUNDATION_EXIT,
    )


def spawn_decision(prefix: str, foundation_session: str | None) -> SpawnRefusal | SpawnClearance:
    if foundation_session is None:
        return no_foundation_refusal(prefix)
    return SpawnClearance(foundation_session=foundation_session)
