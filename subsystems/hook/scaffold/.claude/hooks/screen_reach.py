#!/usr/bin/env python3
"""The reach of a screen: whether a stock screen is switched off for the
Component of the session that is firing it.

A guard hook imports `screen_disabled_here`, declares its own screen name, and
passes the action through when the call returns True. The reach decision is
single-sourced here; a guard adds only its name and honours the verdict.

Stdlib only. This runs under the system python3 that Claude Code invokes for a
hook, with no virtualenv, so it cannot import any vaudeville package. It
re-derives the Component-from-cwd resolution vaudeville-core owns and reads the
same host register (`~/.vaudeville/vaudeville.toml`, redirected by VV_DATA_DIR)
the same way. Reading one immutable value at a second edge is not the shared
kernel; the single-sourced thing is the reach decision, which lives in
`screen_disabled`.

Fail-safe: every read that can fail resolves to "not disabled", so a guard that
cannot tell whether its screen is switched off enforces rather than letting an
action through unchecked.
"""

from __future__ import annotations

import os
import subprocess
import tomllib
from collections.abc import Collection
from pathlib import Path

VAUDEVILLE_FILENAME = "vaudeville.toml"


def screen_disabled(screen_name: str, disabled_here: Collection[str]) -> bool:
    """The reach decision as values: a screen is switched off here iff its name
    is among the screens disabled for this Component. An absent name, or an
    empty set (an unregistered Component, an unreadable register), is not
    disabled, so the guard enforces."""
    return screen_name in disabled_here


def screen_disabled_here(screen_name: str, cwd: str | None) -> bool:
    """Whether `screen_name` is switched off for the Component rooted at `cwd`,
    the session working directory Claude Code delivers on the hook payload.
    Fail-safe: any failure to resolve the Component or read its reach
    configuration returns False, so the guard enforces."""
    clone_root = _main_clone_root(cwd)
    if clone_root is None:
        return False
    return screen_disabled(screen_name, _disabled_screens_for_clone(clone_root))


def _main_clone_root(cwd: str | None) -> Path | None:
    """The main clone's root for the working tree at `cwd`, the path the host
    register keys a Component on. Mirrors vaudeville-core's `main_repo_root`:
    --git-common-dir, not --show-toplevel, because on a linked worktree the
    latter returns the worktree and misses the register entry. None when `cwd`
    is absent or names no git repository."""
    if not cwd:
        return None
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-common-dir"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    git_common = Path(result.stdout.strip())
    if not git_common.is_absolute():
        git_common = (Path(cwd) / git_common).resolve()
    return git_common.parent.resolve()


def _disabled_screens_for_clone(clone_root: Path) -> frozenset[str]:
    """The screen names switched off for the Component whose main clone is
    `clone_root`, read from the host register's project map. Empty when the
    register is absent or malformed, the Component is unregistered, or the entry
    carries no well-formed `disabled_screens` list."""
    try:
        with _register_path().open("rb") as handle:
            raw = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError):
        return frozenset()
    projects = raw.get("projects")
    if not isinstance(projects, dict):
        return frozenset()
    for entry in projects.values():
        if not isinstance(entry, dict):
            continue
        repo_path = entry.get("repo_path")
        if not isinstance(repo_path, str):
            continue
        if Path(repo_path).expanduser().resolve() == clone_root:
            return _screen_names(entry.get("disabled_screens"))
    return frozenset()


def _screen_names(value: object) -> frozenset[str]:
    """A `disabled_screens` field coerced to a set of screen names, empty for
    anything that is not a list of strings."""
    if not isinstance(value, list):
        return frozenset()
    return frozenset(name for name in value if isinstance(name, str))


def _register_path() -> Path:
    """The host register path, honouring VV_DATA_DIR the way vaudeville-core's
    `_default_data_dir` does."""
    override = os.environ.get("VV_DATA_DIR")
    base = Path(override) if override else Path.home() / ".vaudeville"
    return base.expanduser().resolve() / VAUDEVILLE_FILENAME
