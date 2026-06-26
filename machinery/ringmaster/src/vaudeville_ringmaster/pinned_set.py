"""The Pinned Set: the whole federation frozen at gather time, one Pin per Contributor Repo."""

from __future__ import annotations

from dataclasses import dataclass

from vaudeville_ringmaster.pin import Pin, pin_clone
from vaudeville_ringmaster.registry import Registry
from vaudeville_ringmaster.session_clone import SessionClone


@dataclass(frozen=True)
class PinnedSet:
    pins: tuple[Pin, ...]


def pin_session_clones(registry: Registry, clones: list[SessionClone]) -> PinnedSet:
    return PinnedSet(
        pins=tuple(
            pin_clone(clone.name, registry.remote_for(clone.name), clone.path) for clone in clones
        )
    )
