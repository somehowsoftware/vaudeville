"""Unreadable source: the prime-time verdict that a Component's Foundation
cannot be forked because its current reading cannot be obtained.

Priming forks each Component's Foundation from its current reading, which
vaudeville-core sources by cloning the Component's remote. When that clone
cannot be read or authenticated, core aborts the acquisition with a bare
``SystemExit`` — the same untyped exit a failure *inside* the fork (the Claude
turn) raises. This module is the prime-side boundary that tells the two apart:
it enters the reading, and a ``SystemExit`` from the acquisition (the clone, in
``__enter__``) becomes the typed ``UnreadableSource`` verdict, while a
``SystemExit`` from the caller's block is left to propagate as itself. The
tightness of that catch — acquisition only — is the whole discriminator, which
is why prime never needs core to change to name this failure.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import AbstractContextManager, contextmanager
from pathlib import Path

from vaudeville_core import current_reading_of_component


class UnreadableSource(Exception):
    """A Component's current reading could not be obtained: its remote could
    not be read or authenticated. Carries the Component ``prefix`` so the
    prime report can name which Component's source was unreadable."""

    def __init__(self, prefix: str) -> None:
        super().__init__(prefix)
        self.prefix = prefix


@contextmanager
def readable_reading(
    prefix: str,
    *,
    acquire: Callable[[str], AbstractContextManager[Path]] = current_reading_of_component,
) -> Iterator[Path]:
    """Yield Component ``prefix``'s current reading, or raise ``UnreadableSource``.

    The clone runs in the reading's ``__enter__``; a ``SystemExit`` there means
    the source could not be read or authenticated, and is re-raised as
    ``UnreadableSource``. A ``SystemExit`` from the ``with`` block this yields
    into (the Claude fork) is not an acquisition failure, so it propagates
    unchanged and stays a generic exit. ``acquire`` is injected so tests can
    drive the diagnostic path with a fake that aborts at entry, no real git.
    """
    reading = acquire(prefix)
    try:
        source = reading.__enter__()
    except SystemExit as acquisition_failed:
        raise UnreadableSource(prefix) from acquisition_failed
    try:
        yield source
    except BaseException as body_error:
        if not reading.__exit__(type(body_error), body_error, body_error.__traceback__):
            raise
    else:
        reading.__exit__(None, None, None)


def unreadable_source_line(prefix: str, log_path: Path | None = None) -> str:
    """The operator-facing report line for an unreadable source: name the
    Component, say its remote could not be read or authenticated, and point at
    the remedy. ``log_path`` is appended when priming streamed to a log file."""
    line = (
        f"{prefix} FAILED: its Component remote could not be read or authenticated. "
        "Wire git credentials for your Component remotes, then re-prime."
    )
    if log_path is not None:
        line = f"{line} log: {log_path}"
    return line
