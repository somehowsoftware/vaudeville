"""The Provenance: the authoritative record of what a Release's Artifact was built from."""

from __future__ import annotations

from dataclasses import dataclass

import vaudeville_install

import vaudeville_ringmaster
from vaudeville_ringmaster.carried_set import CarriedSet, carried_set_of
from vaudeville_ringmaster.manifest import Manifest
from vaudeville_ringmaster.pin import Pin
from vaudeville_ringmaster.pinned_set import PinnedSet

PROVENANCE_FILENAME = "provenance.toml"


@dataclass(frozen=True)
class Builder:
    ringmaster: str
    installer: str


@dataclass(frozen=True)
class Provenance:
    carried: CarriedSet
    builder: Builder


def provenance_of(pinned_set: PinnedSet, manifest: Manifest) -> Provenance:
    return Provenance(carried=carried_set_of(pinned_set, manifest), builder=running_builder())


def running_builder() -> Builder:
    # The builder is the running ringmaster that stamps the Facade, not a Contributor Session Clone,
    # so it is recorded by its own version and its installer's rather than by a clone-time commit.
    return Builder(
        ringmaster=vaudeville_ringmaster.__version__,
        installer=vaudeville_install.__version__,
    )


def render_provenance_toml(provenance: Provenance) -> str:
    header = (
        "# Build provenance for this Vaudeville release. The [contributors] tables record each\n"
        "# Contributor repository and the exact commit its source was built from; the [builder]\n"
        "# table records the integrator that generated the Facade and built the installer. The\n"
        "# surrounding tree is a curated reading copy; these are the authoritative build input.\n"
    )
    contributor_tables = "\n".join(_contributor_table(pin) for pin in provenance.carried.pins)
    return f"{header}\n{contributor_tables}\n{_builder_table(provenance.builder)}"


def _contributor_table(pin: Pin) -> str:
    # Contributor names (vaudeville-bobiverse, …) are valid TOML bare keys: letters, digits, and the
    # hyphen are exactly the bare-key alphabet, so no quoting is needed.
    return f'[contributors.{pin.name}]\nremote = "{pin.remote}"\ncommit = "{pin.commit}"\n'


def _builder_table(builder: Builder) -> str:
    # The integrator that built the Artifact is not a Contributor Session Clone, so it is identified
    # by its running version rather than a clone-time commit.
    return f'[builder]\nringmaster = "{builder.ringmaster}"\ninstaller = "{builder.installer}"\n'
