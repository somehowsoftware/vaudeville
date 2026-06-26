from __future__ import annotations

import subprocess
from pathlib import Path


def observe_origin(clone: Path) -> str | None:
    # `git config --get` exits non-zero when the key is absent: i.e. the clone
    # has no `origin` remote at all, the host-state the incident hit. Captured,
    # not printed, so a clone with no origin reads as a value rather than noise.
    result = subprocess.run(
        ["git", "-C", str(clone), "config", "--get", "remote.origin.url"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def origin_drift_refusal(
    clone: Path, declared_remote: str | None, observed_origin: str | None
) -> str | None:
    # Absent-origin only. A clone whose `origin` is present but points elsewhere
    # is a separate, silent fault (it fetches the wrong history rather than
    # failing) and catching it safely needs URL normalization, so it is out of
    # scope here. When the registry declares no remote there is no canonical URL
    # to name, so there is nothing to refuse.
    if declared_remote is not None and observed_origin is None:
        return (
            f"{clone} has no 'origin' remote, but the registry declares "
            f"{declared_remote!r} as its canonical remote. Re-add origin before "
            f"spawning a Bob here:\n"
            f"    git -C {clone} remote add origin {declared_remote}"
        )
    return None
