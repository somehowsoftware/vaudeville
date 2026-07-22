from __future__ import annotations

from collections.abc import Sequence

from vaudeville_cue.digest import Section

# The most consecutive stalls the chain tolerates before its successor surfaces. One: a
# single unsupervised, unproductive compression has no benign instance a second would only
# deepen, and the heads-down delivering Bob that resembles a stall is what a landed commit
# tells apart. Named, not inlined, because it is a calibration the field may move.
STALL_BOUND = 1


def made_contact(section: Section) -> bool:
    return bool(section.turns)


def made_progress(section: Section, prior: Section) -> bool:
    # A landed commit moves the work's recorded position off where the prior session left
    # it. A head unknown on either side cannot witness a move, so it reads as no progress
    # — the safe direction, since an uncertain proxy resolving toward "unproductive" costs
    # only a surfaced status, while the opposite lets a runaway pass.
    return section.head is not None and prior.head is not None and section.head != prior.head


def stalled(section: Section, prior: Section | None) -> bool:
    # The chain's origin has no predecessor to measure progress against and is never
    # itself a stall: a Bob's first checkpoint does not surface. A run of stalls is
    # measured from the origin, not through it.
    if prior is None:
        return False
    return not made_contact(section) and not made_progress(section, prior)


def stall_depth(sections: Sequence[Section]) -> int:
    depth = 0
    for index in range(len(sections) - 1, -1, -1):
        prior = sections[index - 1] if index > 0 else None
        if not stalled(sections[index], prior):
            break
        depth += 1
    return depth


def has_run_away(sections: Sequence[Section], *, bound: int = STALL_BOUND) -> bool:
    return stall_depth(sections) >= bound
