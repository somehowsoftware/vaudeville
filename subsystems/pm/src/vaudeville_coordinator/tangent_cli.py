from __future__ import annotations

import sys
from collections.abc import Callable, Mapping
from typing import NoReturn

from vaudeville_coordinator import file_cli
from vaudeville_coordinator.assignment_factory import CreateAssignment
from vaudeville_coordinator.concern_classifier import ClassifyConcern
from vaudeville_coordinator.link_cli import DependEdge
from vaudeville_coordinator.registered_prefix import registered_prefix
from vaudeville_coordinator.tangent import compose_body


def tangent(
    component: str | None,
    summary: str,
    prompt: str,
    context: str,
    deps: list[str],
    *,
    classify_concern: ClassifyConcern,
    repo_descriptions: Callable[[], Mapping[str, str]],
    create_assignment: CreateAssignment,
    add_depend: DependEdge,
) -> None:
    prefix = component or _classified_prefix(
        summary, prompt, context, classify_concern, repo_descriptions
    )
    file_cli.file(
        summary,
        compose_body(prompt, context),
        # check-in, not direct: a tangent is unworked-out, so its safe failure
        # mode is a conversation that may turn out not to have been needed.
        "check-in",
        deps,
        "Premise",
        "Submitted",
        prefix,
        create_assignment=create_assignment,
        add_depend=add_depend,
        default_component=_cwd_never_consulted,
    )


def _classified_prefix(
    summary: str,
    prompt: str,
    context: str,
    classify_concern: ClassifyConcern,
    repo_descriptions: Callable[[], Mapping[str, str]],
) -> str:
    descriptions = repo_descriptions()
    answer = classify_concern(_concern(summary, prompt, context), descriptions)
    prefix = registered_prefix(answer, descriptions)
    if prefix is None:
        _abort_unregistered(answer)
    return prefix


def _concern(summary: str, prompt: str, context: str) -> str:
    return f"{summary}\n\n{prompt}\n\n{context}"


def _abort_unregistered(answer: str) -> NoReturn:
    print(
        f"Error: the concern classifier returned {answer!r}, which names no "
        "registered Component. Re-run with --project <PREFIX> to file it explicitly.",
        file=sys.stderr,
    )
    sys.exit(1)


def _cwd_never_consulted() -> NoReturn:
    raise AssertionError(
        "tangent classifies or overrides its Component before filing; the cwd "
        "default must never be consulted."
    )
