"""The post-apply integrity check: verify the deployed Host Scaffold is spawnable-from.

A successful Install does not prove the host is usable: a Foundation can be stranded off
the host and the installed `vv` can be missing a Contributor command, both failing only
at the first later `vv spawn`/`vv <command>`. This check turns those into a loud Apply
failure instead. The command surface is Ringmaster's own and is checked here; Foundation
durability is delegated to vaudeville-bobiverse's `vv foundations-verify`.

Both probes are pure over an injected host ``vv`` runner (see ``host_vv``); the runner the
composition root supplies is the one that keeps the call off the rehearse shell's staged scratch.
"""

from __future__ import annotations

import json

from vaudeville_install.host_vv import RunVv

SURFACE_PROBE = "--surface"
FOUNDATIONS_VERIFY_SUBCOMMAND = "foundations-verify"


def verify_command_surface(run_vv: RunVv) -> None:
    # Gates priming: priming runs `vv prime`, so a missing or incomplete `vv` must be
    # caught here, before the priming step would trip on it.
    failures = _command_surface_failures(run_vv)
    if failures:
        raise HostScaffoldIntegrityError(failures)


def verify_foundations(run_vv: RunVv) -> None:
    failures = _foundations_failures(run_vv)
    if failures:
        raise HostScaffoldIntegrityError(failures)


def _command_surface_failures(run_vv: RunVv) -> list[str]:
    reported = run_vv([SURFACE_PROBE])
    if reported.returncode != 0:
        base = (
            "installed `vv` does not report its command surface (`vv --surface`); it is missing, "
            "not executable, or a stale/hand-maintained dispatcher rather than the "
            "Ringmaster-generated facade"
        )
        detail = reported.stderr.strip()
        return [f"{base}: {detail}" if detail else base]
    try:
        surface = json.loads(reported.stdout)
    except json.JSONDecodeError:
        return ["installed `vv --surface` did not return a JSON command list"]
    if not isinstance(surface, list) or not surface:
        return ["installed `vv` reports an empty command surface"]
    return []


def _foundations_failures(run_vv: RunVv) -> list[str]:
    verified = run_vv([FOUNDATIONS_VERIFY_SUBCOMMAND])
    if verified.returncode != 0:
        detail = verified.stderr.strip() or verified.stdout.strip()
        message = (
            "Foundations are not durable on the host "
            f"(`vv {FOUNDATIONS_VERIFY_SUBCOMMAND}` exited {verified.returncode})"
        )
        return [f"{message}: {detail}" if detail else message]
    return []


class HostScaffoldIntegrityError(RuntimeError):
    def __init__(self, failures: list[str]) -> None:
        super().__init__(failures)
        self.failures = failures

    def __str__(self) -> str:
        lines = "\n".join(f"  - {failure}" for failure in self.failures)
        return (
            "Apply installed the Host Scaffold, but it failed the post-apply integrity check:\n"
            f"{lines}\n"
            "The host is not deployable-from until these are resolved. Re-prime the Foundations "
            "(`vv prime`) and re-run the host install once the command surface is restored."
        )
