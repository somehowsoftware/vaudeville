from __future__ import annotations

import uuid
from collections.abc import Callable
from pathlib import Path

from vaudeville_core import current_reading_of_component

from vaudeville_bobiverse import foundation
from vaudeville_bobiverse.prime_fanout import (
    MAX_PRIME_CONCURRENCY,
    PrimeOutcome,
    prime_from_shared_bedrock,
)
from vaudeville_bobiverse.prime_invocations import (
    CONTRIBUTOR_TURN,
    ClaudeInvocation,
    bedrock_invocations,
    fork_argv,
)
from vaudeville_bobiverse.prime_runner import begin_log, run_claude
from vaudeville_bobiverse.prime_store import seed_bedrock, store_foundation_transcript

# Both the Bedrock and each concurrent fork stream to their own file here so the
# parallel prime-all run's logs never interleave.
PRIME_LOG_DIR = Path("/tmp")


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
) -> str:
    foundation_session_id = str(uuid.uuid4())
    begin_log(log_path)
    with current_reading_of_component(prefix) as reading:
        # Claude Code names a session's project dir from the realpath-resolved cwd, so
        # encode the resolved reading: where the host reaches its temp root through a
        # symlink (macOS routes $TMPDIR through /var -> /private/var, and the reading
        # clone is minted under $TMPDIR), the unresolved path encodes a slug the forked
        # session was never written under, and the resume finds no conversation.
        reading = reading.resolve()
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
    # Record the session only after its transcript is safely in the store, so a
    # registered Foundation is never one a later spawn cannot find.
    foundation.save(prefix, foundation_session_id, data_files_root=data_files_root)
    return foundation_session_id


def prime(prefix: str, *, data_files_root: Path, projects_root: Path) -> str:
    bedrock_session_id = prime_bedrock(data_files_root=data_files_root)
    return fork_foundation(
        bedrock_session_id,
        prefix,
        data_files_root=data_files_root,
        projects_root=projects_root,
    )


def prime_log_path(prefix: str) -> Path:
    return PRIME_LOG_DIR / f"prime-{prefix.lower()}.log"


def prime_all(
    prefixes: list[str],
    *,
    data_files_root: Path,
    projects_root: Path,
    log_path_for: Callable[[str], Path] = prime_log_path,
    max_concurrency: int = MAX_PRIME_CONCURRENCY,
) -> list[PrimeOutcome]:
    # `vv prime` (no prefix) and `vaudeville prime --all` are the same act, so the
    # wiring that binds the live roots into the Bedrock and fork effects lives here,
    # once; the bedrock-once-then-fan-out policy it feeds is pure and tested apart.
    return prime_from_shared_bedrock(
        prefixes,
        lambda: prime_bedrock(data_files_root=data_files_root, log_path=log_path_for("bedrock")),
        lambda bedrock_session_id, prefix: fork_foundation(
            bedrock_session_id,
            prefix,
            data_files_root=data_files_root,
            projects_root=projects_root,
            log_path=log_path_for(prefix),
        ),
        log_path_for,
        max_concurrency=max_concurrency,
    )


def main(prefix: str, data_files_root: Path, projects_root: Path) -> None:
    print(prime(prefix, data_files_root=data_files_root, projects_root=projects_root))
