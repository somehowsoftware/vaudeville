"""CLI handler for the ``tangent`` subcommand.

Files a provisional Premise from a fixed set of captured fields rather than
from composed prose: the calling agent fills a form, it does not author.
The handler composes the body deterministically via ``compose_body`` and
then files through the same create-plus-depend path ``vv file`` uses, with
the Route fixed to ``check-in`` — a tangent is a side-concern the operator
has not worked out, so its safe failure mode is an unneeded conversation.
The kernel ops are injected; the composition root binds the real ones, tests
bind fakes. The dep-id guard and the create-before-link ordering are the
reused file path's, not duplicated here.
"""

from __future__ import annotations

from collections.abc import Callable

from vaudeville_pm import file_cli
from vaudeville_pm.link_cli import DependEdge
from vaudeville_pm.premise_factory import CreatePremise
from vaudeville_pm.tangent import compose_body


def tangent(
    project: str,
    summary: str,
    prompt: str,
    context: str,
    deps: list[str],
    *,
    create_premise: CreatePremise,
    add_depend: DependEdge,
    default_project: Callable[[], str],
) -> None:
    file_cli.file(
        summary,
        compose_body(prompt, context),
        "check-in",
        deps,
        "Premise",
        "Submitted",
        project,
        create_premise=create_premise,
        add_depend=add_depend,
        default_project=default_project,
    )
