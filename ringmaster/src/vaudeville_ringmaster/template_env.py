"""Renders a generated CLI module from a Jinja template bundled beside this package."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

_ENVIRONMENT = Environment(
    loader=FileSystemLoader(Path(__file__).parent / "templates"),
    trim_blocks=True,
    lstrip_blocks=True,
    keep_trailing_newline=True,
)


def render(template_name: str, **context: object) -> str:
    return _ENVIRONMENT.get_template(template_name).render(**context)
