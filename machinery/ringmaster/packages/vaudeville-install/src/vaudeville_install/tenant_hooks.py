"""The tenant's own Hook Scripts and Hook Matchers, carried in its Tenant Config.

A tenant carries its own hooks inside its config dir, mirroring a Contributor's sibling scaffold
`.claude/hooks/` + `.claude/hooks.json` shape without the scaffold Contribution Layout a tenant is
not: the scripts in a directory, their matcher fragment beside it. Both are optional; a tenant that
supplies neither takes the same install as one with no hooks of its own. Install places these into
the one Owned hooks directory alongside the Contributor-sourced scripts and unions their matchers
into the [Hook Wiring](hook_wiring.py).
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

TENANT_HOOK_SCRIPTS_DIRNAME = "hooks"
TENANT_HOOK_MATCHERS_FILENAME = "hooks.json"


class HookScriptCollision(RuntimeError):
    def __init__(self, clashing_names: list[str]) -> None:
        super().__init__(clashing_names)
        self.clashing_names = clashing_names

    def __str__(self) -> str:
        names = ", ".join(self.clashing_names)
        return (
            f"Tenant Config hook script(s) {names} fold to the same placed filename as another "
            f"hook script bound for the one hooks directory — a stock hook, or another of the "
            f"tenant's own (a case-insensitive host resolves `Guard.sh` and `guard.sh` to one "
            f"file). Placing both would silently shadow one with the other. Rename the clashing "
            f"tenant script(s) under {TENANT_HOOK_SCRIPTS_DIRNAME}/ in the config dir."
        )


def placement_key(script_name: str) -> str:
    """The identity a placed hook script takes under the target filesystem's fold.

    Stock and tenant scripts are authored in two independent, byte-exact vocabularies but land in
    the one Owned hooks dir, where it is the *host* that decides which authored names name the same
    placed file: a case-insensitive host (macOS's default) resolves `Guard.sh` and `guard.sh` to
    one file. The placed filename is therefore a domain identity distinct from the authored one, and
    a hook-script collision is a clash of these keys, not of the raw names. `casefold()` is that
    fold. Naming the key here is what lets the guard and the copy reason about identity by one rule
    (the guard predicts exactly what the host does to the copy's target), and makes the next fold
    that ever bites — Unicode normalization, trailing-dot stripping — a one-line change to this
    function rather than a second special case scattered across the guard.
    """
    return script_name.casefold()


def raise_if_tenant_hook_scripts_collide(stock_hooks_dir: Path, config_dir: Path) -> None:
    # Run before the install wipes the host's hooks dir, so an operator's naming error aborts
    # before the install touches the Host at all. Stock and tenant scripts merge into the one
    # hooks dir by their placement_key, so the collision the domain cares about is two authored
    # scripts sharing a key — the axis is "two authors, one placed file", not "tenant vs stock":
    # a tenant script folds onto a stock one, or two of the tenant's own fold onto each other, and
    # place_tenant_hook_scripts' copy2 silently overwrites one with the other. Detect it over the
    # union of both provenances keyed by placement_key, naming the tenant script(s) the operator
    # can rename. Folding over-detects a case-only near-clash on a case-sensitive host, the safe
    # direction for a guard that only ever aborts an operator's naming mistake.
    tenant_hooks = config_dir / TENANT_HOOK_SCRIPTS_DIRNAME
    if not tenant_hooks.is_dir():
        return
    tenant_names = [entry.name for entry in tenant_hooks.iterdir() if entry.is_file()]
    stock_names = [entry.name for entry in stock_hooks_dir.iterdir() if entry.is_file()]

    names_by_key: dict[str, list[str]] = {}
    for name in stock_names + tenant_names:
        names_by_key.setdefault(placement_key(name), []).append(name)

    # A tenant name clashes when its key is claimed by more than one authored script: the tenant
    # itself contributes one, so a count above one means another script (stock or a second tenant).
    clashing = sorted(name for name in tenant_names if len(names_by_key[placement_key(name)]) > 1)
    if clashing:
        raise HookScriptCollision(clashing)


def place_tenant_hook_scripts(config_dir: Path, hooks_dir: Path) -> None:
    tenant_hooks = config_dir / TENANT_HOOK_SCRIPTS_DIRNAME
    if not tenant_hooks.is_dir():
        return
    for script in sorted(tenant_hooks.iterdir()):
        if script.is_file():
            # Place under the authored name, not its placement_key: the matcher fragment references
            # the script by its authored path. raise_if_tenant_hook_scripts_collide has already
            # ensured no two authored names share a placement_key, so writing each authored name
            # lands one file per placed identity with nothing shadowed.
            placed = hooks_dir / script.name
            shutil.copy2(script, placed)
            # A tenant may commit its hook without the executable bit git would otherwise carry;
            # Claude Code's runtime invocation fails without it, so ensure +x as Build does for a
            # Contributor's.
            placed.chmod(placed.stat().st_mode | 0o111)


def tenant_hook_matchers(config_dir: Path) -> dict[str, list[Any]]:
    fragment = config_dir / TENANT_HOOK_MATCHERS_FILENAME
    if not fragment.is_file():
        return {}
    matchers: dict[str, list[Any]] = json.loads(fragment.read_text())
    return matchers
