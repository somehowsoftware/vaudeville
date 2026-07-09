from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

from vaudeville_bobiverse import foundation
from vaudeville_bobiverse.spawn import target_repo
from vaudeville_bobiverse.spawn.refusal import Refusal

NO_FOUNDATION_EXIT = 2


@dataclass(frozen=True)
class ClearedSpawn:
    target: Path
    foundation_session: str


@dataclass(frozen=True)
class Clearing:
    # A field is None only until its clearance runs and fills it; `cleared()` reads
    # the resolved values out and fails loud if any is still unfilled.
    prefix: str
    data_files_root: Path
    target: Path | None = None
    foundation_session: str | None = None

    def cleared(self) -> ClearedSpawn:
        # A None here means a clearance was skipped — a broken invariant, not a user
        # condition — so this asserts rather than refusing.
        if self.target is None or self.foundation_session is None:
            raise AssertionError("Clearing.cleared() called before every clearance ran")
        return ClearedSpawn(self.target, self.foundation_session)


def no_foundation_refusal(prefix: str) -> Refusal:
    return Refusal(
        message=(
            f"Error: no Foundation for prefix {prefix!r}. "
            f"Run `vv prime {prefix}` before spawning into this Component."
        ),
        exit_code=NO_FOUNDATION_EXIT,
    )


def foundation_refusal(prefix: str, foundation_session: str | None) -> Refusal | None:
    if foundation_session is None:
        return no_foundation_refusal(prefix)
    return None


def clear_target(clearing: Clearing) -> Refusal | Clearing:
    resolved = target_repo.target_repo_for_prefix(clearing.prefix)
    if isinstance(resolved, Refusal):
        return resolved
    return replace(clearing, target=resolved)


def clear_foundation(clearing: Clearing) -> Refusal | Clearing:
    session = foundation.lookup(clearing.prefix, data_files_root=clearing.data_files_root)
    refusal = foundation_refusal(clearing.prefix, session)
    if refusal is not None:
        return refusal
    return replace(clearing, foundation_session=session)


SPAWN_CLEARANCES = (clear_target, clear_foundation)
