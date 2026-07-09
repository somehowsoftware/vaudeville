from __future__ import annotations

import fcntl
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def locked(lock_file: Path) -> Iterator[None]:
    # An exclusive advisory lock held across a critical section, so writers from
    # separate processes serialize where the resource they touch cannot survive a
    # race. The lock lives on a dedicated `.lock` sidecar, never the guarded
    # resource itself, so acquiring it neither reads nor truncates what it guards.
    # The lock releases when the handle closes, including on process death, so a
    # crashed holder never strands the next writer.
    lock_file.parent.mkdir(parents=True, exist_ok=True)
    with lock_file.open("w") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        yield
