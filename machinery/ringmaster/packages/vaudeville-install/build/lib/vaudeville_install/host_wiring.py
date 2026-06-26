"""Post-apply host-wiring verification: confirm a fresh Host can actually spawn, not just that the
Artifact was placed.

A successful Install places the scaffold, but ``vv spawn``/``vv fork`` reach past it into the host
environment: they shell out to ``workmux`` to cut the worktree and tmux window, and they read the
tenant's YouTrack (the tracker every Assignment lives in) from ``credentials.toml``. On a fresh
Host either can be missing, and each surfaces only at the first spawn. This check turns those into a
loud Apply failure, exactly as the command-surface and Foundation probes do for Ringmaster's own
surface and the Foundations.

The bar is host-environment *wiring*, deliberately not Contributor semantics. YouTrack must be
*located* (its config present and the instance answering) and Workmux must be *present and
runnable*. Whether the YouTrack credential actually authenticates, or a real ``workmux add``
succeeds, are deeper questions owned elsewhere: the credential is the province of vaudeville-core's
YouTrack client, and exercising ``workmux add`` has side effects. Pulling either in would teach
Ringmaster a Contributor's internals and give Apply a flakier dependency; both stay out of this
probe, leaving a clean seam for a future ``vv``-side check to validate them.

Pure over injected capabilities, following the functional-core/imperative-shell split: the core
predicates take a reach/which/run callable; the composition root (the Apply CLI) supplies the real
urllib/shutil/subprocess. A test drives every wiring failure with plain fakes.
"""

from __future__ import annotations

import shutil
import subprocess
import tomllib
import urllib.error
import urllib.request
from collections.abc import Callable, Mapping
from pathlib import Path

from vaudeville_install.artifact import CREDENTIALS_FILENAME

# A reach probe answers "did the instance respond?": None when located and reachable, else a short
# reason. A binary-path probe answers "where on PATH is this binary?": its path, or None when the
# name is not on PATH. Run returns a process exit code. VerifyWiring is the capstone the Apply CLI
# binds and Apply calls.
Reach = Callable[[str], "str | None"]
BinaryPath = Callable[[str], "str | None"]
Run = Callable[[list[str]], int]
VerifyWiring = Callable[[], None]

WORKMUX_BINARY = "workmux"
# `--version` is the benign functional smoke: it proves the binary is present AND runs (right
# platform, libraries resolve) without the side effects a real `workmux add` would have.
WORKMUX_VERSION_PROBE = [WORKMUX_BINARY, "--version"]

YOUTRACK_API_BASE_ENV = "YOUTRACK_API_BASE"
YOUTRACK_API_KEY_ENV = "YOUTRACK_API_KEY"

_REACH_TIMEOUT_SECONDS = 10.0


def verify_host_wiring(
    *,
    api_base: str | None,
    api_key: str | None,
    reach: Reach,
    binary_path: BinaryPath,
    run: Run,
) -> None:
    failures = _youtrack_failures(api_base, api_key, reach) + _workmux_failures(binary_path, run)
    if failures:
        raise HostWiringError(failures)


def _youtrack_failures(api_base: str | None, api_key: str | None, reach: Reach) -> list[str]:
    # api_base/api_key arrive pre-resolved by the shell with the same env-over-file precedence
    # vaudeville-core's client uses, so this verifies the values `vv` will actually read. Reach is
    # probed only once a base is located; there is nothing to reach otherwise.
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
    unreachable = reach(api_base)
    if unreachable is not None:
        return [
            f"YouTrack is configured at {api_base} but is not reachable: {unreachable}. Confirm "
            "the URL and the host's network access to the instance."
        ]
    return []


def _workmux_failures(binary_path: BinaryPath, run: Run) -> list[str]:
    located = binary_path(WORKMUX_BINARY)
    if located is None:
        return [
            f"`{WORKMUX_BINARY}` is not on PATH. `vv spawn`/`vv fork` shell out to it to create "
            "the worktree and tmux window, and fail at the first spawn without it. Install Workmux "
            "(https://github.com/raine/workmux)."
        ]
    exit_code = run(WORKMUX_VERSION_PROBE)
    if exit_code != 0:
        return [
            f"`{WORKMUX_BINARY}` is on PATH at {located} but does not run "
            f"(`{' '.join(WORKMUX_VERSION_PROBE)}` exited {exit_code}); the binary may be built "
            "for the wrong platform or missing its libraries. Reinstall Workmux."
        ]
    return []


# --- imperative shell: the real capabilities the composition root injects ---


def locate_youtrack(
    env: Mapping[str, str], credentials_path: Path
) -> tuple[str | None, str | None]:
    """Find (api_base, api_key) the way vaudeville-core's client does: the YOUTRACK_* env vars win,
    then [youtrack] in credentials.toml fills whatever they leave unset."""
    table = _youtrack_table(credentials_path)
    api_base = env.get(YOUTRACK_API_BASE_ENV) or table.get("api_base")
    api_key = env.get(YOUTRACK_API_KEY_ENV) or table.get("api_key")
    return api_base, api_key


def _youtrack_table(credentials_path: Path) -> dict[str, str]:
    if not credentials_path.is_file():
        return {}
    with credentials_path.open("rb") as handle:
        declaration = tomllib.load(handle)
    table = declaration.get("youtrack", {})
    if not isinstance(table, dict):
        return {}
    # Keep only non-empty string values: an empty api_key is as good as unset to the resolver.
    return {key: value for key, value in table.items() if isinstance(value, str) and value}


def binary_path(name: str) -> str | None:
    return shutil.which(name)


def urllib_reach(url: str) -> str | None:
    """Reachability, not authentication: any HTTP response (even 401/404) proves the instance is
    located and answering, so only a connection-level failure (DNS, refused, timeout, TLS) counts
    as unreachable. Validating the credential behind a 401 is vaudeville-core's job, not this
    probe's."""
    request = urllib.request.Request(url, method="GET")
    try:
        urllib.request.urlopen(request, timeout=_REACH_TIMEOUT_SECONDS).close()
    except urllib.error.HTTPError:
        return None
    except (urllib.error.URLError, TimeoutError, OSError) as failure:
        return str(getattr(failure, "reason", failure) or failure)
    return None


def workmux_version_returncode(argv: list[str]) -> int:
    try:
        completed = subprocess.run(argv, capture_output=True, text=True, check=False)
    except OSError:
        # which() resolved the name but exec failed: a wrong-platform or broken binary. Report it
        # as an unrunnable command rather than letting OSError escape as a traceback.
        return 127
    return completed.returncode


class HostWiringError(RuntimeError):
    def __init__(self, failures: list[str]) -> None:
        super().__init__(failures)
        self.failures = failures

    def __str__(self) -> str:
        lines = "\n".join(f"  - {failure}" for failure in self.failures)
        return (
            "Apply placed the Host Scaffold, but the host is not wired for `vv spawn`/`vv fork`:\n"
            f"{lines}\n"
            "The host cannot spawn until these are resolved. Fix the wiring above and re-run "
            "the host install."
        )
