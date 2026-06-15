"""The priming composition roots: drive a Bedrock, fork a Foundation from it.

These own the lifecycles priming runs inside — the minted session ids and the
Current reading that ``fork_foundation`` opens and tears down — so they are
composition roots, left untested by design. Every decision they sequence is a
piece tested on its own: the invocations (``prime_invocations``), the runner
(``prime_runner``), and the transcript moves (``prime_store``). The store-before-
record invariant is structural here: ``store_foundation_transcript`` is the last
statement inside the reading, ``foundation.save`` the first after it closes.
"""

from __future__ import annotations

import uuid
from pathlib import Path

from vaudeville_core import current_reading_of_project

from vaudeville_bobiverse import foundation
from vaudeville_bobiverse.prime_invocations import (
    CONTRIBUTOR_TURN,
    ClaudeInvocation,
    bedrock_invocations,
    fork_argv,
)
from vaudeville_bobiverse.prime_runner import begin_log, run_claude
from vaudeville_bobiverse.prime_store import seed_bedrock, store_foundation_transcript


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
    with current_reading_of_project(prefix) as reading:
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


def main(prefix: str, data_files_root: Path, projects_root: Path) -> None:
    print(prime(prefix, data_files_root=data_files_root, projects_root=projects_root))
