"""Commissioning: verify the deployed Host Installation is spawnable-from.

A successful Install does not prove the host is usable: a Foundation can be stranded off
the host and the installed `vv` can be missing a Contributor command, both failing only
at the first later `vv spawn`/`vv <command>`. Commissioning turns those into a loud install
failure instead. The command surface is Ringmaster's own and is checked here as the Surface
Check; Foundation durability is delegated to vaudeville-bobiverse's `vv foundations-verify`.

Both probes are pure over an injected host ``vv`` runner (see ``host_vv``); the runner the
composition root supplies keeps the call off the rehearse shell's Rehearsal Installation scratch.
"""

from __future__ import annotations

import json

from vaudeville_install.child_process import Completed, LaunchFailed, TimedOut
from vaudeville_install.host_vv import RunVv

SURFACE_PROBE = "--surface"
FOUNDATIONS_VERIFY_SUBCOMMAND = "foundations-verify"

_NO_SURFACE = (
    "installed `vv` does not report its command surface (`vv --surface`); it is missing, "
    "not executable, or a stale/hand-maintained dispatcher rather than the Ringmaster-generated "
    "Composed CLI"
)


def verify_command_surface(run_vv: RunVv) -> None:
    # Gates priming: priming runs `vv prime`, so a missing or incomplete `vv` must be
    # caught here, before the priming step would trip on it.
    failures = _command_surface_failures(run_vv)
    if failures:
        raise CommissioningError(failures)


def verify_foundations(run_vv: RunVv) -> None:
    failures = _foundations_failures(run_vv)
    if failures:
        raise CommissioningError(failures)


def _command_surface_failures(run_vv: RunVv) -> list[str]:
    match run_vv([SURFACE_PROBE]):
        case Completed(returncode=0, stdout=stdout):
            return _surface_shape_failures(stdout)
        case Completed(stderr=stderr):
            detail = stderr.strip()
            return [f"{_NO_SURFACE}: {detail}" if detail else _NO_SURFACE]
        case TimedOut(timeout=timeout):
            return [f"installed `vv {SURFACE_PROBE}` did not answer within {timeout:g}s"]
        case LaunchFailed(reason=reason):
            return [f"{_NO_SURFACE}: {reason}"]


def _surface_shape_failures(stdout: str) -> list[str]:
    try:
        surface = json.loads(stdout)
    except json.JSONDecodeError:
        return ["installed `vv --surface` did not return a JSON command list"]
    if not isinstance(surface, list) or not surface:
        return ["installed `vv` reports an empty command surface"]
    return []


def _foundations_failures(run_vv: RunVv) -> list[str]:
    match run_vv([FOUNDATIONS_VERIFY_SUBCOMMAND]):
        case Completed(returncode=0):
            return []
        case Completed(returncode=returncode, stdout=stdout, stderr=stderr):
            detail = stderr.strip() or stdout.strip()
            message = (
                "Foundations are not durable on the host "
                f"(`vv {FOUNDATIONS_VERIFY_SUBCOMMAND}` exited {returncode})"
            )
            return [f"{message}: {detail}" if detail else message]
        case TimedOut(timeout=timeout):
            return [f"`vv {FOUNDATIONS_VERIFY_SUBCOMMAND}` did not answer within {timeout:g}s"]
        case LaunchFailed(reason=reason):
            return [f"`vv {FOUNDATIONS_VERIFY_SUBCOMMAND}` could not run: {reason}"]


class CommissioningError(RuntimeError):
    def __init__(self, failures: list[str]) -> None:
        super().__init__(failures)
        self.failures = failures

    def __str__(self) -> str:
        lines = "\n".join(f"  - {failure}" for failure in self.failures)
        return (
            "The install placed the Host Installation, but it failed Commissioning:\n"
            f"{lines}\n"
            "The host is not deployable-from until these are resolved. Re-prime the Foundations "
            "(`vv prime`) and re-run the host install once the command surface is restored."
        )
