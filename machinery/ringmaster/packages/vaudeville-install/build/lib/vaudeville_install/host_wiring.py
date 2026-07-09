"""The Host-wiring Check: confirm a fresh Host can reach what its next steps need, not just that
the Artifact was placed. Pure over injected authenticate/read-remote/binary-path/workmux-runs
capabilities; the composition root wires each over the ``child_process`` boundary.
"""

from __future__ import annotations

import re
import shutil
import tomllib
import urllib.error
import urllib.request
from collections.abc import Callable, Mapping
from pathlib import Path

from vaudeville_install.artifact import CREDENTIALS_FILENAME
from vaudeville_install.child_process import Completed, LaunchFailed, Outcome, Spec, TimedOut
from vaudeville_install.tenant_config import TenantConfigUnreadable

# Each probe returns None on success, else a short operator-facing reason; a binary-path probe
# returns the located path, or None when the name is not on PATH.
Authenticate = Callable[[str, str], "str | None"]
ReadRemote = Callable[[str], "str | None"]
BinaryPath = Callable[[str], "str | None"]
WorkmuxRuns = Callable[[], "str | None"]
VerifyWiring = Callable[[], None]

WORKMUX_BINARY = "workmux"
# `--version` is the benign functional smoke: it proves the binary is present AND runs (right
# platform, libraries resolve) without the side effects a real `workmux add` would have.
WORKMUX_VERSION_PROBE = (WORKMUX_BINARY, "--version")

YOUTRACK_API_BASE_ENV = "YOUTRACK_API_BASE"
YOUTRACK_API_KEY_ENV = "YOUTRACK_API_KEY"
# The least-privilege authenticated endpoint: every token can read its own user, so a 2xx proves
# the token authenticates and any other response (a 401/403 rejection, a wrong-URL 404) does not.
YOUTRACK_ME_PATH = "/users/me?fields=login"

_AUTHENTICATE_TIMEOUT_SECONDS = 10.0

# `scheme://userinfo@` — the credential a remote URL (or a git error echoing one) can carry. Strip
# the userinfo so no token reaches an operator-facing diagnostic. An ssh `git@host:path` remote has
# no `://` and is left untouched: its `git@` is a username, not a secret.
_CREDENTIAL_IN_URL = re.compile(r"(\w[\w+.-]*://)[^/@\s]+@")


def verify_host_wiring(
    *,
    api_base: str | None,
    api_key: str | None,
    remotes: list[str],
    authenticate: Authenticate,
    read_remote: ReadRemote,
    binary_path: BinaryPath,
    workmux_runs: WorkmuxRuns,
) -> None:
    failures = (
        _youtrack_failures(api_base, api_key, authenticate)
        + _component_remote_failures(remotes, read_remote)
        + _workmux_failures(binary_path, workmux_runs)
    )
    if failures:
        raise HostWiringError(failures)


def _youtrack_failures(
    api_base: str | None, api_key: str | None, authenticate: Authenticate
) -> list[str]:
    # api_base/api_key arrive pre-resolved by the shell with the same env-over-file precedence
    # vaudeville-core's client uses, so this authenticates the values `vv` will actually read.
    # Authentication is attempted only once both are located; there is nothing to authenticate
    # otherwise.
    if not api_base:
        return [
            "YouTrack is not located: neither the YOUTRACK_API_BASE environment variable nor "
            f"[youtrack].api_base in the host's {CREDENTIALS_FILENAME} is set. `vv` reads the "
            "tenant's tracker from there, so spawn and the lifecycle commands fail without it."
        ]
    if not api_key:
        return [
            f"YouTrack api_base is set to {api_base} but no api_key is: neither YOUTRACK_API_KEY "
            f"nor [youtrack].api_key in {CREDENTIALS_FILENAME}. `vv` cannot authenticate to the "
            "tracker."
        ]
    rejected = authenticate(api_base, api_key)
    if rejected is not None:
        return [
            f"YouTrack is configured at {api_base} but the host cannot authenticate to it: "
            f"{rejected}. Confirm the api_key is a valid token for this instance and the host can "
            "reach it."
        ]
    return []


def _component_remote_failures(remotes: list[str], read_remote: ReadRemote) -> list[str]:
    # Every remote that git cannot read, not just the first: a host missing access to several
    # remotes should hear about all of them in one install, not one re-run per remote. The remote
    # is rendered credential-stripped: the Project Map may carry a token in the URL, and a failure
    # the operator reads must not leak it.
    failures = []
    for remote in remotes:
        unreadable = read_remote(remote)
        if unreadable is not None:
            failures.append(
                f"the Component remote {without_credentials(remote)} is not readable: "
                f"{unreadable}. Priming clones each Component's remote; wire the host's git "
                "credentials for the tenant's own Component remotes (a fresh host reaches its own "
                "private repos, never Vaudeville's) so a read-only `git ls-remote` succeeds."
            )
    return failures


