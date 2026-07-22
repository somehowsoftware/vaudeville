from __future__ import annotations

import os
import shlex
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

UNSAFE_SCRIPT_PATH_EXIT = 2

# Auto mode evaluates each tool call for risk and prompt injection, running the
# safe ones and blocking the risky ones. The operator accepts it once on the
# host (a one-time dialog); later spawns see no interstitial.
#
# CLAUDE_CODE_DISABLE_AUTO_MEMORY turns off Claude Code's built-in auto-memory.
# Vaudeville keeps durable cross-agent facts in Doctrine, not a per-agent store;
# left on, the harness prompts each Bob to record one, which no_memory_writes
# denies only after the Bob has stalled generating it and polluted its context.
# Disabling at launch removes the prompt, so no Bob ever reaches for the deny.
_LAUNCH_ENV = (("CLAUDE_AUTONOMOUS", "1"), ("CLAUDE_CODE_DISABLE_AUTO_MEMORY", "1"))

# We do not validate the model name: claude owns which models exist, so a chosen
# model is passed through opaquely rather than checked against a list of our own
# that would drift from claude's.
DEFAULT_MODEL = "opus"

# --disallowedTools is a bare-name deny: each listed tool is dropped from the
# advertised toolset so the model never sees it, rather than left advertised and
# refused at runtime, where it is a banana peel a policy-naive Bob reaches for and
# burns a turn on. Vaudeville addresses David in the chat, in prose: never
# AskUserQuestion's multiple-choice menu, and never an Artifact (a page rendered
# off to claude.ai) where a paragraph of chat belongs. On a plain orientation
# request a Bob otherwise reaches for that page, spending tokens and the
# conversation's focus on a surface David did not ask for.
_LAUNCH_FLAGS = "--permission-mode auto --disallowedTools AskUserQuestion Artifact"

# A window `workmux add` creates inherits the tmux server's environment, not the
# spawning shell's, so these values reach the spawned claude only when the launch
# script exports them. They matter when a rehearse points the lifecycle at a
# Rehearsal Installation rather than the host install:
#   - CLAUDE_CONFIG_DIR: where `claude --resume` looks for the Foundation
#     transcript, and where it loads skills and hooks from.
#   - PATH: which `claude`/`vv`/`vv-bob`/`vv-cue`/`vv-pm` and the exit teardown
#     resolve to. The script execs `claude` found on this PATH, so a host that
#     keeps the binary outside /usr/bin still launches.
#   - VV_DATA_DIR: where vv reads and writes Foundation state.
_PROPAGATED_ENV_VARS = ("CLAUDE_CONFIG_DIR", "VV_DATA_DIR", "PATH")


@dataclass(frozen=True)
class Launch:
    worktree: str
    launch_turn: Path
    environment: tuple[tuple[str, str], ...] = ()
    model: str = DEFAULT_MODEL

    @classmethod
    def compose(
        cls,
        *,
        worktree: str,
        launch_turn: Path,
        environment: Sequence[tuple[str, str]],
        model: str | None,
    ) -> Launch:
        return cls(worktree, launch_turn, tuple(environment), model or DEFAULT_MODEL)

    def script(self) -> str:
        # workmux runs this script for --agent and appends `--resume <foundation-session>`
        # after it, which "$@" forwards to claude. The environment is set by the script
        # rather than passed to workmux, so a value containing a space (a host PATH with
        # one) never reaches a tokenizer that would split it.
        #
        # claude reads its launch turn (the Launcher for a spawn, the Resume Brief for a
        # reseat) from launch_turn redirected onto stdin, never from argv. The redirect
        # trails "$@" so the fork workmux appends is the only positional argument, and the
        # turn's content -- which can carry any word -- stays off every process's command
        # line, so no `pkill -f <word-in-a-turn>` can ever match the agent.
        exports = "".join(
            f"export {name}={shlex.quote(value)}\n"
            for name, value in (*_LAUNCH_ENV, *self.environment)
        )
        return (
            f"#!/bin/sh\n{exports}"
            f"exec claude --model {shlex.quote(self.model)} {_LAUNCH_FLAGS}"
            f' --remote-control {shlex.quote(self.worktree)} "$@"'
            f" < {shlex.quote(str(self.launch_turn))}\n"
        )


def write_agent_script(clone: Path, launch: Launch) -> Path:
    # Named `claude` deliberately: workmux keys both the conversation fork (--fork)
    # and Claude Code's prompt-injection profile off the program's basename. The
    # per-worktree directory keeps concurrent spawns of one Component, which share
    # its clone, from clobbering each other's script.
    script_dir = clone / ".scratch" / launch.worktree
    script = script_dir / "claude"
    if shlex.quote(str(script)) != str(script):
        # workmux resolves --fork from the raw --agent value (a naive rsplit on '/')
        # but parses the launched command with shlex; a path needing shell quoting
        # satisfies one and breaks the other, so no Bob can launch from it. Name the
        # violation rather than spawn a Bob whose launch would silently fracture.
        print(
            f"Error: launch script path {str(script)!r} needs shell quoting; workmux "
            f"cannot launch a Bob from a clone path containing spaces or shell "
            f"metacharacters. Clone the Component to a path without them.",
            file=sys.stderr,
        )
        sys.exit(UNSAFE_SCRIPT_PATH_EXIT)
    script_dir.mkdir(parents=True, exist_ok=True)
    script.write_text(launch.script())
    script.chmod(0o755)
    return script


def propagated_environment() -> list[tuple[str, str]]:
    return [(name, os.environ[name]) for name in _PROPAGATED_ENV_VARS if os.environ.get(name)]
