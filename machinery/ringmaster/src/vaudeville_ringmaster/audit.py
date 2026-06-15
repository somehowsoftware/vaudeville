"""The Audit."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

import yaml


class Severity(str, Enum):
    BLOCK = "BLOCK"
    FAIL = "FAIL"
    WARN = "WARN"
    REMOVED = "REMOVED"
    ADDED = "ADDED"


@dataclass(frozen=True)
class Finding:
    severity: Severity
    detail: str


@dataclass(frozen=True)
class SkillPresence:
    name: str
    skill_md_text: str | None


@dataclass(frozen=True)
class BuiltScaffoldContents:
    present_facade_executables: frozenset[str]
    skills_dir_present: bool
    skills: tuple[SkillPresence, ...]
    data_dir_present: bool


_FACADE_EXECUTABLES = ("vv", "vaudeville")

# The severities that make an Audit's verdict block the deploy. FAIL marks a structurally broken
# Scaffold; BLOCK is a finding raised expressly to stop it. The rest (WARN, and the ADDED/REMOVED
# drift notes) are advisory and do not block.
_BLOCKING_SEVERITIES = frozenset({Severity.FAIL, Severity.BLOCK})


def findings_are_blocking(findings: Iterable[Finding]) -> bool:
    return any(finding.severity in _BLOCKING_SEVERITIES for finding in findings)


def audit_built_scaffold(built_scaffold: Path, reference: Path | None = None) -> list[Finding]:
    contents = built_scaffold_contents_at(built_scaffold)
    reference_contents = built_scaffold_contents_at(reference) if reference is not None else None
    return findings_for(contents, reference_contents)


def findings_for(
    contents: BuiltScaffoldContents, reference: BuiltScaffoldContents | None = None
) -> list[Finding]:
    findings: list[Finding] = []
    findings.extend(_facade_findings(contents))
    findings.extend(_skills_findings(contents))
    findings.extend(_data_directory_findings(contents))
    if reference is not None:
        findings.extend(_skill_drift_findings(contents, reference))
    return findings


def _facade_findings(contents: BuiltScaffoldContents) -> list[Finding]:
    return [
        Finding(Severity.FAIL, f"Facade executable missing at bin/{name}")
        for name in _FACADE_EXECUTABLES
        if name not in contents.present_facade_executables
    ]


def _skills_findings(contents: BuiltScaffoldContents) -> list[Finding]:
    if not contents.skills_dir_present:
        return [Finding(Severity.FAIL, "Skills directory missing")]
    findings: list[Finding] = []
    for skill in contents.skills:
        findings.extend(_one_skill_findings(skill))
    return findings


def _one_skill_findings(skill: SkillPresence) -> list[Finding]:
    if skill.skill_md_text is None:
        return [Finding(Severity.FAIL, f"Skill {skill.name!r} missing SKILL.md")]
    try:
        frontmatter = skill_frontmatter_in(skill.skill_md_text)
    except ValueError as e:
        return [Finding(Severity.FAIL, f"Skill {skill.name!r}: {e}")]
    findings: list[Finding] = []
    if "name" not in frontmatter:
        findings.append(Finding(Severity.FAIL, f"Skill {skill.name!r} SKILL.md missing 'name'"))
    if "description" not in frontmatter:
        findings.append(
            Finding(Severity.FAIL, f"Skill {skill.name!r} SKILL.md missing 'description'")
        )
    return findings


def _data_directory_findings(contents: BuiltScaffoldContents) -> list[Finding]:
    if not contents.data_dir_present:
        return [Finding(Severity.WARN, "Data Files directory .vaudeville/ missing")]
    return []


def _skill_drift_findings(
    contents: BuiltScaffoldContents, reference: BuiltScaffoldContents
) -> list[Finding]:
    subject_names = {skill.name for skill in contents.skills}
    reference_names = {skill.name for skill in reference.skills}
    findings: list[Finding] = []
    for missing in sorted(reference_names - subject_names):
        findings.append(
            Finding(Severity.REMOVED, f"Skill {missing!r} present in reference but missing here")
        )
    for added in sorted(subject_names - reference_names):
        findings.append(
            Finding(Severity.ADDED, f"Skill {added!r} present here but missing from reference")
        )
    return findings


def skill_frontmatter_in(skill_md_text: str) -> dict[str, Any]:
    if not skill_md_text.startswith("---\n"):
        raise ValueError("SKILL.md missing frontmatter")
    end = skill_md_text.find("\n---", 4)
    if end == -1:
        raise ValueError("SKILL.md frontmatter is unterminated")
    block = skill_md_text[4:end]
    try:
        loaded = yaml.safe_load(block)
    except yaml.YAMLError as e:
        raise ValueError(f"SKILL.md frontmatter is not parseable YAML: {e}") from e
    if not isinstance(loaded, dict):
        raise ValueError("SKILL.md frontmatter is not a mapping")
    return loaded


def built_scaffold_contents_at(built_scaffold: Path) -> BuiltScaffoldContents:
    skills_dir = built_scaffold / "skills"
    skills_dir_present = skills_dir.is_dir()
    skills = (
        tuple(_skill_presence_at(entry) for entry in sorted(skills_dir.iterdir()) if entry.is_dir())
        if skills_dir_present
        else ()
    )
    return BuiltScaffoldContents(
        present_facade_executables=frozenset(
            name for name in _FACADE_EXECUTABLES if (built_scaffold / "bin" / name).is_file()
        ),
        skills_dir_present=skills_dir_present,
        skills=skills,
        data_dir_present=(built_scaffold / ".vaudeville").is_dir(),
    )


def _skill_presence_at(skill_dir: Path) -> SkillPresence:
    skill_md = skill_dir / "SKILL.md"
    return SkillPresence(
        name=skill_dir.name,
        skill_md_text=skill_md.read_text() if skill_md.is_file() else None,
    )
