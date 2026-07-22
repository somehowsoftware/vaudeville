from __future__ import annotations

from collections.abc import Iterable, Sequence

from vaudeville_core import component_from_prefix, list_components
from vaudeville_core.component import Component


def names_of(components: Iterable[Component]) -> list[str]:
    names: list[str] = []
    for component in components:
        names.append(component.name)
        if component.short_name is not None:
            names.append(component.short_name)
    return sorted(names)


def bare_bob_rejection(names: Sequence[str]) -> str:
    return f"Name a Component. Known names: {', '.join(names) or '(none)'}."


def registered_component_names() -> list[str]:
    return names_of(component_from_prefix(prefix) for prefix in list_components())
