"""The Build operation: assemble the Session into a durable, self-installing Artifact.

`ringmaster build` emits an Artifact to an operator-chosen path the operator keeps, where Stage and
Apply build one into a temp dir in passing. That durable, user-supplied target is the difference
that earns this its own safe-target precondition: build_artifact wipes its root, so the operation
refuses to clobber a path that exists and is neither empty nor already an Artifact before it
assembles anything. The wipe is correct for the ephemeral roots Stage and Apply own, so the guard
belongs here on the operator's target rather than in the Build phase every operation shares.
"""

from __future__ import annotations

from pathlib import Path

from vaudeville_install.artifact import Artifact
from vaudeville_install.placement import missing_artifact_components

from vaudeville_ringmaster.assemble import assemble_apply_plan
from vaudeville_ringmaster.build import build_artifact
from vaudeville_ringmaster.registry import Registry
from vaudeville_ringmaster.session_clone import require_each_session_clone_present_in
from vaudeville_ringmaster.uv_operations import BuildWheel


def build(
    registry: Registry, session_clones_dir: Path, out: Path, *, build_wheel: BuildWheel
) -> Artifact:
    refuse_unsafe_build_target(out)
    clones = require_each_session_clone_present_in(registry, session_clones_dir)
    plan = assemble_apply_plan(registry, clones)
    return build_artifact(plan, out, build_wheel=build_wheel)


def refuse_unsafe_build_target(out: Path) -> None:
    # build_artifact wipes its output root, and out is user-supplied and durable: a typo like
    # `--out .` or an existing checkout would be deleted before the build. A fresh path and an empty
    # directory are safe to write into, and rebuilding over a prior Artifact is the intended reuse;
    # anything else is operator state this refuses to clobber.
    if not out.exists():
        return
    if out.is_dir() and not any(out.iterdir()):
        return
    if out.is_dir() and not missing_artifact_components(Artifact(root=out)):
        return
    raise UnsafeBuildTarget(out)


class UnsafeBuildTarget(RuntimeError):
    def __init__(self, out: Path) -> None:
        super().__init__(out)
        self.out = out

    def __str__(self) -> str:
        return (
            f"Refusing to build into {self.out}: it exists and is not empty, and is not a prior "
            "Artifact. Choose a fresh path or remove it first."
        )
