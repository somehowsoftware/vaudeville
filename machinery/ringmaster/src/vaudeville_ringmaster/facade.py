"""Compose the carried command line: the `vv` Facade and the `vaudeville` operator CLI.

Both surfaces are composed the same way — each from a set of Contributor Typer apps, located
through the [tool.vaudeville] Manifest and unioned by one program-parameterized dispatcher. The
Facade reads each Contributor's `binary`; the operator CLI reads its `operator_binary`. A
Contributor that declares no operator app contributes nothing to `vaudeville`, exactly as one
with no Manifest contributes nothing to `vv`.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable

from vaudeville_ringmaster.apply_plan import ApplyPlan
from vaudeville_ringmaster.contribution import Contribution
from vaudeville_ringmaster.manifest import Manifest
from vaudeville_ringmaster.template_env import render


def facade_modules_of(plan: ApplyPlan) -> tuple[str, ...]:
    """The Contributor CLI app modules the `vv` Facade composes."""
    return _app_modules_named_by(plan, lambda manifest: manifest.binary)


def operator_modules_of(plan: ApplyPlan) -> tuple[str, ...]:
    """The Contributor operator app modules the `vaudeville` CLI composes."""
    return _app_modules_named_by(plan, lambda manifest: manifest.operator_binary)


def federation_distributions_of(plan: ApplyPlan) -> tuple[str, ...]:
    """The Contributor distributions the composed command line depends on."""
    return tuple(
        sorted({_distribution_of(c) for c in plan.contributions if c.manifest is not None})
    )


def render_dispatch_module(cli_modules: Iterable[str], *, program: str) -> str:
    return render("dispatch.py.j2", modules=tuple(cli_modules), program=program)


def _app_modules_named_by(
    plan: ApplyPlan, binary_of: Callable[[Manifest], str | None]
) -> tuple[str, ...]:
    modules: list[str] = []
    for contribution in plan.contributions:
        if contribution.manifest is None:
            continue
        binary = binary_of(contribution.manifest)
        if binary is None:
            continue
        modules.append(_app_module_of(contribution, binary))
    return tuple(modules)


def _app_module_of(contribution: Contribution, binary: str) -> str:
    for console_script in contribution.console_scripts:
        if console_script.name == binary:
            module, _, entry = console_script.target.partition(":")
            if not module or not entry:
                raise MalformedCommandSurface(
                    f"Contributor {contribution.name!r} entry point {console_script.target!r} "
                    "is not of the form 'module:function'"
                )
            return module
    raise MalformedCommandSurface(
        f"Contributor {contribution.name!r} declares binary {binary!r} in its Manifest but no "
        "[project.scripts] entry defines it"
    )


def _distribution_of(contribution: Contribution) -> str:
    if contribution.distribution is None:
        raise MalformedCommandSurface(
            f"Contributor {contribution.name!r} offers a Command Surface but is not a buildable "
            "distribution (no [build-system] and [project].name in its pyproject.toml)"
        )
    return contribution.distribution


class MalformedCommandSurface(ValueError):
    pass
