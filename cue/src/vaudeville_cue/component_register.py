from __future__ import annotations

from vaudeville_core import component_from_prefix, list_components


def main() -> None:
    for prefix in list_components():
        component = component_from_prefix(prefix)
        print(f"- {prefix} ({component.name}): {component.description}")
