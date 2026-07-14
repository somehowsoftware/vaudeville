from __future__ import annotations

import sys
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import NoReturn, TypeVar


@dataclass(frozen=True)
class Refusal:
    # One refusal type for every gate, carrying its own exit code as a value, so the
    # code a caller exits with travels with the message it belongs to instead of
    # living in a constant beside the gate, free to drift out of sync.
    message: str
    exit_code: int


def refuse(refusal: Refusal) -> NoReturn:
    # The one place a Refusal is rendered: gates return it as a value and never write
    # to stderr themselves, so this is the only point a refusal reaches the outside world.
    print(refusal.message, file=sys.stderr)
    sys.exit(refusal.exit_code)


T = TypeVar("T")


def refuse_or_clear(
    clearances: Iterable[Callable[[T], Refusal | T]],
    start: T,
) -> Refusal | T:
    # Short-circuits on the first refusal: a later clearance never runs once an earlier
    # one has refused, so its own checks are skipped for a spawn that cannot proceed.
    cleared = start
    for clearance in clearances:
        outcome = clearance(cleared)
        if isinstance(outcome, Refusal):
            return outcome
        cleared = outcome
    return cleared
