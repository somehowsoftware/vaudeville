"""Run one priming ``claude`` invocation, optionally streamed to a log sink.

The thin shell around the priming subprocess: its only patchable surface is the
syscall, so the failure modes — missing ``claude`` (exit 127) and a non-zero
exit (propagated verbatim) — and the choice between inherited stdio and a log
sink are pinned here and nowhere else. ``begin_log`` truncates a sink up front so
a re-priming run never appends onto a stale log.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import NoReturn

from vaudeville_bobiverse.prime_invocations import ClaudeInvocation

CLAUDE_MISSING_EXIT = 127


def begin_log(log_path: Path | None) -> None:
    if log_path is not None:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_bytes(b"")


def run_claude(invocation: ClaudeInvocation) -> None:
    try:
        if invocation.log_path is None:
            result = subprocess.run(invocation.argv, cwd=invocation.cwd, check=False)
        else:
            with invocation.log_path.open("ab") as log:
                result = subprocess.run(
                    invocation.argv,
                    cwd=invocation.cwd,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    check=False,
                )
    except FileNotFoundError:
        _abort_no_claude()
    if result.returncode != 0:
        sys.exit(result.returncode)


def _abort_no_claude() -> NoReturn:
    print(
        "Error: `claude` not found on PATH. `vv prime` requires it.",
        file=sys.stderr,
    )
    sys.exit(CLAUDE_MISSING_EXIT)
