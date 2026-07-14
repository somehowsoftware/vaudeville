from __future__ import annotations

import subprocess
import sys
from collections.abc import Callable, Mapping
from typing import NoReturn

ClassifyConcern = Callable[[str, Mapping[str, str]], str]

_MODEL = "sonnet"


def classify_concern(concern: str, descriptions: Mapping[str, str]) -> str:
    # The choice must depend only on the prompt, never on the cwd the capturing
    # thread sits in; otherwise the originating Component biases it, the very
    # misfiling this classifier exists to prevent. --safe-mode drops cwd/config
    # customization (CLAUDE.md, skills, hooks, MCP), --tools "" drops filesystem
    # access, and stdin=DEVNULL drops the pipe claude -p would otherwise read.
    # Not --bare: bare refuses the OAuth/keychain auth this deployment runs on.
    result = subprocess.run(
        [
            "claude",
            "-p",
            _classification_prompt(concern, descriptions),
            "--model",
            _MODEL,
            "--safe-mode",
            "--tools",
            "",
        ],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        _abort(f"the concern classifier exited {result.returncode}: {result.stderr.strip()}")
    answer = result.stdout.strip()
    if not answer:
        _abort("the concern classifier returned no answer.")
    return answer


def _classification_prompt(concern: str, descriptions: Mapping[str, str]) -> str:
    register = "\n".join(f"- {prefix}: {summary}" for prefix, summary in descriptions.items())
    return (
        "Decide which one Component a captured concern belongs to, by its subject.\n\n"
        f"Components:\n{register}\n\n"
        f"Concern:\n{concern}\n\n"
        "Reply with exactly one Component prefix from the list above: the prefix "
        "only, in uppercase, with no punctuation and no explanation."
    )


def _abort(message: str) -> NoReturn:
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(1)
