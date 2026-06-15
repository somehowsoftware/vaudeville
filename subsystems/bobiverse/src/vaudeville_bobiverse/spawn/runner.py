"""Run the configured /spawn downstream as a subprocess.

The downstream contract surface:
    <command> <premise-id>
"""

from __future__ import annotations

import subprocess
import sys

COMMAND_NOT_FOUND_EXIT = 127


def downstream_args(premise_id: str) -> list[str]:
    return [premise_id]


def run_downstream(argv: list[str]) -> str:
    try:
        result = subprocess.run(argv, capture_output=True, text=True, check=False)
    except FileNotFoundError:
        print(
            f"Error: downstream command {argv[0]!r} not found on PATH. "
            f"Check [spawn.downstream] command in ~/.vaudeville/vaudeville.toml — "
            f"the binary may be missing or misnamed.",
            file=sys.stderr,
        )
        sys.exit(COMMAND_NOT_FOUND_EXIT)

    if result.returncode != 0:
        if result.stderr:
            sys.stderr.write(result.stderr)
        print(
            f"Error: downstream {argv[0]!r} exited with status {result.returncode}.",
            file=sys.stderr,
        )
        sys.exit(result.returncode)

    return result.stdout
