from __future__ import annotations

import os
from pathlib import Path

ENV_VAR = "VV_DATA_DIR"


def data_dir() -> Path:
    # Empty override is treated as unset so a stray `export VV_DATA_DIR=` in a
    # shell does not silently redirect reads to a weird path.
    override = os.environ.get(ENV_VAR)
    base = Path(override) if override else Path.home() / ".vaudeville"
    # Resolve to an absolute, symlink-canonical path. `prime` runs the Bedrock with
    # this as the claude cwd, and Claude Code keys the transcript under the resolved
    # cwd; the per-repo fork then seeds from project_directory(data_files_root). A
    # relative or symlinked value would key those two differently and strand the Bedrock.
    return base.expanduser().resolve()
