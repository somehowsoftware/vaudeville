from __future__ import annotations

import sys
from pathlib import Path
from typing import NoReturn

from vaudeville_bobiverse import foundation


def stranded_foundations(
    recorded: dict[str, str], stored_session_ids: set[str]
) -> list[tuple[str, str]]:
    return [
        (prefix, session_id)
        for prefix, session_id in sorted(recorded.items())
        if session_id not in stored_session_ids
    ]


def verify(recorded: dict[str, str], store: Path) -> None:
    if not recorded:
        _abort("no Foundations recorded in foundations.toml; run `vv prime` before deploying")
    stranded = stranded_foundations(recorded, foundation.stored_session_ids(store))
    if stranded:
        listing = ", ".join(f"{prefix} ({session_id})" for prefix, session_id in stranded)
        _abort(
            f"Foundations recorded but not present in the store ({store}): {listing}. "
            "Re-prime with `vv prime` so future spawns and forks resolve them."
        )
    print(f"All {len(recorded)} Foundations are present in the store ({store}).")


def _abort(message: str) -> NoReturn:
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(1)
