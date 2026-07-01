"""Compose the body of an incident-report investigation Command from captured fields.

The operator flags an incident and asks an agent to file a report on it. There is
nothing to author, only to capture: this module lays the witness's observed problem
and a pointer to the transcript into a fixed shape, with no composition discretion.
The Command the body rides in is unsigned and check-in routed; the operator signs it
off later to authorize the investigation, and a clear-headed reader diagnoses from the
transcript, which is the ground truth the body only indexes.

The problem is quoted as a blockquote rather than inlined, the same guard ``tangent``
uses: a witness account may contain markdown headings or bullets, and inlining would
let that captured text masquerade as authored body structure. The fixed form admits no
diagnosis, root cause, or remedy of its own; a cause has no place to go.
"""

from __future__ import annotations

_BANNER = (
    "> **Incident report — unsigned investigation Command.** Filed via `vv incident-report` "
    "because the operator flagged an incident. The account below is a witness's observation of "
    "what went wrong, not a diagnosis; the transcript named under *Where the transcript is* is the "
    "ground truth this body only indexes. Sign this off to authorize the investigation: a "
    "clear-headed Bob picks it up, reads the transcript, and does the diagnosing. There is "
    "deliberately no root cause here."
)

_ARCHIVAL_NOTE = (
    "Worktrees are archived on teardown, so the path above may no longer exist by the time the "
    "investigation runs. If it is gone, look for the same worktree name under the Component's "
    "`__worktrees__archive/`, or resolve the transcript from the session id."
)


def _quoted(captured: str) -> str:
    return "\n".join(f"> {line}" if line else ">" for line in captured.split("\n"))


def compose_body(
    problem: str,
    component: str,
    worktree: str,
    assignment: str | None,
    session: str | None,
) -> str:
    return (
        f"{_BANNER}\n\n"
        f"## What went wrong (observed)\n\n{_quoted(problem)}\n\n"
        f"## Where the transcript is\n\n"
        f"- Component: {component}\n"
        f"- Assignment: {assignment or 'none (ad-hoc session, no Assignment)'}\n"
        f"- Worktree: {worktree}\n"
        f"- Session: {session or 'unknown — resolve from the worktree transcript store'}\n\n"
        f"{_ARCHIVAL_NOTE}\n"
    )
