from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

AUTO_PERMISSION_MODE = ("--permission-mode", "auto")

# Priming is comprehension and earnest re-expression of the doctrine and spec,
# not frontier reasoning, so the priming turns run on a cheaper model and effort
# than the session default.
PRIMING_MODEL = ("--model", "sonnet", "--effort", "medium")

DOCTRINE_SUBTREE = "doctrine"
PROJECT_DOCS_SUBTREE = "project-docs"


def doctrine_turn(doctrine_dir: Path) -> str:
    return (
        f"Please read every document under {doctrine_dir}: the universal Vaudeville "
        "Doctrine every tenant primes against: its bearing, its code discipline, its "
        "practice, and the cross-context vocabulary. Then restate, in your own words, "
        "what this framework is for, what discipline it expects of you, and where "
        "your judgement is supposed to bite. This is the cross-context priming every "
        "Bob in every Component receives."
    )


def project_context_turn(project_docs_dir: Path) -> str:
    return (
        f"Now read every document under {project_docs_dir}: the project documentation "
        "this tenant shares across all of its repositories: the cross-cutting practices "
        "and conventions that hold for this project but not for every tenant. Then "
        "restate what this tells you about the project you are working within, above the "
        "level of any single repository."
    )


CONTRIBUTOR_TURN = (
    "Now read this Component's own spec and vocabulary: every document under "
    "docs/, and only those. Do not open src/ or tests/. Priming internalises the spec and "
    "the ubiquitous language, not the implementation; the code is what a Bob spawned here "
    "reads fresh when it works the repo, so reading it now only spends context without "
    "adding priming value. Then restate, from the docs alone, what you learned about this "
    "Context's responsibilities, its internal vocabulary, and how the spec says "
    "its pieces fit together. You are this Component's Foundation: future Bobs "
    "spawned in this repo will fork from your session and inherit this conversation as "
    "their priming."
)


def shared_priming_turns(data_files_root: Path) -> tuple[str, str]:
    return (
        doctrine_turn(data_files_root / DOCTRINE_SUBTREE),
        project_context_turn(data_files_root / PROJECT_DOCS_SUBTREE),
    )


def priming_argv(session_id: str, prompt: str, *, opening_turn: bool) -> list[str]:
    session_flag = "--session-id" if opening_turn else "--resume"
    return [
        "claude",
        "--print",
        *AUTO_PERMISSION_MODE,
        *PRIMING_MODEL,
        session_flag,
        session_id,
        prompt,
    ]


def fork_argv(bedrock_session_id: str, foundation_session_id: str, prompt: str) -> list[str]:
    # --fork-session branches into a new session id rather than continuing the Bedrock
    # in place, so the one Bedrock can be forked once per Component.
    return [
        "claude",
        "--print",
        *AUTO_PERMISSION_MODE,
        *PRIMING_MODEL,
        "--resume",
        bedrock_session_id,
        "--fork-session",
        "--session-id",
        foundation_session_id,
        prompt,
    ]


@dataclass(frozen=True)
class ClaudeInvocation:
    argv: list[str]
    cwd: Path
    log_path: Path | None = None
    # Priming never reads stdin: --print runs one non-interactive turn. Closing it
    # keeps a first-run trust or auth prompt from blocking on an inherited tty, the
    # same hang the sibling spawn path forecloses in WorkmuxInvocation.
    stdin: int = subprocess.DEVNULL


def bedrock_invocations(
    bedrock_session_id: str,
    *,
    data_files_root: Path,
    log_path: Path | None = None,
) -> list[ClaudeInvocation]:
    # The shared turns read only the host-fixed doctrine/ and project-docs/ subtrees,
    # so they need no Component checkout; the data dir is a stable place to run them in.
    # The first turn mints the session; the rest resume it.
    return [
        ClaudeInvocation(
            argv=priming_argv(bedrock_session_id, prompt, opening_turn=index == 0),
            cwd=data_files_root,
            log_path=log_path,
        )
        for index, prompt in enumerate(shared_priming_turns(data_files_root))
    ]
