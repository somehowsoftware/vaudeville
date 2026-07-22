from __future__ import annotations

import json
import shlex
import subprocess
import sys
from pathlib import Path

from vaudeville_bobiverse.spawn.agent import Launch, propagated_environment

PANE_UNRESOLVED_EXIT = 2
BRIEF_UNREADABLE_EXIT = 3


def pane_from_status(status_json: str) -> str | None:
    # `workmux status <worktree> --json` reports the worktree's tmux pane; one worktree, one
    # pane. An empty report means the worktree has no live pane to reseat.
    entries = json.loads(status_json)
    return str(entries[0]["pane_id"]) if entries else None


def reseat_command(pane: str, agent_script: Path) -> list[str]:
    # `respawn-pane -k` replaces the pane's process in one act: it kills the current claude and
    # execs the fresh one, so a competing injector cannot swallow the handoff the way a sent
    # /clear could. The launch runs the reused agent script and nothing else: the script reads the
    # Brief from its file on claude's stdin (never argv), so no `pkill -f` matching a word inside
    # the Brief can reap this pane. The script supplies the whole launch (flags, env,
    # --remote-control) and forwards nothing as "$@" -- no --resume, the conversation is shed,
    # not forked.
    return ["tmux", "respawn-pane", "-k", "-t", pane, shlex.quote(str(agent_script))]


def reseat(worktree: str, brief_path: Path, model: str | None = None) -> None:
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
    # respawn-pane -k is reseat's one destructive step: it kills the live claude before the
    # fresh one reads the Brief (from its own stdin, in the respawned shell). Read the Brief
    # here first, in the parent, so a missing or unreadable handoff file refuses like a missing
    # pane -- before the respawn, leaving the live session whole -- rather than killing the pane
    # and then stranding it when the redirect fails.
    try:
        brief_path.read_text()
    except OSError as err:
        print(
            f"Error: Resume Brief {str(brief_path)!r} is unreadable ({err}); refusing to reseat "
            f"worktree {worktree!r} before the destructive respawn, leaving the live session "
            f"whole.",
            file=sys.stderr,
        )
        sys.exit(BRIEF_UNREADABLE_EXIT)
    launch = Launch.compose(
        worktree=worktree,
        launch_turn=brief_path,
        environment=propagated_environment(),
        model=model,
    )
    agent_script = brief_path.parent / "reseat-agent.sh"
    agent_script.write_text(launch.script())
    agent_script.chmod(0o755)
    subprocess.run(reseat_command(pane, agent_script), check=True)  # noqa: S603, S607


def main(worktree: str, brief_path: str, model: str | None = None) -> None:
    reseat(worktree, Path(brief_path), model)
