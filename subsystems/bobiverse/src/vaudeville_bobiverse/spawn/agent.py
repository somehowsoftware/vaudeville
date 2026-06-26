from __future__ import annotations

import os
import shlex
from collections.abc import Sequence

# Auto mode evaluates each tool call for risk and prompt injection, running the
# safe ones and blocking the risky ones. The operator accepts it once on the
# host (a one-time dialog); later spawns see no interstitial.
#
# CLAUDE_CODE_DISABLE_AUTO_MEMORY turns off Claude Code's built-in auto-memory.
# Vaudeville keeps durable cross-agent facts in Doctrine, not a per-agent store;
# left on, the harness prompts each Bob to record one, which no_memory_writes
# denies only after the Bob has stalled generating it and polluted its context.
# Disabling at launch removes the prompt, so no Bob ever reaches for the deny.
#
# --disallowedTools AskUserQuestion is a bare-name deny: it drops the tool from
# the advertised toolset so the model never sees it, rather than leaving it
# advertised and refusing the call at runtime. Vaudeville addresses David in
# prose, never a multiple-choice menu; advertised, the tool is a banana peel a
# policy-naive Bob reaches for and burns a turn on the refusal. The trailing
# --remote-control flag agent_command appends terminates this variadic option.
SPAWN_AGENT = (
    "CLAUDE_AUTONOMOUS=1 CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 /usr/bin/claude "
    "--model opus --permission-mode auto --disallowedTools AskUserQuestion"
)

# A window `workmux add` creates inherits the tmux server's environment, not the
# spawning shell's, so these values reach the spawned claude only when baked
# onto its command line. They matter when a rehearse points the lifecycle at a
# Staged Scaffold rather than the host install:
#   - CLAUDE_CONFIG_DIR: where `claude --resume` looks for the Foundation
#     transcript, and where it loads skills and hooks from.
#   - PATH: which `vv`/`vv-bob`/`vv-cue`/`vv-pm` and the exit teardown resolve to.
#   - VV_DATA_DIR: where vv reads and writes Foundation state.
_PROPAGATED_ENV_VARS = ("CLAUDE_CONFIG_DIR", "VV_DATA_DIR", "PATH")


def agent_command(propagated_environment: Sequence[tuple[str, str]], worktree: str) -> str:
    environment_assignments = " ".join(
        f"{name}={shlex.quote(value)}" for name, value in propagated_environment
    )
    parts = [environment_assignments, SPAWN_AGENT, "--remote-control", shlex.quote(worktree)]
    return " ".join(part for part in parts if part)


def propagated_environment() -> list[tuple[str, str]]:
    return [(name, os.environ[name]) for name in _PROPAGATED_ENV_VARS if os.environ.get(name)]
