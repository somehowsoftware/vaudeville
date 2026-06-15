"""Install: the common half of the deploy — place an Artifact at a Destination, reading only it."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from vaudeville_install.artifact import (
    CREDENTIALS_FILENAME,
    DOC_TREE_NAMES,
    FACADE_DISTRIBUTION,
    PROJECT_MAP_FILENAME,
    RESERVED_FILENAMES,
    Artifact,
)
from vaudeville_install.data_file_ledger import (
    prune_data_files_a_prior_install_placed,
    record_placed_data_files,
)
from vaudeville_install.destination import Destination, Host, Layout, Staging
from vaudeville_install.doc_tree import install_doc_tree_at
from vaudeville_install.hook_substitution import replace_hooks_dir_placeholder_in
from vaudeville_install.settings import write_settings_with_hooks
from vaudeville_install.uv_operations import PUBLIC_INDEX, InstallFacade


def missing_artifact_components(artifact: Artifact) -> list[str]:
    """The layout components a root lacks; empty for an Artifact Build produced.

    Build always creates every slot directory (even when empty) and writes the matcher fragment, so
    a root missing any of these was not produced by Build — a wrong or partial path.
    """
    required = {
        "skills/": artifact.skills,
        "data/": artifact.data_files,
        "doc-trees/": artifact.doc_trees,
        "hooks/": artifact.hooks,
        "cli/": artifact.carried_cli,
    }
    missing = [label for label, path in required.items() if not path.is_dir()]
    if not artifact.hook_matchers.is_file():
        missing.append("hook-matchers.json")
    return missing


class MalformedArtifact(RuntimeError):
    def __init__(self, root: Path, missing: list[str]) -> None:
        super().__init__(root, missing)
        self.root = root
        self.missing = missing

    def __str__(self) -> str:
        return (
            f"{self.root} is not a well-formed Artifact (missing: {', '.join(self.missing)}). "
            "Point --artifact at an Artifact produced by `ringmaster build`."
        )


def install_artifact(
    artifact: Artifact,
    destination: Destination,
    *,
    config_dir: Path,
    install_facade: InstallFacade,
) -> None:
    layout = destination.layout
    _prepare(destination)
    _place_skills(artifact, layout)
    _place_hooks(artifact, layout)
    _place_data_files(artifact, destination)
    _place_doc_trees(artifact, layout)
    _place_config(config_dir, layout)
    _write_settings(artifact, destination)
    _install_facade(artifact, layout, install_facade)
    _mirror_host_state(destination)


def _prepare(destination: Destination) -> None:
    match destination:
        case Staging(root=root):
            if root.exists():
                shutil.rmtree(root)
            root.mkdir(parents=True)
        case Host():
            layout = destination.layout
            # Doc-tree subtrees are framework-owned at fixed names under the data dir, exactly like
            # the skills and hooks directories: wipe them wholesale so a deploy that drops one
            # leaves nothing stale, then placement rebuilds whatever the Artifact still carries.
            framework_owned = [
                layout.skills_dir,
                layout.hooks_dir,
                *(layout.data_dir / name for name in DOC_TREE_NAMES),
            ]
            for owned in framework_owned:
                # Remove whatever sits at the owned path, not just a directory: a doc-tree slot may
                # hold a file from a legacy release that shipped the name as a Data File, and rmtree
                # raises on a non-directory.
                if owned.is_dir() and not owned.is_symlink():
                    shutil.rmtree(owned)
                elif owned.is_symlink() or owned.exists():
                    owned.unlink()


def _place_skills(artifact: Artifact, layout: Layout) -> None:
    shutil.copytree(artifact.skills, layout.skills_dir)


def _place_hooks(artifact: Artifact, layout: Layout) -> None:
    shutil.copytree(artifact.hooks, layout.hooks_dir)


def _place_data_files(artifact: Artifact, destination: Destination) -> None:
    data_dir = destination.layout.data_dir
    carried = sorted(path.name for path in artifact.data_files.iterdir() if path.is_file())
    match destination:
        case Host():
            # Reserved names are operator/framework state, never Contributor Data Files. Keep them
            # even if a stale ledger from a prior release lists one, so pruning cannot unlink the
            # operator's project map and delete state vv needs to resolve repos.
            prune_data_files_a_prior_install_placed(
                data_dir, keeping=set(carried) | RESERVED_FILENAMES
            )
    data_dir.mkdir(parents=True, exist_ok=True)
    for name in carried:
        shutil.copy2(artifact.data_files / name, data_dir / name)
    match destination:
        case Host():
            record_placed_data_files(data_dir, carried)


def _place_doc_trees(artifact: Artifact, layout: Layout) -> None:
    if not artifact.doc_trees.is_dir():
        return
    layout.data_dir.mkdir(parents=True, exist_ok=True)
    for subtree in sorted(artifact.doc_trees.iterdir()):
        if subtree.is_dir():
            install_doc_tree_at(subtree, layout.data_dir / subtree.name)


def _place_config(config_dir: Path, layout: Layout) -> None:
    # The tenant's config, copied from the operator's config dir into the data dir each deploy: the
    # project map and credentials, plus the project-docs tree rebuilt wholesale so the data dir
    # reflects the config dir. (The Registry is integrator-internal: it ships with Ringmaster as
    # package data, read from beside the module, and is never copied here.)
    data_dir = layout.data_dir
    data_dir.mkdir(parents=True, exist_ok=True)
    for name in (PROJECT_MAP_FILENAME, CREDENTIALS_FILENAME):
        shutil.copy2(config_dir / name, data_dir / name)
    placed_docs = data_dir / "project-docs"
    if placed_docs.exists():
        shutil.rmtree(placed_docs)
    config_docs = config_dir / "project-docs"
    if config_docs.is_dir():
        shutil.copytree(config_docs, placed_docs)


def _write_settings(artifact: Artifact, destination: Destination) -> None:
    merged = json.loads(artifact.hook_matchers.read_text())
    hooks_block = replace_hooks_dir_placeholder_in(merged, destination.layout.hooks_dir)
    write_settings_with_hooks(
        destination.layout.settings_path,
        hooks_block,
        base_settings_path=_settings_base_for(destination),
    )


def _settings_base_for(destination: Destination) -> Path | None:
    match destination:
        case Staging(host_home=host_home):
            return host_home / ".claude" / "settings.json"
        case Host():
            return None


def _install_facade(artifact: Artifact, layout: Layout, install_facade: InstallFacade) -> None:
    install_facade(
        distribution=FACADE_DISTRIBUTION,
        find_links=artifact.carried_cli,
        index_url=PUBLIC_INDEX,
        bin_dir=layout.bin_dir,
        tool_dir=layout.tool_dir,
    )


def _mirror_host_state(destination: Destination) -> None:
    match destination:
        case Host():
            return
        case Staging(root=root, host_home=host_home):
            host_dotfile = host_home / ".claude.json"
            if host_dotfile.is_file():
                # claude writes back to .claude.json, so the Staged Scaffold copies
                # it rather than symlinking — the stand-in must never be a writeback
                # path into operator state.
                shutil.copy2(host_dotfile, root / ".claude.json")
            host_credentials = host_home / ".claude" / ".credentials.json"
            if host_credentials.exists():
                # Symlinked so host credential rotation stays visible to in-flight
                # stages without a re-stage.
                (root / ".credentials.json").symlink_to(host_credentials)
