"""The Apply Plan."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from vaudeville_ringmaster.contribution import Contribution


@dataclass(frozen=True)
class ApplyPlan:
    contributions: tuple[Contribution, ...]


def raise_if_apply_plan_has_collisions(plan: ApplyPlan) -> None:
    collisions = _collisions_in(plan)
    if collisions:
        raise InvalidApplyPlan(collisions)


def _collisions_in(plan: ApplyPlan) -> list[str]:
    collisions: list[str] = []

    skill_counts = Counter(
        skill.name for contribution in plan.contributions for skill in contribution.skills
    )
    for name, count in skill_counts.items():
        if count > 1:
            collisions.append(f"Skill {name!r} appears in {count} Contributions")

    doc_tree_counts = Counter(
        doc_tree.name for contribution in plan.contributions for doc_tree in contribution.doc_trees
    )
    for name, count in doc_tree_counts.items():
        if count > 1:
            collisions.append(f"Doc Tree {name!r} appears in {count} Contributions")

    return collisions


class InvalidApplyPlan(ValueError):
    def __init__(self, collisions: list[str]) -> None:
        super().__init__(collisions)
        self.collisions = collisions

    def __str__(self) -> str:
        return "Apply Plan validation failed: " + "; ".join(self.collisions)
