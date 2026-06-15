"""Current reading — a registered project's source as it currently,
canonically is, handed to a caller for the span of one read.

A Bob reads sibling projects (a peer Managed Repository, the doctrine
repo) for cross-context. A Current reading makes that read current by
construction: the caller receives the project's source at its canonical
current state and reads it with ordinary tools, rather than trusting a
long-lived local clone that may have drifted from the canonical history.

The caller names the project by prefix; resolving where a project's
canonical history lives is the register's job (``config_file``), and the
git boundary that materialises and tears down the reading is this
module's — like ``worktree``, it shells out to git. Neither the location
nor the teardown surfaces to the caller.
"""

from __future__ import annotations

import subprocess
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from vaudeville_core.config_file import (
    VAUDEVILLE_FILENAME,
    _abort,
    host_config_path,
    managed_repository_for_project,
)


@contextmanager
def current_reading_of_project(
    prefix: str, *, host_config_dir: Path | None = None
) -> Iterator[Path]:
    """Hand the caller project ``prefix``'s source as it currently is.

    Yields a path to read for the duration of the ``with`` block; the
    reading is torn down when the block exits.
    """
    repository = managed_repository_for_project(prefix, host_config_dir=host_config_dir)
    if repository.remote is None:
        register = host_config_path(VAUDEVILLE_FILENAME, host_config_dir)
        _abort(
            f"{register}: project {prefix!r} has no `remote`. "
            "A Fresh clone reads the project's current remote tip, so the entry needs "
            "its git URL."
        )
    with _current_reading_from(repository.remote) as source:
        yield source


@contextmanager
def _current_reading_from(remote: str) -> Iterator[Path]:
    with tempfile.TemporaryDirectory(prefix="vaudeville-current-reading-") as scratch:
        source = Path(scratch) / "source"
        result = subprocess.run(
            ["git", "clone", "--quiet", remote, str(source)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            detail = result.stderr.strip() or "git failed"
            _abort(f"could not read project at {remote!r} ({detail})")
        yield source
