from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExitProfile:
    state_name: str
    workflow_name: str | None
    comment_header: str


DELIVERED = ExitProfile("Delivered", None, "## Closeout Synopsis")
ABANDONED = ExitProfile("Abandoned", None, "## Obsolete Reason")
RETURNED = ExitProfile("Active", "Returned", "## Return Note")
UNCLAIM = ExitProfile("Ready", "Submitted", "")
