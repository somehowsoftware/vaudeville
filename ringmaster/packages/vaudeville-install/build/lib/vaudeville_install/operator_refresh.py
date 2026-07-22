"""The operator-facing Refresh flow: plan, preview, gate a reprime on the operator's consent, apply,
and report. Pure over the injected capabilities (the confirm prompt, the report sink, the host
``vv`` runner), so a test drives the whole flow with no terminal and no real ``vv``; the composition
root (``operator_cli``) supplies the real ones.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from vaudeville_install.destination import Layout
from vaudeville_install.host_vv import RunVv
from vaudeville_install.refresh import apply_refresh_plan, refresh_plan_for
from vaudeville_install.refresh_report import applied_report, dry_run_report, reprime_prompt


def run_refresh(
    *,
    config_dir: Path,
    layout: Layout,
    prime_vv: RunVv,
    dry_run: bool,
    assume_yes: bool,
    confirm: Callable[[str], bool],
    report: Callable[[str], None],
) -> None:
    plan = refresh_plan_for(config_dir, layout)
    if dry_run:
        report(dry_run_report(plan, config_dir))
        return
    if plan.reprime_needed and not assume_yes and not confirm(reprime_prompt(plan)):
        report("Refresh cancelled; nothing was changed.")
        return
    apply_refresh_plan(plan, config_dir, layout, prime_vv)
    report(applied_report(plan, config_dir))
