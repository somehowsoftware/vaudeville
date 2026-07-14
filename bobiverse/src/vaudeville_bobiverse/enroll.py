from __future__ import annotations

import subprocess
import sys
from collections.abc import Callable
from enum import Enum
from pathlib import Path
from typing import NoReturn

from vaudeville_core import provision, register_component
from vaudeville_core.component import Component

SPEC_FRONT_MATTER = (
    "*This is a spec: high-level WHAT. Low-level WHAT is in the test suite; HOW is in the code.*"
)
VOCABULARY_FRONT_MATTER = (
    "*This is a UL doc: terms defined in relation to one another. For "
    "framework-level UL see `~/.vaudeville/doctrine/vocabulary.md`.*"
)


class ComponentKind(Enum):
    context = "context"
    resource = "resource"


def documentary_skeleton(kind: ComponentKind) -> dict[Path, str]:
    if kind is ComponentKind.resource:
        return {}
    return {
        Path("docs/spec.md"): _doc_stub("Spec", SPEC_FRONT_MATTER),
        Path("docs/vocabulary.md"): _doc_stub("Vocabulary", VOCABULARY_FRONT_MATTER),
    }


def _doc_stub(title: str, front_matter: str) -> str:
    return f"# {title}\n\n{front_matter}\n"


def scaffold(repo_path: Path, skeleton: dict[Path, str]) -> tuple[list[Path], list[Path]]:
    written: list[Path] = []
    skipped: list[Path] = []
    for relative, content in skeleton.items():
        target = repo_path / relative
        if target.exists():
            skipped.append(relative)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        written.append(relative)
    return written, skipped


def is_repository_root(repo_path: Path) -> bool:
    result = subprocess.run(
        ["git", "-C", str(repo_path), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return False
    return Path(result.stdout.strip()).resolve() == repo_path.expanduser().resolve()


def origin_remote(repo_path: Path) -> str | None:
    result = subprocess.run(
        ["git", "-C", str(repo_path), "remote", "get-url", "origin"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def enroll(
    prefix: str,
    *,
    repo_path: Path,
    name: str,
    kind: ComponentKind,
    remote: str | None,
    short_name: str | None,
    description: str | None,
    host_config_dir: Path,
    provision_project: Callable[[str, str], str] = provision,
    register: Callable[..., None] = register_component,
    report: Callable[[str], None] = print,
) -> None:
    if not is_repository_root(repo_path):
        _abort(
            f"{repo_path} is not the root of a git repository. `enroll` wires an "
            f"existing repository into Vaudeville; point --repo-path at the "
            f"repository's top-level directory (create and check it out first if it "
            f"does not yet exist)."
        )

    canonical_remote = remote if remote is not None else origin_remote(repo_path)
    if canonical_remote is None:
        _abort(
            f"{repo_path} has no `origin` remote and --remote was not given. `enroll` "
            f"stands up a Component that `vaudeville prime` clones from its remote, so "
            f"give the repository an origin (or pass --remote) and enroll again."
        )

    skeleton = documentary_skeleton(kind)

    tracker_project_id = provision_project(prefix, name)
    report(f"Provisioned tracker project {prefix} ({tracker_project_id}).")

    register(
        Component(
            prefix=prefix,
            tracker_project_id=tracker_project_id,
            repo_path=repo_path,
            description=description,
            remote=canonical_remote,
            name=name,
            short_name=short_name,
        ),
        host_config_dir=host_config_dir,
    )
    report(f"Registered {prefix} in vaudeville.toml.")

    _report_scaffold(report, kind, scaffold(repo_path, skeleton))
    _report_prime_tail(report, prefix)


def _report_scaffold(
    report: Callable[[str], None],
    kind: ComponentKind,
    outcome: tuple[list[Path], list[Path]],
) -> None:
    if kind is ComponentKind.resource:
        report("Scaffolded no documentary skeleton (a Resource holds no domain to specify).")
        return
    written, skipped = outcome
    if written:
        report(f"Scaffolded {_join(written)}.")
    if skipped:
        report(f"Left in place (already present) {_join(skipped)}.")


def _report_prime_tail(report: Callable[[str], None], prefix: str) -> None:
    report(
        f"Next: commit and push the scaffold to {prefix}'s origin, then run "
        f"`vaudeville prime {prefix}` to build its Foundation."
    )


def _join(paths: list[Path]) -> str:
    return ", ".join(str(path) for path in paths)


def _abort(message: str) -> NoReturn:
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(1)
