from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExitProfile:
    state_name: str
    workflow_name: str | None
    unassign: bool
    comment_header: str


DELIVERED = ExitProfile("Delivered", None, False, "## Closeout Synopsis")
ABANDONED = ExitProfile("Abandoned", None, True, "## Obsolete Reason")
RETURNED = ExitProfile("Active", "Returned", True, "## Return Note")
UNCLAIM = ExitProfile("Ready", "Submitted", True, "")
