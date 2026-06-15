"""Resolving the current project from the git working tree.

The git boundary: it asks git for the repository root of a working
directory — a main clone or a linked worktree — and looks that root up in
the project register read from the host config.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from vaudeville_core.config_file import (
    VAUDEVILLE_FILENAME,
    _abort,
    host_config_path,
    load_config,
)
from vaudeville_core.project import project_for_repo_root


def main_repo_root(cwd: Path) -> Path:
    # --git-common-dir, not --show-toplevel: on a worktree the latter returns
    # the worktree path, missing the vaudeville.toml entry that keys on the
    # main clone.
    result = subprocess.run(
        ["git", "rev-parse", "--git-common-dir"],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        _abort(
            f"cwd {cwd} is not inside a git repository "
            f"({result.stderr.strip() or 'git rev-parse failed'})."
        )
    git_common = Path(result.stdout.strip())
    if not git_common.is_absolute():
        git_common = (cwd / git_common).resolve()
    return git_common.parent.resolve()


def project_from_cwd(cwd: Path | None = None, *, host_config_dir: Path | None = None) -> str:
    cwd = (cwd or Path.cwd()).resolve()
    repo_root = main_repo_root(cwd)
    config = load_config(host_config_dir)
    project = project_for_repo_root(config, repo_root)
    if project is None:
        known = ", ".join(
            f"{candidate.prefix}={candidate.repo_path}"
            for candidate in sorted(config.projects.values(), key=lambda p: p.prefix)
        )
        register = host_config_path(VAUDEVILLE_FILENAME, host_config_dir)
        _abort(
            f"repo at {repo_root} is not registered in "
            f"{register}. Known mappings: {known or '(none)'}."
        )
    return project.prefix
