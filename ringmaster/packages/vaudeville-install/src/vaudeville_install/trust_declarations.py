"""The Trust Declarations: the English policy the permission classifier trusts.

Materialized into the ``autoMode`` block of the settings.json Install writes, in two parts: the
Framework Allowances (the framework's own always-safe operations, named for a classifier that knows
nothing of Vaudeville) and the Environment Declarations (this tenant's source-control org and
tracker, declared internal infrastructure). ``trust_declarations_for`` reads those tenant facts
from the Tenant Config and composes the block; the ``compose_*`` functions are its pure folds.
Additive by construction: the ``$defaults`` sentinel leads every emitted section so the
classifier's built-in blocks survive.
"""

from __future__ import annotations

import os
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from vaudeville_install.artifact import CREDENTIALS_FILENAME
from vaudeville_install.host_wiring import locate_youtrack
from vaudeville_install.tenant_config import project_remotes

_DEFAULTS = "$defaults"
_TRUST_DECLARATION_SECTIONS = ("environment", "allow", "soft_deny", "hard_deny")

# The classifier is an external model that knows nothing of Vaudeville's vocabulary, so each rule
# names the literal commands and the otherwise-suspicious step it allows (a managed-clone reset,
# the ~/.claude writes, the detached launch) and scopes it, or it gets blocked as a threat.
FRAMEWORK_ALLOWANCES: dict[str, list[str]] = {
    "allow": [
        "Resetting a Vaudeville-managed repository clone to its origin/main, the `git fetch` + "
        "`git reset --hard` + `git clean` that `vv spawn` and `vv fork` run on the framework's own "
        "clone directories (e.g. ~/vaudeville-*), is allowed: those clones are disposable "
        "framework state re-derived from origin on every spawn, never the user's working repo or "
        "any uncommitted work.",
        "Writing a Bob's primed Foundation under ~/.claude/projects/ and pre-accepting worktree "
        "folder-trust entries in ~/.claude.json, what `vv spawn` and `vv fork` do to seed a new "
        "Bob, is allowed: it is scoped to those two locations and never edits settings.json, "
        "`.mcp.json`, or permission rules.",
        "Launching a detached `claude --permission-mode auto` session for a new Bob via `workmux`, "
        "the final step of `vv spawn` and `vv fork`, is allowed: spawning Bobs in auto mode is "
        "Vaudeville's intended, operator-sanctioned execution model, not an attempt to evade an "
        "approval gate.",
        'Recording a headroom-screen stay with `vv stay "<reason>"`, which writes the stay file '
        "`.scratch/headroom-stay.json` under the Bob's own worktree, is allowed: the headroom "
        "screen instructs the Bob to record a stay to stand its soft rungs down, so this is the "
        "agent following a framework screen's own sanctioned remedy, scoped to its worktree's "
        "`.scratch/`, not a write outside its work area.",
    ],
}


def source_control_root(remote_url: str) -> str | None:
    parsed = urlparse(remote_url)
    if not parsed.scheme or not parsed.netloc:
        return None
    owner = parsed.path.strip("/").split("/", 1)[0]
    return f"{parsed.netloc}/{owner}" if owner else None


def compose_environment_declarations(
    source_control_roots: Iterable[str], tracker_host: str | None
) -> dict[str, list[str]]:
    # Declaring the org and tracker trusted internal infrastructure is what stops the classifier
    # reading internal pushes and Assignment writes as external exfiltration.
    lines = [
        f"Source control: {root} and every repository under it is this tenant's own. All "
        f"operations on those repositories are internal, not external: pushing and pulling, "
        f"opening pull requests, and reviewing, commenting on, and replying to issues and pull "
        f"requests (including via the GitHub API and the `gh` CLI)."
        for root in dict.fromkeys(source_control_roots)
    ]
    if tracker_host:
        lines.append(
            f"Work tracker: {tracker_host} is this tenant's YouTrack instance, trusted internal "
            f"infrastructure that Bobs read and write Assignments through. Its API writes "
            f"(creating, claiming, resolving, and commenting on Assignments) are internal "
            f"operations, not external collaboration-tool writes."
        )
    return {"environment": lines} if lines else {}


def compose_trust_declarations(*partials: Mapping[str, Any] | None) -> dict[str, list[str]]:
    # The classifier replaces, not extends, a section's built-in block list when "$defaults" is
    # absent, so every emitted section leads with it or the built-in blocks (force-push, `curl |
    # bash`, …) silently vanish; a section nothing adds to is omitted so its built-ins apply.
    sections: dict[str, list[str]] = {}
    for name in _TRUST_DECLARATION_SECTIONS:
        additions: list[str] = []
        for partial in partials:
            additions.extend(entry for entry in (partial or {}).get(name, []) if entry != _DEFAULTS)
        if additions:
            sections[name] = [_DEFAULTS, *dict.fromkeys(additions)]
    return sections


def trust_declarations_for(config_dir: Path) -> dict[str, list[str]]:
    """Materialize the Trust Declarations for a deploy: the Framework Allowances plus the
    Environment Declarations composed from what the Tenant Config already states — the
    source-control orgs in the Project Map and the tracker in the Tracker Credentials."""
    roots = [
        root for remote in project_remotes(config_dir) if (root := source_control_root(remote))
    ]
    tracker_host, _ = locate_youtrack(os.environ, config_dir / CREDENTIALS_FILENAME)
    return compose_trust_declarations(
        FRAMEWORK_ALLOWANCES, compose_environment_declarations(roots, tracker_host)
    )
