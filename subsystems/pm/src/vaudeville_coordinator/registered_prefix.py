from __future__ import annotations

from collections.abc import Mapping


# The anti-corruption boundary: a classifier's answer is untrusted foreign text, so
# only one that already names a registered Component may pass. A prefix the model
# invented is then structurally unable to reach an Assignment create.
def registered_prefix(answer: str, descriptions: Mapping[str, str]) -> str | None:
    candidate = answer.strip()
    return candidate if candidate in descriptions else None
