"""How a Refresh Plan reads to an operator: the dry-run report, the reprime prompt, and the applied
report ``vaudeville refresh`` shows. The one place that turns a plan into operator-facing words, so
the flow (``operator_refresh``) and the composition root carry no message text.
"""

from __future__ import annotations

from pathlib import Path

from vaudeville_install.refresh import RefreshPlan


def dry_run_report(plan: RefreshPlan, config_dir: Path) -> str:
    synced = (
        f"Refresh would sync your config (project map, credentials, project-docs) from "
        f"{config_dir}."
    )
    if plan.reprime_needed:
        return f"{synced}\nIt would reprime the Foundations:\n{_reprime_reason(plan)}"
    return f"{synced}\nThe project docs and map are unchanged, so it would not reprime."


def reprime_prompt(plan: RefreshPlan) -> str:
    return (
        "Refreshing will reprime the Foundations (re-running `vv prime`):\n"
        + _reprime_reason(plan)
        + "\nProceed?"
    )


def applied_report(plan: RefreshPlan, config_dir: Path) -> str:
    # The source leads. A sync from the wrong dir and a sync from the right one are the same run to
    # an operator who is never told which one it read, and that indistinguishability is what let a
    # host drift from its own config repo unnoticed.
    synced = f"Synced your config from {config_dir}."
    if plan.reprime_needed:
        return f"{synced} Reprimed the Foundations."
    return f"{synced} The project docs and map were unchanged, so the Foundations were left as-is."


def _reprime_reason(plan: RefreshPlan) -> str:
    reasons = []
    if plan.project_map_changed:
        reasons.append("The project map changed (a Component may have been added or removed).")
    if plan.changed_project_docs:
        reasons.append("These project docs changed:\n" + _changed_docs_listing(plan))
    return "\n".join(reasons)


def _changed_docs_listing(plan: RefreshPlan) -> str:
    return "\n".join(f"  - {doc}" for doc in sorted(plan.changed_project_docs))
