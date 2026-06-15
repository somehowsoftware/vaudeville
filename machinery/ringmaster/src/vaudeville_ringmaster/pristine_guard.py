"""The Pristine guard: refuse any hot-fixed Session Clone, so the Host reflects only merged code."""

from __future__ import annotations

import subprocess

from vaudeville_ringmaster.session_clone import SessionClone, recorded_clone_sha_of


def session_clone_is_pristine(
    *, has_uncommitted_changes: bool, clone_time_sha: str | None, current_head_sha: str | None
) -> bool:
    if has_uncommitted_changes:
        return False
    if clone_time_sha is None or current_head_sha is None:
        return False
    return current_head_sha == clone_time_sha


def session_clone_is_pristine_on_disk(session_clone: SessionClone) -> bool:
    return session_clone_is_pristine(
        has_uncommitted_changes=_git_reports_uncommitted_changes(session_clone),
        clone_time_sha=recorded_clone_sha_of(session_clone),
        current_head_sha=_current_head_sha(session_clone),
    )


def enforce_pristine_guard_on(session_clones: list[SessionClone]) -> None:
    hot_fixed = [clone for clone in session_clones if not session_clone_is_pristine_on_disk(clone)]
    if hot_fixed:
        raise HotFixedSessionClones(hot_fixed)


class HotFixedSessionClones(RuntimeError):
    def __init__(self, session_clones: list[SessionClone]) -> None:
        super().__init__(session_clones)
        self.session_clones = session_clones

    def __str__(self) -> str:
        listing = ", ".join(clone.name for clone in self.session_clones)
        return (
            f"Hot-fixed Session Clones cannot be deployed: {listing}. "
            "Productionize each Hot-fix as a PR, merge it into the relevant Contributor's main, "
            "and re-run `ringmaster clone` before Apply."
        )


def _git_reports_uncommitted_changes(session_clone: SessionClone) -> bool:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=session_clone.path,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip() != ""


def _current_head_sha(session_clone: SessionClone) -> str | None:
    # `--verify HEAD` resolves the commit at HEAD, or exits non-zero when HEAD is unborn (a `.git`
    # with no commit). Report the absence rather than raising, so the decision fails closed on a
    # clone that is not a Clone-produced checkout instead of crashing the guard.
    result = subprocess.run(
        ["git", "rev-parse", "--verify", "HEAD"],
        cwd=session_clone.path,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()
