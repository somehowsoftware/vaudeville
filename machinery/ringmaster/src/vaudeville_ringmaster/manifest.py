"""The Manifest: the validated bill of materials a Survey produces."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from vaudeville_ringmaster.contribution import Contribution


@dataclass(frozen=True)
class Manifest:
    contributions: tuple[Contribution, ...]


def raise_if_manifest_has_collisions(manifest: Manifest) -> None:
    collisions = _collisions_in(manifest)
    if collisions:
        raise InvalidManifest(collisions)


def _collisions_in(manifest: Manifest) -> list[str]:
    collisions: list[str] = []

    skill_counts = Counter(
        skill.name for contribution in manifest.contributions for skill in contribution.skills
    )
    for name, count in skill_counts.items():
        if count > 1:
            collisions.append(f"Skill {name!r} appears in {count} Contributions")

    doc_tree_counts = Counter(
        doc_tree.name
        for contribution in manifest.contributions
        for doc_tree in contribution.doc_trees
    )
    for name, count in doc_tree_counts.items():
        if count > 1:
            collisions.append(f"Doc Tree {name!r} appears in {count} Contributions")

    return collisions


class InvalidManifest(ValueError):
    def __init__(self, collisions: list[str]) -> None:
        super().__init__(collisions)
        self.collisions = collisions

    def __str__(self) -> str:
        return "Manifest validation failed: " + "; ".join(self.collisions)
