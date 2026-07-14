from __future__ import annotations

from pathlib import Path

from vaudeville_ringmaster.carried_set import carried_set_of
from vaudeville_ringmaster.changeset import Changeset, changeset_of
from vaudeville_ringmaster.github_release import RunGh
from vaudeville_ringmaster.pinned_set import pin_session_clones
from vaudeville_ringmaster.predecessor import resolve_predecessor
from vaudeville_ringmaster.pristine_guard import enforce_pristine_guard_on
from vaudeville_ringmaster.published_home import PUBLISHED_HOME
from vaudeville_ringmaster.registry import Registry
from vaudeville_ringmaster.session_clone import require_each_session_clone_present_in
from vaudeville_ringmaster.survey import survey_manifest


def assemble_changeset(registry: Registry, session_clones_dir: Path, run_gh: RunGh) -> Changeset:
    clones = require_each_session_clone_present_in(registry, session_clones_dir)
    enforce_pristine_guard_on(clones)
    carried_set = carried_set_of(
        pin_session_clones(registry, clones), survey_manifest(registry, clones)
    )
    return changeset_of(carried_set, resolve_predecessor(PUBLISHED_HOME, run_gh), run_gh)
