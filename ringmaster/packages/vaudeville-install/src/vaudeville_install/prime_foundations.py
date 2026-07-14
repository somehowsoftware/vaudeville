"""Prime the Contributor Foundations on the Host: Priming, the host install's closing step.

Spawn and Fork reseed a new Bob from its Contributor's primed Foundation session. Those sessions
are durable only when priming ran against the Host's own Claude state, not the Rehearsal stand-in
the smoke uses, whose transcripts live in the rehearsal scratch and vanish from the Host's view. The
install runs this after the Host Installation is placed, against the just-installed unified ``vv``
so the Foundations the host records resolve for the next ``vv spawn`` / ``vv fork`` without a manual
re-prime.

Priming itself is BOB's ``vv prime``; it enumerates the Components to prime and drives the priming
turns. The install reaches it through the injected host ``vv`` runner (see ``host_vv``), built from
a host-targeted environment so priming cannot run against the rehearse shell's rehearsal scratch.
"""

from __future__ import annotations

from vaudeville_install.child_process import Completed, LaunchFailed, Outcome, TimedOut
from vaudeville_install.destination import Layout
from vaudeville_install.host_vv import RunVv
from vaudeville_install.priming_watermark import record_priming_watermark

PRIME_SUBCOMMAND = "prime"


def prime_foundations(run_vv: RunVv, layout: Layout) -> None:
    outcome = run_vv([PRIME_SUBCOMMAND])
    if isinstance(outcome, Completed) and outcome.returncode == 0:
        # Record the Priming Watermark only on success: a failed prime leaves the prior one stale so
        # the next Refresh re-derives the reprime and repairs — see priming_watermark.
        record_priming_watermark(layout)
        return
    raise FoundationsNotPrimed(_why_priming_failed(outcome))


def _why_priming_failed(outcome: Outcome) -> str:
    match outcome:
        case Completed(returncode=returncode, stdout=stdout, stderr=stderr):
            detail = stderr.strip() or stdout.strip()
            base = f"`vv {PRIME_SUBCOMMAND}` exited {returncode}"
            return f"{base}: {detail}" if detail else base
        case TimedOut(timeout=timeout):
            return f"`vv {PRIME_SUBCOMMAND}` did not finish within {timeout:g}s and was terminated"
        case LaunchFailed(reason=reason):
            return reason


class FoundationsNotPrimed(RuntimeError):
    def __init__(self, cause: str) -> None:
        super().__init__(cause)
        self.cause = cause

    def __str__(self) -> str:
        return (
            "Priming the Contributor Foundations failed: the Host Installation is placed but "
            "spawn/fork will fail until the Foundations exist. Resolve the cause and re-run "
            f"`vv prime`, or re-run the host install.\n{self.cause}"
        )
