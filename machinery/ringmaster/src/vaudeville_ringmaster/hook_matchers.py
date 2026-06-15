"""The Hook Matchers slot."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_SCAFFOLD_PATH = Path("scaffold") / ".claude" / "hooks.json"


@dataclass(frozen=True)
class HookMatchers:
    source_path: Path
    content: dict[str, Any]


class MalformedHookMatchers(ValueError):
    pass


def hook_matchers_declared_in(content: object, source_path: Path) -> HookMatchers:
    if not isinstance(content, dict):
        raise MalformedHookMatchers(
            f"{source_path}: top-level value must be a JSON object mapping event names to "
            "matcher lists"
        )
    return HookMatchers(source_path=source_path, content=content)


def read_hook_matchers_at(source_root: Path) -> HookMatchers | None:
    path = source_root / _SCAFFOLD_PATH
    if not path.is_file():
        return None
    with path.open() as f:
        content = json.load(f)
    return hook_matchers_declared_in(content, path)


def merge_hook_matchers(matchers: list[HookMatchers]) -> dict[str, list[Any]]:
    merged: dict[str, list[Any]] = {}
    for matcher in matchers:
        if not isinstance(matcher.content, dict):
            raise MalformedHookMatchers(
                f"{matcher.source_path}: top-level value must be a JSON object"
            )
        for event, entries in matcher.content.items():
            if not isinstance(entries, list):
                raise MalformedHookMatchers(
                    f"{matcher.source_path}: value for event {event!r} must be a list of "
                    "matcher entries"
                )
            merged.setdefault(event, []).extend(entries)
    return merged
