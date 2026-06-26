"""The Carried Set: the subset of a Pinned Set whose source ships inside the Artifact."""

from __future__ import annotations

from dataclasses import dataclass

from vaudeville_ringmaster.apply_plan import ApplyPlan
from vaudeville_ringmaster.carried_contribution import carried_contributions
from vaudeville_ringmaster.pin import Pin
from vaudeville_ringmaster.pinned_set import PinnedSet


@dataclass(frozen=True)
class CarriedSet:
    pins: tuple[Pin, ...]


def carried_set_of(pinned_set: PinnedSet, plan: ApplyPlan) -> CarriedSet:
    carried = {contribution.name for contribution in carried_contributions(plan)}
    return CarriedSet(pins=tuple(pin for pin in pinned_set.pins if pin.name in carried))
