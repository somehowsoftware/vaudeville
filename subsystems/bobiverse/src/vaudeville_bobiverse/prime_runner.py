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
        # Truncate up front so a re-priming run starts a fresh log rather than
        # appending onto a stale one.
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
