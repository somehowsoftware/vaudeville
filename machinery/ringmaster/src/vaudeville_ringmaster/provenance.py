"""The Provenance: the authoritative record of what a release's install Artifact was built from."""

from __future__ import annotations

from dataclasses import dataclass

import vaudeville_install

import vaudeville_ringmaster
from vaudeville_ringmaster.apply_plan import ApplyPlan
from vaudeville_ringmaster.carried_contribution import carried_contributions
from vaudeville_ringmaster.contribution import Contribution
from vaudeville_ringmaster.registry import Registry
from vaudeville_ringmaster.session_clone import recorded_clone_sha_at

PROVENANCE_FILENAME = "provenance.toml"


@dataclass(frozen=True)
class ContributorProvenance:
    name: str
    remote: str
    commit: str


@dataclass(frozen=True)
class BuilderProvenance:
    ringmaster: str
    installer: str


def provenance_for(registry: Registry, plan: ApplyPlan) -> tuple[ContributorProvenance, ...]:
    return tuple(
        _provenance_of(registry, contribution) for contribution in carried_contributions(plan)
    )


def builder_provenance() -> BuilderProvenance:
    # The integrator inputs Build embeds beyond the Contributor wheels: the Facade is stamped with
    # this version and the installer is built from this `vaudeville_install`. Read the same running
    # versions carried_cli stamps and builds from, so the record matches what actually shipped.
    return BuilderProvenance(
        ringmaster=vaudeville_ringmaster.__version__,
        installer=vaudeville_install.__version__,
    )


def _provenance_of(registry: Registry, contribution: Contribution) -> ContributorProvenance:
    commit = recorded_clone_sha_at(contribution.source_root)
    if commit is None:
        raise MissingCloneProvenance(contribution.name)
    return ContributorProvenance(
        name=contribution.name, remote=registry.remote_for(contribution.name), commit=commit
    )


def render_provenance_manifest(
    contributors: tuple[ContributorProvenance, ...], builder: BuilderProvenance
) -> str:
    header = (
        "# Build provenance for this Vaudeville release. The [contributors] tables record each\n"
        "# Contributor repository and the exact commit its source was built from; the [builder]\n"
        "# table records the integrator that generated the Facade and built the installer. The\n"
        "# surrounding tree is a curated reading copy; these are the authoritative build input.\n"
    )
    contributor_tables = "\n".join(_contributor_table(contributor) for contributor in contributors)
    return f"{header}\n{contributor_tables}\n{_builder_table(builder)}"


def _contributor_table(provenance: ContributorProvenance) -> str:
    # Contributor names (vaudeville-bobiverse, …) are valid TOML bare keys: letters, digits, and the
    # hyphen are exactly the bare-key alphabet, so no quoting is needed.
    return (
        f"[contributors.{provenance.name}]\n"
        f'remote = "{provenance.remote}"\n'
        f'commit = "{provenance.commit}"\n'
    )


def _builder_table(builder: BuilderProvenance) -> str:
    # The integrator that built the Artifact is not a Contributor Session Clone, so it is identified
    # by its running version rather than a clone-time commit.
    return f'[builder]\nringmaster = "{builder.ringmaster}"\ninstaller = "{builder.installer}"\n'


class MissingCloneProvenance(RuntimeError):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.name = name

    def __str__(self) -> str:
        return (
            f"Session Clone {self.name!r} carries no recorded clone-time commit, so its "
            "build provenance cannot be recorded. It was not produced by `ringmaster clone`; "
            "re-run Clone to open a fresh Session before Publish."
        )
