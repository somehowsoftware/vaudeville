from __future__ import annotations

import os
import sys
import tempfile
import uuid
from collections.abc import Callable
from contextlib import AbstractContextManager
from pathlib import Path

from vaudeville_core import current_reading_of_component, list_components

from vaudeville_bobiverse import foundation
from vaudeville_bobiverse.prime_env import noninteractive_git_env
from vaudeville_bobiverse.prime_fanout import (
    MAX_PRIME_CONCURRENCY,
    PrimeOutcome,
    prime_from_shared_bedrock,
    prime_outcome_of,
    prime_report,
    priming_banner,
)
from vaudeville_bobiverse.prime_invocations import (
    CONTRIBUTOR_TURN,
    ClaudeInvocation,
    bedrock_invocations,
    fork_argv,
)
from vaudeville_bobiverse.prime_runner import begin_log, run_claude
from vaudeville_bobiverse.prime_source import readable_reading
from vaudeville_bobiverse.prime_store import (
    discard_reading_scratch,
    seed_bedrock,
    store_foundation_transcript,
)

# How often the fan-out breaks silence while forks are in flight. Frequent enough that
# a working run never looks hung, sparse enough not to bury the eventual report.
DEFAULT_HEARTBEAT_SECONDS = 15.0


def prime_heartbeat_interval() -> float:
    # A nonpositive interval makes the fan-out's wait(timeout=...) return
    # instantly, spinning the heartbeat into a stderr flood -- the illegible
    # churn the loop exists to expose. Fall back to the default over any value
    # that defeats it, malformed or nonpositive alike.
    try:
        seconds = float(os.environ.get("VV_PRIME_HEARTBEAT_SECONDS", DEFAULT_HEARTBEAT_SECONDS))
    except ValueError:
        return DEFAULT_HEARTBEAT_SECONDS
    return seconds if seconds > 0 else DEFAULT_HEARTBEAT_SECONDS


def announce(line: str) -> None:
    # Priming progress goes to stderr so stdout stays the machine-readable
    # primed-session report; flush so a heartbeat is never buffered behind a stalled
    # fork, which is exactly what it exists to reveal.
    print(line, file=sys.stderr, flush=True)


def prime_bedrock(*, data_files_root: Path, log_path: Path | None = None) -> str:
    bedrock_session_id = str(uuid.uuid4())
    begin_log(log_path)
    for invocation in bedrock_invocations(
        bedrock_session_id, data_files_root=data_files_root, log_path=log_path
    ):
        run_claude(invocation)
    return bedrock_session_id


def fork_foundation(
    bedrock_session_id: str,
    prefix: str,
    *,
    data_files_root: Path,
    projects_root: Path,
    log_path: Path | None = None,
    acquire: Callable[[str], AbstractContextManager[Path]] = current_reading_of_component,
    fork_body: Callable[[Path], str] | None = None,
) -> str:
    foundation_session_id = str(uuid.uuid4())
    begin_log(log_path)

    def prime_the_foundation(reading: Path) -> str:
        seed_bedrock(
            bedrock_session_id,
            reading=reading,
            projects_root=projects_root,
            data_files_root=data_files_root,
        )
        run_claude(
            ClaudeInvocation(
                argv=fork_argv(bedrock_session_id, foundation_session_id, CONTRIBUTOR_TURN),
                cwd=reading,
                log_path=log_path,
            )
        )
        store_foundation_transcript(
            foundation_session_id,
            primed_in=reading,
            projects_root=projects_root,
            data_files_root=data_files_root,
        )
        # Register the session only once its transcript is in the store, so a
        # recorded Foundation is never one a later spawn cannot find.
        foundation.save(prefix, foundation_session_id, data_files_root=data_files_root)
        return foundation_session_id

    fork = fork_body or prime_the_foundation
    with readable_reading(prefix, acquire=acquire) as reading:
        # Claude Code names a session's project dir from the realpath-resolved cwd, so
        # encode the resolved reading: where the host reaches its temp root through a
        # symlink (macOS routes $TMPDIR through /var -> /private/var, and the reading
        # clone is minted under $TMPDIR), the unresolved path encodes a slug the forked
        # session was never written under, and the resume finds no conversation.
        reading = reading.resolve()
        try:
            return fork(reading)
        finally:
            discard_reading_scratch(reading, projects_root=projects_root)


