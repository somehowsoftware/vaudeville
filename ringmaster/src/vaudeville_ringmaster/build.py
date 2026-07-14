"""Build: integrate a Manifest into a destination-ignorant Artifact."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from vaudeville_install.artifact import Artifact
from vaudeville_install.doc_tree import install_doc_tree_at

from vaudeville_ringmaster.carried_cli import carry_integrated_cli_into
from vaudeville_ringmaster.data_file import install_data_file_at
from vaudeville_ringmaster.hook_matchers import merge_hook_matchers
from vaudeville_ringmaster.hook_script import install_hook_script_at
from vaudeville_ringmaster.manifest import Manifest
from vaudeville_ringmaster.skill import install_skill_at
from vaudeville_ringmaster.uv_operations import BuildWheel


def build_artifact(manifest: Manifest, root: Path, *, build_wheel: BuildWheel) -> Artifact:
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    artifact = Artifact(root=root)
    _collect_files_into(manifest, artifact)
    _merge_matchers_into(manifest, artifact)
    carry_integrated_cli_into(manifest, artifact.carried_cli, build_wheel)
    return artifact


def _collect_files_into(manifest: Manifest, artifact: Artifact) -> None:
    for directory in (artifact.skills, artifact.data_files, artifact.doc_trees, artifact.hooks):
        directory.mkdir(parents=True, exist_ok=True)
    for contribution in manifest.contributions:
        for skill in contribution.skills:
            install_skill_at(skill, artifact.skills)
        for data_file in contribution.data_files:
            install_data_file_at(data_file, artifact.data_files)
        for doc_tree in contribution.doc_trees:
            install_doc_tree_at(doc_tree.source_path, artifact.doc_trees / doc_tree.name)
        for hook_script in contribution.hook_scripts:
            install_hook_script_at(hook_script, artifact.hooks)


def _merge_matchers_into(manifest: Manifest, artifact: Artifact) -> None:
    matchers = [c.hook_matchers for c in manifest.contributions if c.hook_matchers is not None]
    artifact.hook_matchers.write_text(json.dumps(merge_hook_matchers(matchers), indent=2))
