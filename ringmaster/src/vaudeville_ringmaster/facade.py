"""Compose the carried command line: the `vv` Facade and the `vaudeville` operator CLI.

Both surfaces are composed the same way: each from a set of Contributor Typer apps, located
through the [tool.vaudeville] CLI Declaration and unioned by one program-parameterized dispatcher.
The Facade reads each Contributor's `binary`; the operator CLI reads its `operator_binary`. A
Contributor that declares no operator app contributes nothing to `vaudeville`, exactly as one
with no CLI Declaration contributes nothing to `vv`.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable

from vaudeville_install.artifact import INSTALLER_DISTRIBUTION

from vaudeville_ringmaster.cli_declaration import CLIDeclaration
from vaudeville_ringmaster.contribution import Contribution
from vaudeville_ringmaster.manifest import Manifest
from vaudeville_ringmaster.template_env import render


def facade_modules_of(manifest: Manifest) -> tuple[str, ...]:
    """The Contributor CLI app modules the `vv` Facade composes."""
    return _app_modules_named_by(manifest, lambda cli_declaration: cli_declaration.binary)


def operator_modules_of(manifest: Manifest) -> tuple[str, ...]:
    """The Contributor operator app modules the `vaudeville` CLI composes."""
    return _app_modules_named_by(manifest, lambda cli_declaration: cli_declaration.operator_binary)


def federation_distributions_of(manifest: Manifest) -> tuple[str, ...]:
    """The carried distributions the Composed CLI depends on.

    A `vv` app ships in its Contributor's own carried distribution; an operator-only app rides in
    the carried installer instead, because the integrator that declares it is build-time tooling the
    Artifact never carries. Declaring the uncarried integrator here would make the Composed CLI
    resolve against a wheel Build never carried, breaking the tenant install.
    """
    distributions: set[str] = set()
    for contribution in manifest.contributions:
        declaration = contribution.cli_declaration
        if declaration is None:
            continue
        if declaration.binary is not None:
            distributions.add(_distribution_of(contribution))
        elif declaration.operator_binary is not None:
            distributions.add(INSTALLER_DISTRIBUTION)
    return tuple(sorted(distributions))


def render_dispatch_module(cli_modules: Iterable[str], *, program: str) -> str:
    return render("dispatch.py.j2", modules=tuple(cli_modules), program=program)


def _app_modules_named_by(
    manifest: Manifest, binary_of: Callable[[CLIDeclaration], str | None]
) -> tuple[str, ...]:
    modules: list[str] = []
    for contribution in manifest.contributions:
        if contribution.cli_declaration is None:
            continue
        binary = binary_of(contribution.cli_declaration)
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
        f"Contributor {contribution.name!r} declares binary {binary!r} in its CLI Declaration "
        "but no [project.scripts] entry defines it"
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
