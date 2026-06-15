"""Fork a Foundation per Contributor — capped, failure-isolated — and report.

``fork_every_foundation`` maps the prefixes through an injected per-Contributor
fork under a concurrency cap, turning each result into a ``PrimeOutcome`` and
each Contributor's ``SystemExit`` into one failed outcome that does not sink the
others. The fork is handed in, so this piece never knows what work it
parallelizes — and its cap and isolation are asserted with a plain fake fork,
not by intercepting priming. ``prime_report`` splits the outcomes into the
stdout/stderr lines and the process exit code.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

# Each Foundation fork drives its own `claude` session. Fanning out one worker per
# Contributor saturated the model API and tripped a server-side concurrency throttle
# ("not your usage limit") when `ringmaster apply` forked every Foundation at once. Cap
# the fan-out so a many-Contributor host still forks in parallel without self-throttling.
MAX_PRIME_CONCURRENCY = 3


@dataclass(frozen=True)
class PrimeOutcome:
    prefix: str
    log_path: Path
    session_id: str | None = None
    exit_code: int | str | None = None

    @property
    def primed(self) -> bool:
        return self.session_id is not None


def fork_every_foundation(
    prefixes: list[str],
    fork_one: Callable[[str], str],
    log_path_for: Callable[[str], Path],
    *,
    max_concurrency: int,
) -> list[PrimeOutcome]:
    if not prefixes:
        return []
    outcomes: list[PrimeOutcome] = []
    with ThreadPoolExecutor(max_workers=min(len(prefixes), max_concurrency)) as executor:
        futures = {executor.submit(fork_one, prefix): prefix for prefix in prefixes}
        for future in as_completed(futures):
            prefix = futures[future]
            try:
                session_id = future.result()
            except SystemExit as exc:
                outcomes.append(PrimeOutcome(prefix, log_path_for(prefix), exit_code=exc.code))
            else:
                outcomes.append(PrimeOutcome(prefix, log_path_for(prefix), session_id=session_id))
    return outcomes


def prime_report(outcomes: Sequence[PrimeOutcome]) -> tuple[list[str], list[str], int]:
    stdout_lines: list[str] = []
    stderr_lines: list[str] = []
    for outcome in outcomes:
        if outcome.primed:
            stdout_lines.append(
                f"{outcome.prefix} primed → {outcome.session_id}  (log: {outcome.log_path})"
            )
        else:
            stderr_lines.append(
                f"{outcome.prefix} FAILED (exit {outcome.exit_code}); log: {outcome.log_path}"
            )
    exit_code = 1 if any(not outcome.primed for outcome in outcomes) else 0
    return stdout_lines, stderr_lines, exit_code
