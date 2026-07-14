# Install: the common half of the deploy, placing an Artifact at a Destination, reading only it.

from __future__ import annotations

import shutil
from pathlib import Path

from vaudeville_install.artifact import (
    DOC_TREE_NAMES,
    FACADE_DISTRIBUTION,
    REQUIRED_TENANT_CONFIG_FILENAMES,
    RESERVED_FILENAMES,
    Artifact,
)
from vaudeville_install.data_file_ledger import (
    prune_data_files_a_prior_install_placed,
    record_placed_data_files,
)
from vaudeville_install.destination import Destination, Host, Layout, Rehearsal
from vaudeville_install.doc_tree import install_doc_tree_at
from vaudeville_install.hook_wiring import hook_wiring_for
from vaudeville_install.settings import write_owned_settings
from vaudeville_install.tenant_config import (
    TenantConfigUnreadable,
    raise_if_required_tenant_config_missing,
)
from vaudeville_install.tenant_hooks import (
    place_tenant_hook_scripts,
    raise_if_tenant_hook_scripts_collide,
)
from vaudeville_install.trust_declarations import trust_declarations_for
from vaudeville_install.uv_operations import PUBLIC_INDEX, InstallComposedCLI

# Named once here so the placer and a Refresh reading back what it wrote resolve the same subtree.
PROJECT_DOCS_DIRNAME = "project-docs"


def install_artifact(
    artifact: Artifact,
    destination: Destination,
    *,
    config_dir: Path,
    install_composed_cli: InstallComposedCLI,
) -> None:
    # Both guards run before _prepare wipes the host's trees, so a tenant-config fault — a hook-name
    # collision, or a required config file the config dir lacks — aborts untouched, not mid-install.
    raise_if_tenant_hook_scripts_collide(artifact.hooks, config_dir)
    raise_if_required_tenant_config_missing(config_dir)
    layout = destination.layout
    _prepare(destination)
    _place_skills(artifact, layout)
    _place_hooks(artifact, layout, config_dir)
    _place_data_files(artifact, destination)
    _place_doc_trees(artifact, layout)
    place_config(config_dir, layout)
    _write_settings(artifact, destination, config_dir)
    _install_composed_cli(artifact, layout, install_composed_cli)
    _mirror_host_state(destination)


def _prepare(destination: Destination) -> None:
    match destination:
        case Rehearsal(root=root):
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


def _place_hooks(artifact: Artifact, layout: Layout, config_dir: Path) -> None:
    shutil.copytree(artifact.hooks, layout.hooks_dir)
    place_tenant_hook_scripts(config_dir, layout.hooks_dir)


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


def place_config(config_dir: Path, layout: Layout) -> None:
    # The tenant's config, copied from the operator's config dir into the data dir each deploy: the
    # project map and credentials, plus the project-docs tree rebuilt wholesale so the data dir
    # reflects the config dir. (The Registry is integrator-internal: it ships with Ringmaster as
    # package data, read from beside the module, and is never copied here.)
    #
    # The one placer of the Tenant Config, shared by an Install and a Refresh, so a Refresh cannot
    # drift from what an Install would place.
    data_dir = layout.data_dir
    data_dir.mkdir(parents=True, exist_ok=True)
    for name in REQUIRED_TENANT_CONFIG_FILENAMES:
        source = config_dir / name
        try:
            shutil.copy2(source, data_dir / name)
        except FileNotFoundError as missing:
            # A Tenant Config the install must place but the config dir lacks: name the file the
            # operator has to provide rather than let a raw FileNotFoundError escape as a traceback.
            raise TenantConfigUnreadable(source, missing) from missing
    placed_docs = data_dir / PROJECT_DOCS_DIRNAME
    if placed_docs.exists():
        shutil.rmtree(placed_docs)
    config_docs = config_dir / PROJECT_DOCS_DIRNAME
    if config_docs.is_dir():
        shutil.copytree(config_docs, placed_docs)


def _write_settings(artifact: Artifact, destination: Destination, config_dir: Path) -> None:
    write_owned_settings(
        destination.layout.settings_path,
        hook_wiring=hook_wiring_for(artifact, config_dir, destination.layout.hooks_dir),
        trust_declarations=trust_declarations_for(config_dir),
        base_settings_path=_settings_base_for(destination),
    )


def _settings_base_for(destination: Destination) -> Path | None:
    match destination:
        case Rehearsal(host_home=host_home):
            return host_home / ".claude" / "settings.json"
        case Host():
            return None


def _install_composed_cli(
    artifact: Artifact, layout: Layout, install_composed_cli: InstallComposedCLI
) -> None:
    install_composed_cli(
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
        case Rehearsal(root=root, host_home=host_home):
            host_dotfile = host_home / ".claude.json"
            if host_dotfile.is_file():
                # claude writes back to .claude.json, so the Rehearsal Installation copies
                # it rather than symlinking; the stand-in must never be a writeback
                # path into operator state.
                shutil.copy2(host_dotfile, root / ".claude.json")
            host_credentials = host_home / ".claude" / ".credentials.json"
            if host_credentials.exists():
                # Symlinked so host credential rotation stays visible to in-flight
                # stages without a re-stage.
                (root / ".credentials.json").symlink_to(host_credentials)
