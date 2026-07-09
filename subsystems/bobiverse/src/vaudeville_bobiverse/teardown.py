from __future__ import annotations

import os
import subprocess
from importlib import resources
from pathlib import Path

WORKTREES_SUFFIX = "__worktrees"


def archive_root_for_worktree(worktree_toplevel: Path) -> Path:
    parent = worktree_toplevel.parent
    if not parent.name.endswith(WORKTREES_SUFFIX):
        raise RuntimeError(
            f"worktree {worktree_toplevel} does not match the "
            f"<repo>{WORKTREES_SUFFIX}/<name> convention; refusing to "
            f"derive archive root."
        )
    return parent.parent / f"{parent.name}__archive"


def derive_archive_root(cwd: Path | None = None) -> Path:
    cwd = (cwd or Path.cwd()).resolve()
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"cwd {cwd} is not inside a git worktree "
            f"({result.stderr.strip() or 'git rev-parse failed'})."
        )
    return archive_root_for_worktree(Path(result.stdout.strip()).resolve())


def launch_teardown(worktree_name: str | None, archive_root: Path) -> None:
    env = os.environ.copy()
    env["WORKTREE_ARCHIVE_ROOT"] = str(archive_root)
    script_ref = resources.files("vaudeville_bobiverse").joinpath(
        "scripts/teardown-archive-and-remove.sh"
    )
    with resources.as_file(script_ref) as script_path:
        args = ["bash", str(script_path)]
        if worktree_name:
            args.append(worktree_name)
        # This teardown kills the tmux pane of the agent that launched it, so it
        # must outlive that agent; start_new_session detaches it into its own session.
        # Popen dups the fd into the child, so the parent's copy closes safely after spawn.
        with Path("/tmp/teardown-archive.log").open("ab") as log:
            subprocess.Popen(  # noqa: S603
                args,
                stdin=subprocess.DEVNULL,
                stdout=log,
                stderr=log,
                start_new_session=True,
                env=env,
            )


def run(worktree_name: str | None) -> None:
    launch_teardown(worktree_name, derive_archive_root())
