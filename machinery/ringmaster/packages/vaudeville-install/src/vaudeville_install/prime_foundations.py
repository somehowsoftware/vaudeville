"""Prime the Contributor Foundations on the Host: Apply's closing step.

Spawn and Fork reseed a new Bob from its Contributor's primed Foundation session. Those sessions
are durable only when priming ran against the Host's own Claude state — not the Staging stand-in
the smoke uses, whose transcripts live in the staged scratch and vanish from the Host's view. Apply
runs this after the Host Scaffold is placed, against the just-installed unified ``vv`` so the
Foundations the host records resolve for the next ``vv spawn`` / ``vv fork`` without a manual
re-prime.

Priming itself is BOB's ``vv prime`` — it enumerates the projects to prime and drives the priming
turns. Apply reaches it through the injected host ``vv`` runner (see ``host_vv``), the same
subprocess-over-``vv`` seam every cross-Contributor call uses; that runner is built from a
host-targeted environment, so priming cannot land on the rehearse shell's staged scratch.
"""

from __future__ import annotations

from vaudeville_install.host_vv import RunVv

PRIME_SUBCOMMAND = "prime"


def prime_foundations(run_vv: RunVv) -> None:
    # `vv prime` with no prefix lets BOB prime every project in its projects.toml. Pure over the
    # injected runner, which carries the host `vv` path and a host-targeted environment.
    result = run_vv([PRIME_SUBCOMMAND])
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise FoundationsNotPrimed(result.returncode, detail)


class FoundationsNotPrimed(RuntimeError):
    def __init__(self, returncode: int, detail: str = "") -> None:
        super().__init__(returncode, detail)
        self.returncode = returncode
        self.detail = detail

    def __str__(self) -> str:
        base = (
            f"Priming the Contributor Foundations failed (`vv prime` exited {self.returncode}): "
            "the Host Scaffold is installed but spawn/fork will fail until the Foundations exist. "
            "Resolve the cause and re-run `ringmaster apply` or `vv prime`."
        )
        return f"{base}\n{self.detail}" if self.detail else base
