"""What the Artifact carries: the Contributions whose source ends up inside it.

The one definition of the carried set, so Build's placement and the Provenance's record of what
shipped derive from the same source and cannot drift apart.
"""

from __future__ import annotations

from vaudeville_ringmaster.contribution import Contribution
from vaudeville_ringmaster.manifest import Manifest


def contribution_carries_a_wheel(contribution: Contribution) -> bool:
    # A distribution rides in the Artifact when it backs the integrated command line: the
    # Command-Surface Contributors and the libraries they share. A Contributor that builds its own
    # CLI but contributes no Command Surface (the integrator itself) is build-time tooling, not
    # part of what installs.
    return contribution.distribution is not None and (
        contribution.cli_declaration is not None or not contribution.console_scripts
    )


def contribution_carries_scaffold(contribution: Contribution) -> bool:
    # Must stay in lockstep with the scaffold slots Build collects into the Artifact (build.py): a
    # slot Build carries but this omits would drop a shipped source from the Provenance. Hook
    # Matchers count too, even though Build merges them into hook-matchers.json rather than copying.
    return bool(
        contribution.skills
        or contribution.data_files
        or contribution.doc_trees
        or contribution.hook_scripts
        or contribution.hook_matchers is not None
    )


def carried_contributions(manifest: Manifest) -> list[Contribution]:
    return [
        contribution
        for contribution in manifest.contributions
        if contribution_carries_a_wheel(contribution) or contribution_carries_scaffold(contribution)
    ]