def _workmux_failures(binary_path: BinaryPath, workmux_runs: WorkmuxRuns) -> list[str]:
    located = binary_path(WORKMUX_BINARY)
    if located is None:
        return [
            f"`{WORKMUX_BINARY}` is not on PATH. `vv spawn`/`vv fork` shell out to it to create "
            "the worktree and tmux window, and fail at the first spawn without it. Install Workmux "
            "(https://github.com/raine/workmux)."
        ]
    unrunnable = workmux_runs()
    if unrunnable is not None:
        return [
            f"`{WORKMUX_BINARY}` is on PATH at {located} but does not run ({unrunnable}); the "
            "binary may be built for the wrong platform or missing its libraries. Reinstall "
            "Workmux."
        ]
    return []


def build_ls_remote_spec(remote: str, env: Mapping[str, str], timeout: float) -> Spec:
    # Readability, the read-only twin of Priming's clone: `git ls-remote` takes the same transport
    # and `credential.helper` path a clone would, so a host that cannot read the remote here cannot
    # clone it there. The child-process boundary forces GIT_TERMINAL_PROMPT=0 and closes stdin, so a
    # missing credential fails fast rather than hanging on a prompt no headless host can answer.
    return Spec(argv=("git", "ls-remote", remote), env=env, timeout=timeout)


def interpret_ls_remote(outcome: Outcome) -> str | None:
    match outcome:
        case Completed(returncode=0):
            return None
        case Completed(returncode=returncode, stderr=stderr):
            return without_credentials(stderr.strip()) or f"`git ls-remote` exited {returncode}"
        case TimedOut(timeout=timeout):
            return f"`git ls-remote` did not answer within {timeout:g}s"
        case LaunchFailed(reason=reason):
            return without_credentials(reason)


def build_workmux_spec(env: Mapping[str, str], timeout: float) -> Spec:
    return Spec(argv=WORKMUX_VERSION_PROBE, env=env, timeout=timeout)


def interpret_workmux(outcome: Outcome) -> str | None:
    probe = " ".join(WORKMUX_VERSION_PROBE)
    match outcome:
        case Completed(returncode=0):
            return None
        case Completed(returncode=returncode, stderr=stderr):
            detail = stderr.strip()
            base = f"`{probe}` exited {returncode}"
            return f"{base}: {detail}" if detail else base
        case TimedOut(timeout=timeout):
            return f"`{probe}` did not answer within {timeout:g}s"
        case LaunchFailed(reason=reason):
            return reason


def without_credentials(text: str) -> str:
    return _CREDENTIAL_IN_URL.sub(r"\1", text)


def locate_youtrack(
    env: Mapping[str, str], credentials_path: Path
) -> tuple[str | None, str | None]:
    # The YOUTRACK_* env vars win, then [youtrack] in credentials.toml fills what they leave unset,
    # the precedence vaudeville-core's own client resolves by.
    table = _youtrack_table(credentials_path)
    api_base = env.get(YOUTRACK_API_BASE_ENV) or table.get("api_base")
    api_key = env.get(YOUTRACK_API_KEY_ENV) or table.get("api_key")
    return api_base, api_key


def _youtrack_table(credentials_path: Path) -> dict[str, str]:
    if not credentials_path.is_file():
        return {}
    try:
        with credentials_path.open("rb") as handle:
            declaration = tomllib.load(handle)
    except tomllib.TOMLDecodeError as malformed:
        raise TenantConfigUnreadable(credentials_path, malformed) from malformed
    table = declaration.get("youtrack", {})
    if not isinstance(table, dict):
        return {}
    # Keep only non-empty string values: an empty api_key is as good as unset to the resolver.
    return {key: value for key, value in table.items() if isinstance(value, str) and value}


def binary_path(name: str) -> str | None:
    return shutil.which(name)


def youtrack_authenticated(api_base: str, api_key: str) -> str | None:
    # A rejected token and an unreachable tracker are reported distinctly, so the operator can tell
    # "wrong token" from "cannot reach".
    request = urllib.request.Request(
        f"{api_base.rstrip('/')}{YOUTRACK_ME_PATH}",
        method="GET",
        headers={"Authorization": f"Bearer {api_key}", "Accept": "application/json"},
    )
    try:
        urllib.request.urlopen(request, timeout=_AUTHENTICATE_TIMEOUT_SECONDS).close()
    except urllib.error.HTTPError as rejected:
        return f"the tracker rejected the request (HTTP {rejected.code})"
    except (urllib.error.URLError, TimeoutError, OSError) as unreachable:
        reason = getattr(unreachable, "reason", unreachable) or unreachable
        return f"could not reach the tracker: {reason}"
    return None


class HostWiringError(RuntimeError):
    def __init__(self, failures: list[str]) -> None:
        super().__init__(failures)
        self.failures = failures

    def __str__(self) -> str:
        lines = "\n".join(f"  - {failure}" for failure in self.failures)
        return (
            "The install placed the Host Installation, but the host is not wired for what Priming "
            "and `vv spawn`/`vv fork` need next:\n"
            f"{lines}\n"
            "The host cannot be primed or spawned from until these are resolved. Fix the wiring "
            "above and re-run the host install."
        )
