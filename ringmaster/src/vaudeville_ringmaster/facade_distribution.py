"""Composes the carried CLI distribution: the `vv` Facade and the `vaudeville` operator CLI.

Both are dispatchers rendered from one template, differing only in the program name they carry and
the Contributor app modules they compose. The distribution declares one entry point per surface,
each pointing at its own dispatcher module.
"""

from __future__ import annotations

from pathlib import Path

from vaudeville_install.artifact import FACADE_DISTRIBUTION

from vaudeville_ringmaster.facade import render_dispatch_module

FACADE_PACKAGE = "vaudeville_vv"

_FACADE_COMMAND = "vv"
_OPERATOR_COMMAND = "vaudeville"
_FACADE_DISPATCH_MODULE = "dispatch"
_OPERATOR_DISPATCH_MODULE = "operator_dispatch"


def render_facade_distribution(
    destination: Path,
    *,
    facade_modules: tuple[str, ...],
    operator_modules: tuple[str, ...],
    distributions: tuple[str, ...],
    version: str,
) -> None:
    package_dir = destination / "src" / FACADE_PACKAGE
    package_dir.mkdir(parents=True, exist_ok=True)
    (destination / "pyproject.toml").write_text(_pyproject(distributions, version))
    (package_dir / "__init__.py").write_text("")
    (package_dir / f"{_FACADE_DISPATCH_MODULE}.py").write_text(
        render_dispatch_module(facade_modules, program=_FACADE_COMMAND)
    )
    (package_dir / f"{_OPERATOR_DISPATCH_MODULE}.py").write_text(
        render_dispatch_module(operator_modules, program=_OPERATOR_COMMAND)
    )


def _pyproject(contributor_distributions: tuple[str, ...], version: str) -> str:
    dependencies = (*sorted(contributor_distributions), "typer", "click")
    rendered = "".join(f'    "{dependency}",\n' for dependency in dependencies)
    return (
        "[build-system]\n"
        'requires = ["setuptools>=68.0"]\n'
        'build-backend = "setuptools.build_meta"\n'
        "\n"
        "[project]\n"
        f'name = "{FACADE_DISTRIBUTION}"\n'
        f'version = "{version}"\n'
        "dependencies = [\n"
        f"{rendered}"
        "]\n"
        "\n"
        "[project.scripts]\n"
        f'{_FACADE_COMMAND} = "{FACADE_PACKAGE}.{_FACADE_DISPATCH_MODULE}:main"\n'
        f'{_OPERATOR_COMMAND} = "{FACADE_PACKAGE}.{_OPERATOR_DISPATCH_MODULE}:main"\n'
        "\n"
        "[tool.setuptools.packages.find]\n"
        'where = ["src"]\n'
    )