def prime(prefix: str, *, data_files_root: Path, projects_root: Path) -> PrimeOutcome:
    # Priming never blocks on a human: assert non-interactive git over every
    # child once, on the main thread, before any clone runs. Set-once at the
    # composition root, not per-fork, since mutating os.environ across the
    # fork-out threads would race.
    os.environ.update(noninteractive_git_env())
    bedrock_session_id = prime_bedrock(data_files_root=data_files_root)
    return prime_outcome_of(
        lambda: fork_foundation(
            bedrock_session_id,
            prefix,
            data_files_root=data_files_root,
            projects_root=projects_root,
        ),
        prefix,
        None,
    )


def prime_log_dir() -> Path:
    # A per-run scratch dir under $TMPDIR (honoured via gettempdir), keyed by pid so
    # two tenants priming at once never write into each other's logs. It persists
    # after the run because the report's failure lines point back at these files.
    return Path(tempfile.gettempdir()) / f"vv-prime-{os.getpid()}"


def prime_log_path(prefix: str) -> Path:
    return prime_log_dir() / f"prime-{prefix.lower()}.log"


def prime_all(
    prefixes: list[str],
    *,
    data_files_root: Path,
    projects_root: Path,
    log_path_for: Callable[[str], Path] = prime_log_path,
    max_concurrency: int = MAX_PRIME_CONCURRENCY,
    heartbeat: Callable[[str], None] = announce,
) -> list[PrimeOutcome]:
    # `vv prime` (no prefix) and `vaudeville prime --all` are the same act, so the
    # wiring that binds the live roots into the Bedrock and fork effects lives here,
    # once; the bedrock-once-then-fan-out policy it feeds is pure and tested apart.
    os.environ.update(noninteractive_git_env())
    if prefixes:
        heartbeat(priming_banner(prefixes, max_concurrency=max_concurrency))

    def prime_announced_bedrock() -> str:
        # The shared Bedrock runs first and streams to a log, so the terminal would
        # otherwise sit silent through it before any fork can tick. Bracket it with a
        # start and a done line, so no phase of the run is an unlabelled silence an
        # operator has to read as either working or hung.
        heartbeat("priming the shared Bedrock first (Doctrine, project-docs)")
        bedrock_session_id = prime_bedrock(
            data_files_root=data_files_root,
            log_path=log_path_for("bedrock"),
        )
        heartbeat("shared Bedrock primed; forking Foundations")
        return bedrock_session_id

    return prime_from_shared_bedrock(
        prefixes,
        prime_announced_bedrock,
        lambda bedrock_session_id, prefix: fork_foundation(
            bedrock_session_id,
            prefix,
            data_files_root=data_files_root,
            projects_root=projects_root,
            log_path=log_path_for(prefix),
        ),
        log_path_for,
        max_concurrency=max_concurrency,
        heartbeat=heartbeat,
        heartbeat_interval=prime_heartbeat_interval(),
    )


def print_prime_report(outcomes: list[PrimeOutcome]) -> None:
    stdout_lines, stderr_lines, exit_code = prime_report(outcomes)
    for line in stdout_lines:
        print(line)
    for line in stderr_lines:
        print(line, file=sys.stderr)
    if exit_code != 0:
        sys.exit(exit_code)


def main(prefix: str, data_files_root: Path, projects_root: Path) -> None:
    print_prime_report(
        [prime(prefix, data_files_root=data_files_root, projects_root=projects_root)]
    )


def main_all(prefixes: list[str], data_files_root: Path, projects_root: Path) -> None:
    print_prime_report(
        prime_all(prefixes, data_files_root=data_files_root, projects_root=projects_root)
    )


def prime_one_or_all(
    prefix: str | None,
    *,
    data_files_root: Path,
    projects_root: Path,
    registered: Callable[[], list[str]] = list_components,
    prime_one: Callable[[str, Path, Path], None] = main,
    prime_every: Callable[[list[str], Path, Path], None] = main_all,
) -> None:
    # `vv prime BOB` and `vaudeville prime bobiverse` name one Component; a bare
    # `vv prime` and `vaudeville prime --all` name every registered one. An empty
    # register primes nothing, said out loud here rather than fanned out over zero
    # Components. Both surfaces resolve their syntax to a prefix-or-None and share this
    # one dispatch, so neither carries the one-vs-all rule itself.
    if prefix is not None:
        prime_one(prefix, data_files_root, projects_root)
        return
    prefixes = registered()
    if not prefixes:
        print("No Components in ~/.vaudeville/projects.toml; nothing to prime.")
        return
    prime_every(prefixes, data_files_root, projects_root)
