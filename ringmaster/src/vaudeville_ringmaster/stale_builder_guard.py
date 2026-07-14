"""The Stale Builder guard: refuse a Deploy or Publish driven by a running Ringmaster older than the
vaudeville-ringmaster Session Clone it would build from, so a stale Builder cannot silently drive a
release with its own outdated install code and Registry."""

from __future__ import annotations

import re
import subprocess
from enum import Enum, auto
from pathlib import Path

import vaudeville_ringmaster

# The Home Repo's Contributor name: the one Contributor that is also the Builder, present in every
# federation. Deploy's Self-update reaches for the same clone at `session_clones_dir / this`.
HOME_REPO_NAME = "vaudeville-ringmaster"

# A Builder's position in the Home Repo's main history: the nearest release tag as a CalVer stem
# `vYYYY.MM.DD.N` read as (year, month, day, counter), paired with the commits landed since that
# tag. The stem alone is not the commit order: main carries untagged commits between tags — the
# auto-tag workflow accepts an unpaired intermediate during a merge burst of 3+ (`ci.yml`), and a
# deploy clones whatever HEAD is, tagged or not. So a stale host at tag T and an up-to-date worktree
# some commits past T share the stem T and are told apart only by the commits-since-tag distance,
# which setuptools-scm and `git describe` both derive from that nearest tag. Ordering these pairs
# lexicographically — stem first, distance to break a stem tie — answers "older than" in the
# domain's own terms without leaning on any packaging library.
CalVer = tuple[int, int, int, int]
BuilderPosition = tuple[CalVer, int]

# The CalVer stem: four leading dot-separated integers after an optional `v`, int-parsed so a tag's
# zero-padding (`v2026.07.08.2`) and setuptools-scm's stripped form (`2026.7.8.2`) read alike.
_CALVER_STEM = re.compile(r"v?(\d+)\.(\d+)\.(\d+)\.(\d+)")

# Commits-since-tag, encoded differently by the two release-identity sources that reach the parse:
# setuptools-scm no-guess-dev stamps `<stem>.post1.dev<N>+g<sha>`, `git describe` stamps
# `<stem>-<N>-g<sha>`. Both count from the nearest tag; an exact tag carries neither and is distance
# 0. The two forms never collide — no `git describe` output contains `.dev`, and setuptools-scm's
# local segment joins with `+`, never the `-<N>-g` git uses.
_SCM_DISTANCE = re.compile(r"\.dev(\d+)")
_DESCRIBE_DISTANCE = re.compile(r"-(\d+)-g[0-9a-f]+")


class BuilderVerdict(Enum):
    CURRENT = auto()
    STALE = auto()
    RUNNING_INDETERMINATE = auto()
    HOME_REPO_INDETERMINATE = auto()


def builder_position(version: str) -> BuilderPosition | None:
    # Parse a release identity — a running `__version__` or a `git describe` — into its comparable
    # position. A string with no CalVer stem (the `0.0.0+source` fallback, an empty `git describe`)
    # is no position at all: None, an indeterminacy the verdict names, never a version that sorts
    # lowest.
    stem = _CALVER_STEM.match(version)
    if stem is None:
        return None
    calver = (int(stem[1]), int(stem[2]), int(stem[3]), int(stem[4]))
    return (calver, _commits_since_tag(version))


def _commits_since_tag(version: str) -> int:
    for pattern in (_SCM_DISTANCE, _DESCRIBE_DISTANCE):
        match = pattern.search(version)
        if match is not None:
            return int(match[1])
    return 0


def builder_verdict(running: str, home_repo: str) -> BuilderVerdict:
    running_position = builder_position(running)
    home_repo_position = builder_position(home_repo)
    # Indeterminacy is diagnosed per side before any comparison: "I cannot establish a version" is a
    # different fact from "I am older", with a different fix. The running side is named first so its
    # fix is the one shown when neither version can be read.
    if running_position is None:
        return BuilderVerdict.RUNNING_INDETERMINATE
    if home_repo_position is None:
        return BuilderVerdict.HOME_REPO_INDETERMINATE
    if running_position < home_repo_position:
        return BuilderVerdict.STALE
    return BuilderVerdict.CURRENT


def enforce_current_builder(session_clones_dir: Path) -> None:
    # The effectful boundary: read the running Builder's version and the Home Repo Session Clone's
    # release identity, hand both to the pure verdict as values, and refuse on anything but CURRENT.
    # Injected into Deploy and Publish rather than called inline, because these two readings are not
    # satisfiable from a Session's real git state the way the Pristine guard's are.
    running = vaudeville_ringmaster.__version__
    home_repo = _home_repo_release_identity(session_clones_dir / HOME_REPO_NAME)
    verdict = builder_verdict(running, home_repo)
    if verdict is BuilderVerdict.CURRENT:
        return
    if verdict is BuilderVerdict.STALE:
        raise StaleBuilder(running=running, home_repo=home_repo)
    raise IndeterminateBuilderVersion(verdict=verdict, running=running, home_repo=home_repo)


class StaleBuilder(RuntimeError):
    def __init__(self, *, running: str, home_repo: str) -> None:
        super().__init__(running, home_repo)
        self.running = running
        self.home_repo = home_repo

    def __str__(self) -> str:
        return (
            f"The running ringmaster ({self.running}) is older than the {HOME_REPO_NAME} Session "
            f"Clone it would build from ({self.home_repo}): it would build with its own outdated "
            "install code and Registry, not the code being released. Re-run from the updated "
            "worktree (`uv run --python 3.14 ringmaster …`), or let a prior `ringmaster apply` "
            "self-update the host tool first."
        )


class IndeterminateBuilderVersion(RuntimeError):
    def __init__(self, *, verdict: BuilderVerdict, running: str, home_repo: str) -> None:
        super().__init__(verdict, running, home_repo)
        self.verdict = verdict
        self.running = running
        self.home_repo = home_repo

    def __str__(self) -> str:
        if self.verdict is BuilderVerdict.RUNNING_INDETERMINATE:
            return (
                f"The running ringmaster reports no release version ({self.running}), so it cannot "
                f"be checked against the {HOME_REPO_NAME} Session Clone it would build from. Run "
                "from an installed ringmaster or the updated worktree "
                "(`uv run --python 3.14 ringmaster …`), not from unmanaged source."
            )
        return (
            f"The {HOME_REPO_NAME} Session Clone carries no release tag "
            f"({self.home_repo or 'none'}), so the running ringmaster cannot be checked against "
            "the code it would build from. Re-open the Session with `ringmaster clone` to restore "
            "a clean Home Repo."
        )


def _home_repo_release_identity(home_repo: Path) -> str:
    # The Home Repo's Builder identity is the `git describe` of its checked-out commit against the
    # release tags. `--match 'v[0-9]*'` reads only the release tags (never a stray non-version tag).
    # No `--abbrev=0`: the bare nearest tag would report a HEAD one or more commits past that tag as
    # the tag itself, so a host still on that tag would tie the newer Session Clone and pass — the
    # untagged-merge-burst hole this guard exists to close. The full describe carries the
    # commits-since-tag distance that tells the two apart. An empty string when no release tag is
    # reachable, which parses to no position, so the guard refuses fail-safe rather than vouch for a
    # currency it cannot establish.
    result = subprocess.run(
        ["git", "describe", "--tags", "--match", "v[0-9]*"],
        cwd=home_repo,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()
