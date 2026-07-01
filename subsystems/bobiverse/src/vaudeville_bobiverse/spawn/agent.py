from __future__ import annotations

import os
import shlex
import sys
from collections.abc import Sequence
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

# --disallowedTools AskUserQuestion is a bare-name deny: it drops the tool from
# the advertised toolset so the model never sees it, rather than leaving it
# advertised and refusing the call at runtime. Vaudeville addresses David in
# prose, never a multiple-choice menu; advertised, the tool is a banana peel a
# policy-naive Bob reaches for and burns a turn on the refusal. The
# --remote-control flag that follows terminates this variadic option.
SPAWN_FLAGS = "--model opus --permission-mode auto --disallowedTools AskUserQuestion"

# A window `workmux add` creates inherits the tmux server's environment, not the
# spawning shell's, so these values reach the spawned claude only when the launch
# script exports them. They matter when a rehearse points the lifecycle at a
# Staged Scaffold rather than the host install:
#   - CLAUDE_CONFIG_DIR: where `claude --resume` looks for the Foundation
#     transcript, and where it loads skills and hooks from.
#   - PATH: which `claude`/`vv`/`vv-bob`/`vv-cue`/`vv-pm` and the exit teardown
#     resolve to. The script execs `claude` found on this PATH, so a host that
#     keeps the binary outside /usr/bin still launches.
#   - VV_DATA_DIR: where vv reads and writes Foundation state.
_PROPAGATED_ENV_VARS = ("CLAUDE_CONFIG_DIR", "VV_DATA_DIR", "PATH")


def agent_script_body(propagated_environment: Sequence[tuple[str, str]], worktree: str) -> str:
    # workmux runs the script for --agent and appends `--resume <foundation-session>`
    # after it, which "$@" forwards to claude. The environment is set by the script
    # rather than passed to workmux, so a value containing a space (a host PATH with
    # one) never reaches a tokenizer that would split it.
    exports = "".join(
        f"export {name}={shlex.quote(value)}\n"
        for name, value in (*_LAUNCH_ENV, *propagated_environment)
    )
    return (
        f"#!/bin/sh\n{exports}"
        f'exec claude {SPAWN_FLAGS} --remote-control {shlex.quote(worktree)} "$@"\n'
    )


def write_agent_script(
    clone: Path, worktree: str, propagated_environment: Sequence[tuple[str, str]]
) -> Path:
    # Named `claude` deliberately: workmux keys both the conversation fork (--fork)
    # and Claude Code's prompt-injection profile off the program's basename. The
    # per-worktree directory keeps concurrent spawns of one Component, which share
    # its clone, from clobbering each other's script.
    script_dir = clone / ".scratch" / worktree
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
    script.write_text(agent_script_body(propagated_environment, worktree))
    script.chmod(0o755)
    return script


def propagated_environment() -> list[tuple[str, str]]:
    return [(name, os.environ[name]) for name in _PROPAGATED_ENV_VARS if os.environ.get(name)]
