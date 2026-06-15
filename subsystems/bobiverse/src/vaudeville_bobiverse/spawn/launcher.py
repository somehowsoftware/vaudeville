"""Compose the configured downstream into a launcher file for /spawn."""

from __future__ import annotations

from pathlib import Path

from vaudeville_core import downstream_command

from vaudeville_bobiverse.spawn.runner import downstream_args, run_downstream


def write_launcher(repo_root: Path, premise_id: str, body: str) -> Path:
    scratch_dir = repo_root / ".scratch"
    scratch_dir.mkdir(exist_ok=True)
    launcher = scratch_dir / f"launcher-{premise_id}.md"
    launcher.write_text(body)
    return launcher


def spawn_launcher(premise_id: str, *, repo_root: Path | None = None) -> Path:
    if repo_root is None:
        from vaudeville_bobiverse.spawn.target_repo import resolve_target_repo

        repo_root = resolve_target_repo(premise_id)
    argv = [*downstream_command(), *downstream_args(premise_id)]
    body = run_downstream(argv)
    return write_launcher(repo_root, premise_id, body)


def main(premise_id: str) -> None:
    launcher = spawn_launcher(premise_id)
    print(launcher)
