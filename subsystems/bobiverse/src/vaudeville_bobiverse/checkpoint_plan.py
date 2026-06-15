from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from vaudeville_bobiverse.checkpoint_layout import CheckpointLayout
from vaudeville_bobiverse.digest import Section, render
from vaudeville_bobiverse.digest_store import serialize_sections
from vaudeville_bobiverse.resume_brief import resume_brief

SESSION_ID_ENV = "CLAUDE_CODE_SESSION_ID"

CHECKPOINT_REFUSED_EXIT = 2

_DRIVE_SUBCOMMAND = "checkpoint-drive"

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


def plan_checkpoint(
    continuation: str | None,
    carryover: str,
    sections: tuple[Section, ...] | None,
    *,
    deployed_skills: frozenset[str] | set[str],
    layout: CheckpointLayout,
    pane: str,
    transcript_dir: Path,
) -> CheckpointRefusal | CheckpointPlan:
    if continuation is not None and continuation not in deployed_skills:
        return CheckpointRefusal(
            f"continuation skill /{continuation} is not deployed; a /clear now would strand "
            "this Bob in a cleared session with no way back. Redeploy the scaffold so the "
            "skill resolves, then retry."
        )
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
            (layout.resume_brief, resume_brief(render(sections), carryover, continuation)),
        ),
        # Re-invoke the entry point that's running (sys.argv[0]) with the driver
        # subcommand, not `python -m vaudeville_bobiverse...`: a fresh `-m` child does
        # not go through the shiv zipapp's bootstrap, so under the packaged build the
        # package is not importable and the detached driver dies before /clear. Re-
        # entering sys.argv[0] resolves the package the same way the running command did.
        launch=(
            sys.executable,
            sys.argv[0],
            _DRIVE_SUBCOMMAND,
            pane,
            str(transcript_dir),
            str(layout.resume_brief),
        ),
    )
