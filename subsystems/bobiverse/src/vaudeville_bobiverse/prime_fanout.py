from __future__ import annotations

import time
from collections.abc import Callable, Sequence
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from vaudeville_bobiverse.prime_source import UnreadableSource, unreadable_source_line

# Each Foundation fork drives its own `claude` session. Forking every Contributor
# at once saturates the model API and trips a server-side concurrency throttle, so
# cap the fan-out; a many-Contributor host still forks in parallel without
# self-throttling.
MAX_PRIME_CONCURRENCY = 3


class PrimeOutcomeKind(Enum):
    PRIMED = "primed"
    SOURCE_UNAVAILABLE = "source_unavailable"
    EXITED = "exited"
    ERRORED = "errored"


@dataclass(frozen=True)
class PrimeOutcome:
    prefix: str
    # None when the prime streamed to the terminal rather than a log file, as the
    # single-Component prime does; the fan-out always logs and always names one.
    log_path: Path | None
    kind: PrimeOutcomeKind
    session_id: str | None = None
    exit_code: int | str | None = None
    error: str | None = None

    @property
    def primed(self) -> bool:
        return self.kind is PrimeOutcomeKind.PRIMED


def prime_outcome_of(
    fork_result: Callable[[], str], prefix: str, log_path: Path | None
) -> PrimeOutcome:
    try:
        session_id = fork_result()
    except UnreadableSource:
        return PrimeOutcome(prefix, log_path, kind=PrimeOutcomeKind.SOURCE_UNAVAILABLE)
    except SystemExit as exited:
        return PrimeOutcome(prefix, log_path, kind=PrimeOutcomeKind.EXITED, exit_code=exited.code)
    except Exception as errored:
        return PrimeOutcome(prefix, log_path, kind=PrimeOutcomeKind.ERRORED, error=repr(errored))
    return PrimeOutcome(prefix, log_path, kind=PrimeOutcomeKind.PRIMED, session_id=session_id)


def priming_banner(prefixes: Sequence[str], *, max_concurrency: int) -> str:
    return (
        f"priming {len(prefixes)} Foundation(s), {max_concurrency} at a time: {', '.join(prefixes)}"
    )


def still_priming_line(pending: Sequence[str], *, elapsed_seconds: float) -> str:
    return f"still priming after {int(elapsed_seconds)}s: {', '.join(pending)}"


def fork_every_foundation(
    prefixes: list[str],
    fork_one: Callable[[str], str],
    log_path_for: Callable[[str], Path],
    *,
    max_concurrency: int,
    heartbeat: Callable[[str], None] = lambda _line: None,
    heartbeat_interval: float = 15.0,
) -> list[PrimeOutcome]:
    if not prefixes:
        return []
    outcomes: list[PrimeOutcome] = []
    started = time.monotonic()
    with ThreadPoolExecutor(max_workers=min(len(prefixes), max_concurrency)) as executor:
        futures = {executor.submit(fork_one, prefix): prefix for prefix in prefixes}
        pending = set(futures)
        # Bound each wait to a heartbeat interval, not to the next completion, so a fork
        # gone silent still yields a sign of life each idle slice instead of holding the
        # run quiet until it happens to return.
        while pending:
            done, pending = wait(pending, timeout=heartbeat_interval, return_when=FIRST_COMPLETED)
            if not done:
                heartbeat(
                    still_priming_line(
                        sorted(futures[future] for future in pending),
                        elapsed_seconds=time.monotonic() - started,
                    )
                )
                continue
            for future in done:
                prefix = futures[future]
                outcomes.append(prime_outcome_of(future.result, prefix, log_path_for(prefix)))
    return outcomes


def prime_from_shared_bedrock(
    prefixes: list[str],
    make_bedrock: Callable[[], str],
    fork_one: Callable[[str, str], str],
    log_path_for: Callable[[str], Path],
    *,
    max_concurrency: int,
    heartbeat: Callable[[str], None] = lambda _line: None,
    heartbeat_interval: float = 15.0,
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
        heartbeat=heartbeat,
        heartbeat_interval=heartbeat_interval,
    )


def errored_line(prefix: str, error: str | None, log_path: Path | None) -> str:
    return _with_log(f"{prefix} FAILED: unexpected error during priming: {error}", log_path)


def _with_log(line: str, log_path: Path | None) -> str:
    return line if log_path is None else f"{line}; log: {log_path}"


def prime_report(outcomes: Sequence[PrimeOutcome]) -> tuple[list[str], list[str], int]:
    stdout_lines: list[str] = []
    stderr_lines: list[str] = []
    for outcome in outcomes:
        if outcome.kind is PrimeOutcomeKind.PRIMED:
            primed = f"{outcome.prefix} primed → {outcome.session_id}"
            if outcome.log_path is not None:
                primed = f"{primed}  (log: {outcome.log_path})"
            stdout_lines.append(primed)
        elif outcome.kind is PrimeOutcomeKind.SOURCE_UNAVAILABLE:
            stderr_lines.append(unreadable_source_line(outcome.prefix, outcome.log_path))
        elif outcome.kind is PrimeOutcomeKind.EXITED:
            stderr_lines.append(
                _with_log(f"{outcome.prefix} FAILED (exit {outcome.exit_code})", outcome.log_path)
            )
        else:
            stderr_lines.append(errored_line(outcome.prefix, outcome.error, outcome.log_path))
    exit_code = 1 if any(not outcome.primed for outcome in outcomes) else 0
    return stdout_lines, stderr_lines, exit_code
