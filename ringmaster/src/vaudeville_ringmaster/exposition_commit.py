"""The git boundary for Publish: write an Exposition to the Published Home as one labeled commit."""

from __future__ import annotations

import shutil
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Protocol

from vaudeville_ringmaster.published_home import GitOutcome

# The identity the integrator's release commits carry on the Published Home.
_COMMIT_AUTHOR_NAME = "Vaudeville Ringmaster"
_COMMIT_AUTHOR_EMAIL = "agents@somehowsoftware.com"


class CommitExposition(Protocol):
    def __call__(self, *, repository: str, version: str, exposition: Path) -> str: ...


def exposition_commit_message(version: str) -> str:
    return f"{version}: source exposition"


def https_clone_url(repository: str) -> str:
    # Clone the Published Home over an explicit HTTPS URL rather than the scheme-less `owner/repo`
    # form, which `gh` resolves to the operator's `git_protocol`. Under `git_protocol = ssh` the
    # scheme-less form makes `origin` an SSH remote, so the push would authenticate with the
    # operator's SSH key instead of the resolved token. Pinning HTTPS, together with the runner's
    # credential helper, keeps the token-backed push deterministic.
    return f"https://github.com/{repository}"


def place_exposition_in_checkout(checkout: Path, exposition: Path) -> None:
    # Replace the checkout's prior Exposition wholesale while preserving its `.git`, so the new
    # commit extends the Published Home's history rather than orphaning it.
    for entry in checkout.iterdir():
        if entry.name == ".git":
            continue
        if entry.is_dir() and not entry.is_symlink():
            shutil.rmtree(entry)
        else:
            entry.unlink()
    for entry in exposition.iterdir():
        target = checkout / entry.name
        if entry.is_dir() and not entry.is_symlink():
            shutil.copytree(entry, target, symlinks=True)
        else:
            shutil.copy2(entry, target)


def commit_exposition_with_git(
    *,
    repository: str,
    version: str,
    exposition: Path,
    run_git: Callable[[list[str]], GitOutcome],
) -> str:
    # Returns the SHA of the commit it pushed, so Publish can pin the Release tag to exactly this
    # commit rather than to whatever the default branch head is at release time. Every git command
    # runs through the injected authenticated runner, which presents the resolved Published Home
    # token over HTTPS, so both the clone and the push that extends the history use it.
    with tempfile.TemporaryDirectory() as checkout_parent:
        checkout = Path(checkout_parent) / "published-home"
        _require_success(
            run_git(["clone", https_clone_url(repository), str(checkout)]), repository, version
        )
        place_exposition_in_checkout(checkout, exposition)
        _require_success(run_git(["-C", str(checkout), "add", "-A"]), repository, version)
        # --allow-empty: a release whose source is byte-identical to the prior one still earns its
        # own commit, so the Release has a distinct commit to tag.
        _require_success(
            run_git(
                [
                    "-C",
                    str(checkout),
                    "-c",
                    f"user.name={_COMMIT_AUTHOR_NAME}",
                    "-c",
                    f"user.email={_COMMIT_AUTHOR_EMAIL}",
                    "commit",
                    "--allow-empty",
                    "-m",
                    exposition_commit_message(version),
                ]
            ),
            repository,
            version,
        )
        committed_sha = _require_success(
            run_git(["-C", str(checkout), "rev-parse", "HEAD"]), repository, version
        ).strip()
        _require_success(
            run_git(["-C", str(checkout), "push", "origin", "HEAD:main"]), repository, version
        )
        return committed_sha


def exposition_committer(run_git: Callable[[list[str]], GitOutcome]) -> CommitExposition:
    # Bind the authenticated git runner into a CommitExposition the composition root injects.
    def commit_exposition(*, repository: str, version: str, exposition: Path) -> str:
        return commit_exposition_with_git(
            repository=repository, version=version, exposition=exposition, run_git=run_git
        )

    return commit_exposition


def _require_success(outcome: GitOutcome, repository: str, version: str) -> str:
    if outcome.returncode != 0:
        raise ExpositionCommitFailed(
            repository, version, outcome.returncode, outcome.stderr.strip()
        )
    return outcome.stdout


class ExpositionCommitFailed(RuntimeError):
    def __init__(self, repository: str, version: str, returncode: int, detail: str = "") -> None:
        super().__init__(repository, version, returncode, detail)
        self.repository = repository
        self.version = version
        self.returncode = returncode
        self.detail = detail

    def __str__(self) -> str:
        base = (
            f"Committing the source exposition for {self.version!r} to {self.repository} "
            f"failed (exited {self.returncode}). A fresh Published Home must already carry a "
            "base commit on its default branch, and the host must be able to push to it."
        )
        return f"{base}\n{self.detail}" if self.detail else base
