from __future__ import annotations

from enum import Enum


class CommitProvenance(Enum):
    UNMOVED = "unmoved"
    AUTHORED = "authored"
    MERGE_RESOLUTION = "merge-resolution"
    REVIEWER_FIX = "reviewer-fix"


def classify(
    prev_head: str, new_head: str, *, merged_in_range: bool, answered_in_range: bool
) -> CommitProvenance:
    if prev_head == "" or new_head == prev_head:
        return CommitProvenance.UNMOVED
    if merged_in_range:
        return CommitProvenance.MERGE_RESOLUTION
    if answered_in_range:
        return CommitProvenance.REVIEWER_FIX
    return CommitProvenance.AUTHORED


def is_forced_round(provenance: CommitProvenance) -> bool:
    return provenance in {CommitProvenance.MERGE_RESOLUTION, CommitProvenance.REVIEWER_FIX}
