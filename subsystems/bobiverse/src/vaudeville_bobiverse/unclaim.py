"""The `vv unclaim` atom: re-pool a Premise with no record it was claimed.

Unclaim is the bobiverse-local closeout transition. It writes State=Ready,
Workflow=Submitted, and clears the Assignee so the Premise looks as it did
before any Bob picked it up, and posts no comment — a successor picker sees a
Premise indistinguishable from one that was never claimed. PM's `vv resolve`
and `vv return` cover the kernel terminations (delivered, abandoned,
returned); this covers the Bob-session case where the worktree should never
have existed, which is a word about the Bob's relationship to the Premise
rather than about the Premise's own deliverable state.

The transition lives in `vaudeville_core`; this atom delegates to it with the
`UNCLAIM` profile and does nothing else. It does not tear the worktree down —
sequencing teardown after the transition is the caller's job.
"""

from __future__ import annotations

from collections.abc import Callable

from vaudeville_core import UNCLAIM, ExitProfile, apply_transition


def unclaim_premise(
    premise: str,
    *,
    transition: Callable[[str, ExitProfile], None] = apply_transition,
) -> None:
    transition(premise, UNCLAIM)
