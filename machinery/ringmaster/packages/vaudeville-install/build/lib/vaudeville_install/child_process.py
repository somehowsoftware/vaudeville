"""Run a child process under a bound, quietly: the installer's one subprocess boundary.

The sole importer of ``subprocess``, a line a fitness test holds so no unbounded, tty-inheriting
boundary can reappear. Infrastructure, not ubiquitous language: it names none of the domain's
pieces and cannot tell one boundary from another.
"""

from __future__ import annotations

import math
import os
import signal
import subprocess
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

GIT_TERMINAL_PROMPT_ENV = "GIT_TERMINAL_PROMPT"


@dataclass(frozen=True)
class Spec:
    argv: Sequence[str]
    env: Mapping[str, str]
    timeout: float
    capture_stdout: bool = True

    def __post_init__(self) -> None:
        # A zero, infinite, or missing bound is the hang this module forecloses.
        if not (math.isfinite(self.timeout) and self.timeout > 0):
            raise ValueError(
                f"a child-process Spec needs a finite positive timeout, got {self.timeout!r}"
            )


@dataclass(frozen=True)
class Completed:
    returncode: int
    stdout: str
    stderr: str


@dataclass(frozen=True)
class TimedOut:
    timeout: float


@dataclass(frozen=True)
class LaunchFailed:
    reason: str


# Three outcomes, never an exit code: a child that timed out or never launched stays distinct from
# one that ran and returned 124 or 127. A caller matches and interprets per boundary.
Outcome = Completed | TimedOut | LaunchFailed


def run(spec: Spec) -> Outcome:
    child_env = {**spec.env, GIT_TERMINAL_PROMPT_ENV: "0"}
    try:
        # `start_new_session` makes the child a session (and process-group) leader: the timeout can
        # kill the whole tree — the child and any git/claude it spawned — rather than the immediate
        # child alone, and stripping the controlling terminal reinforces stdin=DEVNULL and
        # GIT_TERMINAL_PROMPT=0 so a child cannot fall back to /dev/tty to prompt.
        process = subprocess.Popen(
            [*spec.argv],
            stdout=subprocess.PIPE if spec.capture_stdout else None,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
            text=True,
            env=child_env,
            start_new_session=True,
        )
    except OSError as launch_failure:
        # An absent or non-executable argv[0] never started; report it as its own outcome, not a
        # traceback escaping the boundary and not an invented exit code.
        return LaunchFailed(f"could not launch `{spec.argv[0]}`: {launch_failure}")
    try:
        stdout, stderr = process.communicate(timeout=spec.timeout)
    except subprocess.TimeoutExpired:
        _kill_process_group(process)
        # Drain and reap now that the group is dead: the kill closed every write end of the captured
        # pipes, so this returns rather than blocking on a grandchild holding one open.
        process.communicate()
        return TimedOut(spec.timeout)
    # A child run with stdout inherited (capture_stdout=False) comes back as None.
    return Completed(process.returncode, stdout or "", stderr or "")


def _kill_process_group(process: subprocess.Popen[str]) -> None:
    # The child leads its own process group (start_new_session), so SIGKILL the group to take its
    # wedged git/claude descendants down with it. If the group is already gone (the child raced us
    # to exit), fall back to killing the child by pid; either way the caller's communicate reaps it.
    try:
        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
    except ProcessLookupError, PermissionError:
        process.kill()
