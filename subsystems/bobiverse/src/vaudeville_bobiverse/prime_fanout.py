from __future__ import annotations

from collections.abc import Callable, Sequence
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

# Each Foundation fork drives its own `claude` session. Forking every Contributor
# at once saturates the model API and trips a server-side concurrency throttle, so
# cap the fan-out; a many-Contributor host still forks in parallel without
# self-throttling.
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


def prime_from_shared_bedrock(
    prefixes: list[str],
    make_bedrock: Callable[[], str],
    fork_one: Callable[[str, str], str],
    log_path_for: Callable[[str], Path],
    *,
    max_concurrency: int,
) -> list[PrimeOutcome]:
    # One shared Bedrock feeds every fork, so it is stood up once and only when at
    # least one Foundation will fork from it: an empty Component set forks nothing and
    # so drives no Bedrock turns, rather than standing up a Bedrock nothing consumes.
    if not prefixes:
        return []
    bedrock_session_id = make_bedrock()
    return fork_every_foundation(
        prefixes,
        lambda prefix: fork_one(bedrock_session_id, prefix),
        log_path_for,
        max_concurrency=max_concurrency,
    )


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
