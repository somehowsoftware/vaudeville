from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from vaudeville_cue.checkpoint_layout import CheckpointLayout
from vaudeville_cue.digest import Section, render
from vaudeville_cue.digest_store import serialize_sections
from vaudeville_cue.resume_brief import resume_brief
from vaudeville_cue.runaway import has_run_away

SESSION_ID_ENV = "CLAUDE_CODE_SESSION_ID"

CHECKPOINT_REFUSED_EXIT = 2

_RESEAT_VERB = "reseat"

TRANSCRIPT_UNRESOLVED = (
    "this session's transcript could not be resolved "
    f"(${SESSION_ID_ENV} unset, or no transcript recorded for it), so the Digest "
    "cannot be extracted and a resumed Bob could not rebuild operator intent."
)


@dataclass(frozen=True)
class CheckpointRefusal:
    message: str
    exit_code: int = CHECKPOINT_REFUSED_EXIT


@dataclass(frozen=True)
class CheckpointPlan:
    writes: tuple[tuple[Path, str], ...]
    launch: tuple[str, ...]
    reseat_log: Path


def plan_checkpoint(
    carryover: str,
    sections: tuple[Section, ...] | None,
    *,
    layout: CheckpointLayout,
    pane: str,
) -> CheckpointRefusal | CheckpointPlan:
    if sections is None:
        return CheckpointRefusal(TRANSCRIPT_UNRESOLVED)
    if not carryover.strip():
        return CheckpointRefusal(
            "the Carryover is empty; a resumed Bob would have nothing to continue from. "
            "Author it and deliver it on stdin."
        )
    return CheckpointPlan(
        writes=(
            (layout.digest, serialize_sections(sections)),
            (layout.carryover, carryover),
            (
                layout.resume_brief,
                resume_brief(render(sections), carryover, surface_and_wait=has_run_away(sections)),
            ),
        ),
        # The detached handoff is bobiverse's `reseat` primitive: it replaces the
        # Bob's pane session in place, seeding the fresh session with the Resume Brief as
        # its born-grounded first turn. The session is replaced in one act, with nothing
        # to detect or observe. cue passes only the pane and the brief path; the launch
        # knowledge (model, remote-control, autonomy, the foundation it drops) is
        # bobiverse's alone. Re-invoke the running entry point (sys.argv[0]), not
        # `python -m`: a fresh `-m` child misses the shiv zipapp's bootstrap and dies
        # before reseating; sys.argv[0] resolves the assembled `vv` facade the way the
        # running command did, and the facade carries the verb.
        launch=(
            sys.executable,
            sys.argv[0],
            _RESEAT_VERB,
            pane,
            str(layout.resume_brief),
        ),
        reseat_log=layout.reseat_log,
    )
