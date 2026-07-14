"""Whether a root is a well-formed Artifact: the layout-completeness check both halves run.

Build runs it to recognize a directory it already produced as a placeable Artifact; Install runs it
at its boundary before reading a root as one. It is filesystem I/O over the [Artifact](artifact.py)
contract, kept out of that contract so the pure shape stays importable without any placement
machinery.
"""

from __future__ import annotations

from pathlib import Path

from vaudeville_install.artifact import Artifact


def missing_artifact_components(artifact: Artifact) -> list[str]:
    """The layout components a root lacks; empty for an Artifact Build produced.

    Build always creates every slot directory (even when empty) and writes the matcher fragment, so
    a root missing any of these was not produced by Build: a wrong or partial path.
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
