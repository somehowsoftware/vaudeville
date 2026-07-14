from __future__ import annotations

from pathlib import Path

from vaudeville_core import downstream_command

from vaudeville_bobiverse.spawn.refusal import Refusal, refuse
from vaudeville_bobiverse.spawn.runner import downstream_args, run_downstream


def write_launcher(repo_root: Path, assignment_id: str, body: str) -> Path:
    scratch_dir = repo_root / ".scratch"
    scratch_dir.mkdir(exist_ok=True)
    launcher = scratch_dir / f"launcher-{assignment_id}.md"
    launcher.write_text(body)
    return launcher


def spawn_launcher(assignment_id: str, *, repo_root: Path | None = None) -> Path:
    if repo_root is None:
        # Only the standalone `vv spawn-launcher` reaches this branch; `vv spawn`
        # resolves the target up front and passes it in. Here there is no higher
        # composition root, so a refusal is rendered and exits rather than returned.
        from vaudeville_bobiverse.spawn.target_repo import resolve_target_repo

        resolved = resolve_target_repo(assignment_id)
        if isinstance(resolved, Refusal):
            refuse(resolved)
        repo_root = resolved
    argv = [*downstream_command(), *downstream_args(assignment_id)]
    body = run_downstream(argv)
    return write_launcher(repo_root, assignment_id, body)


def main(assignment_id: str) -> None:
    launcher = spawn_launcher(assignment_id)
    print(launcher)
