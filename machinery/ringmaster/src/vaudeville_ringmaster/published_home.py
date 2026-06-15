"""Authenticated access to the Published Home: resolve the elevated token, present it to gh and git.

The single shell boundary every Published Home interaction goes through. Publish writes to the
Published Home from three call sites — list tags and create release (via ``gh``) and the source
commit (via ``git``) — and each must authenticate with the same elevated, Published-Home-scoped
token, never the broad credential the host's automation otherwise carries. ``gh`` reads ``GH_TOKEN``
from its environment natively; raw ``git`` does not, so it is handed the token through an explicit
credential helper rather than left to whatever ambient ``git_protocol`` or installed helper the host
happens to have. Both runners are built here from one resolved token and injected by the composition
root, so authentication is presented in exactly one place and no call site re-derives it.

The token is resolved from an integrator-internal credentials file in the operator's config dir,
deliberately *not* the tenant's ``credentials.toml`` (which Install copies into the deployed data
dir for the runtime); the elevated token must live in a file the deploy path never copies.
"""

from __future__ import annotations

import os
import subprocess
import tomllib
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from vaudeville_ringmaster.github_release import GhOutcome

# The integrator-internal credentials file in the operator's config dir. Distinct from the tenant's
# `credentials.toml` (which Install copies into the deployed data dir); this one is never deployed,
# so the elevated token stays on the integrator side.
RINGMASTER_CREDENTIALS_FILENAME = "ringmaster-credentials.toml"

_CREDENTIALS_SECTION = "published-home"
_TOKEN_KEY = "token"

# The env var the git credential helper reads the token from. Held in the environment, never in
# argv, so it cannot surface in a process listing or the captured stderr of a failed git command.
_TOKEN_ENV = "VV_PUBLISHED_HOME_TOKEN"

RunGh = Callable[[list[str]], GhOutcome]
RunGit = Callable[[list[str]], "GitOutcome"]


@dataclass(frozen=True)
class GitOutcome:
    returncode: int
    stdout: str
    stderr: str


def published_home_token(credentials_path: Path) -> str:
    token = _token_in(credentials_path)
    if token is None:
        raise PublishedHomeTokenMissing(credentials_path)
    return token


def _token_in(credentials_path: Path) -> str | None:
    if not credentials_path.is_file():
        return None
    with credentials_path.open("rb") as handle:
        declaration = tomllib.load(handle)
    section = declaration.get(_CREDENTIALS_SECTION, {})
    if not isinstance(section, dict):
        return None
    token = section.get(_TOKEN_KEY)
    # An empty token is as good as unset.
    return token if isinstance(token, str) and token else None


def gh_runner(token: str) -> RunGh:
    # gh reads GH_TOKEN natively; overriding it in the subprocess environment presents the elevated
    # token in place of any ambient one.
    env = {**os.environ, "GH_TOKEN": token}

    def run_gh(argv: list[str]) -> GhOutcome:
        try:
            completed = subprocess.run(argv, capture_output=True, text=True, check=False, env=env)
        except OSError as launch_failure:
            return GhOutcome(127, "", f"could not launch `gh`: {launch_failure}")
        return GhOutcome(completed.returncode, completed.stdout, completed.stderr)

    return run_gh


def git_runner(token: str) -> RunGit:
    # Raw git does not read GH_TOKEN. Hand it the token through an explicit credential helper, with
    # the token in the environment, so a git push authenticates with the elevated token regardless
    # of the host's git_protocol or whether a global gh credential helper is configured.
    env = {**os.environ, _TOKEN_ENV: token}

    def run_git(argv: list[str]) -> GitOutcome:
        try:
            completed = subprocess.run(
                ["git", *git_credential_argv(), *argv],
                capture_output=True,
                text=True,
                check=False,
                env=env,
            )
        except OSError as launch_failure:
            return GitOutcome(127, "", f"could not launch `git`: {launch_failure}")
        return GitOutcome(completed.returncode, completed.stdout, completed.stderr)

    return run_git


def git_credential_argv() -> list[str]:
    # Reset any inherited credential helper first (an empty value clears the accumulated list, so a
    # host helper bound to another credential cannot answer), then install ours. Each entry is a
    # `git -c <name>=<value>` config assignment, so the helper rides as the value of
    # credential.helper. With an HTTPS remote this makes git authenticate with the resolved token
    # deterministically.
    return ["-c", "credential.helper=", "-c", "credential.helper=" + _credential_helper_command()]


def _credential_helper_command() -> str:
    # A `!`-prefixed value is run by git as a shell command; this one returns the resolved token as
    # the HTTPS basic-auth password. The token is read from the environment by name, never embedded
    # here, so it stays out of argv and out of any captured diagnostic. (No operation guard: git
    # ignores the output on store/erase, and a function called with no arguments cannot see git's
    # appended operation in `$1` anyway.)
    return '!f() { echo "username=x-access-token"; echo "password=$' + _TOKEN_ENV + '"; }; f'


class PublishedHomeTokenMissing(RuntimeError):
    def __init__(self, credentials_path: Path) -> None:
        super().__init__(credentials_path)
        self.credentials_path = credentials_path

    def __str__(self) -> str:
        return (
            "Publish needs the elevated, Published-Home-scoped token to write to the Published "
            "Home; the broad agent PR credential cannot. Set "
            f"[{_CREDENTIALS_SECTION}].{_TOKEN_KEY} in {self.credentials_path} and re-run "
            "`ringmaster publish`."
        )
