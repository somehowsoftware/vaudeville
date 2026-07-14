from __future__ import annotations

from collections.abc import Mapping
from typing import NamedTuple


class Request(NamedTuple):
    method: str
    path: str
    json_body: Mapping[str, object] | None = None
    params: Mapping[str, str] | None = None
    allow_404: bool = False
