"""The Release Name: a Release's synthetic, release-level CalVer identity (vYYYY.MM.DD.N)."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class ReleaseName:
    value: str

    @property
    def asset_filename(self) -> str:
        return f"vaudeville-{self.value}.tar.gz"


def next_release_name(today: date, taken: Iterable[str]) -> ReleaseName:
    # Pad month and day so the release list sorts chronologically: unpadded, an October–December
    # tag would sort lexically before a single-digit month. (PEP 440 strips the padding from the
    # wheels' own versions, which sorts numerically anyway; the padding is the tag's, not the
    # package's.) The counter disambiguates same-day Releases.
    #
    # `taken` is the Published Home's git tag namespace: `gh release create` reuses an existing tag,
    # so a Release Name is free exactly when no tag already stamps it.
    stem = f"v{today.year}.{today.month:02d}.{today.day:02d}"
    already = set(taken)
    counter = 1
    while f"{stem}.{counter}" in already:
        counter += 1
    return ReleaseName(f"{stem}.{counter}")
