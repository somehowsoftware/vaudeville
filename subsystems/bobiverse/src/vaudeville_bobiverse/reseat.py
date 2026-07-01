from __future__ import annotations

import json
import shlex
import subprocess
import sys
from pathlib import Path

from vaudeville_bobiverse.spawn.agent import agent_script_body, propagated_environment

# A reseat hands claude the Resume Brief as its positional first turn, and a single argv
# argument caps near MAX_ARG_STRLEN (128 KiB on Linux). A Brief past that ceiling cannot
# land, so refuse before the destructive respawn: the fail-safe leaves the live session
# whole rather than killing it for a handoff that could never seat.
_BRIEF_ARG_CEILING = 100_000

BRIEF_TOO_LARGE_EXIT = 2
PANE_UNRESOLVED_EXIT = 2


def brief_fits(brief: str) -> bool:
    return len(brief.encode("utf-8")) <= _BRIEF_ARG_CEILING


def pane_from_status(status_json: str) -> str | None:
    # `workmux status <worktree> --json` reports the worktree's tmux pane; one worktree, one
    # pane. An empty report means the worktree has no live pane to reseat.
    entries = json.loads(status_json)
    return str(entries[0]["pane_id"]) if entries else None


def reseat_command(pane: str, agent_script: Path, brief_path: Path) -> list[str]:
    # `respawn-pane -k` replaces the pane's process in one act: it kills the current claude and
    # execs the fresh one, so a competing injector cannot swallow the handoff the way a sent
    # /clear could. The Brief is read from its file at exec time and reaches claude as a single
    # positional first turn; command-substitution output is not re-parsed, so the Brief's own
    # backticks and quotes stay inert. The agent script supplies the launch (flags, env,
    # --remote-control) and forwards the Brief as "$@"; no --resume, the conversation is shed,
    # not forked.
    launch = f'{shlex.quote(str(agent_script))} "$(cat {shlex.quote(str(brief_path))})"'
    return ["tmux", "respawn-pane", "-k", "-t", pane, launch]


def reseat(worktree: str, brief_path: Path) -> None:
    brief = brief_path.read_text(encoding="utf-8")
    if not brief_fits(brief):
        print(
            f"Error: Resume Brief is {len(brief.encode('utf-8'))} bytes, past the "
            f"{_BRIEF_ARG_CEILING}-byte ceiling for claude's positional first turn; the reseat "
            "could not land it. Refusing before the respawn, so the live session survives.",
            file=sys.stderr,
        )
        sys.exit(BRIEF_TOO_LARGE_EXIT)
    status = subprocess.run(  # noqa: S603, S607
        ["workmux", "status", worktree, "--json"], capture_output=True, text=True, check=True
    ).stdout
    pane = pane_from_status(status)
    if pane is None:
        print(
            f"Error: no workmux pane for worktree {worktree!r}; nothing to reseat.",
            file=sys.stderr,
        )
        sys.exit(PANE_UNRESOLVED_EXIT)
    # The launch is spawn's, reused verbatim (model, remote-control, autonomy, the env trio),
    # so the knowledge that births a Bob lives in one place; the only thing reseat does
    # differently is forward the Brief instead of letting workmux append the Foundation fork.
    agent_script = brief_path.parent / "reseat-agent.sh"
    agent_script.write_text(agent_script_body(propagated_environment(), worktree))
    agent_script.chmod(0o755)
    subprocess.run(reseat_command(pane, agent_script, brief_path), check=True)  # noqa: S603, S607


def main(worktree: str, brief_path: str) -> None:
    reseat(worktree, Path(brief_path))
