"""Opportunity Detector. Every result is DRAFT and evidence-cited;
none is ever auto-approved, escalated, or acted on — Headquarters is
advisory only (see CONTRACT.md). v1.0 implements three mechanical,
low-overreach heuristics rather than a larger, fuzzier set; each is
named honestly as a candidate for a human to consider, not a claim
that the opportunity is definitely worth taking.

Per the Additional Execution Directive's Robustness Requirement
("new repositories, agents, registries and documents should be
discoverable with minimal Headquarters changes"), the two heuristics
below that used to hard-code specific repo/file names now discover
their targets by a bounded, shallow filename-pattern search instead —
a new repo or a new registry file needs a `config.json` entry, never
a code change, to be picked up here. This is still narrower than
Observation Agent's own deep content scanning: these searches only
ever match file *names* against a fixed pattern, within a small,
excluded-dir-aware depth bound — they never read or interpret file
content the way a repository-scanning check would."""

from __future__ import annotations

import re
from pathlib import Path

from .collector import Collected
from .config import HeadquartersConfig
from .models import Confidence, Evidence, Finding

_EXCLUDED_DIRS = {".git", "__pycache__", "node_modules", ".venv"}
_MAX_DEPTH = 4
_REGISTRY_NAME = re.compile(r"registry", re.IGNORECASE)


def _bounded_walk(root: Path, max_depth: int):
    """Yield files under `root` up to `max_depth` directory levels
    deep, skipping known-noise directories. Bounded and shallow on
    purpose — a discovery aid, not a general repository scanner."""
    if not root.is_dir():
        return
    stack: list[tuple[Path, int]] = [(root, 0)]
    while stack:
        current, depth = stack.pop()
        try:
            entries = list(current.iterdir())
        except OSError:
            continue
        for entry in entries:
            if entry.is_dir():
                if entry.name in _EXCLUDED_DIRS or depth + 1 > max_depth:
                    continue
                stack.append((entry, depth + 1))
            elif entry.is_file():
                yield entry


def discover_registry_files(repo_root: Path) -> list[Path]:
    """Any `.md` file whose name contains "registry" (case-insensitive),
    found within a bounded, shallow walk of the repository."""
    return sorted(
        p for p in _bounded_walk(repo_root, _MAX_DEPTH)
        if p.suffix == ".md" and _REGISTRY_NAME.search(p.name)
    )


def discover_safety_scanners(config: HeadquartersConfig) -> list[tuple[str, Path]]:
    """Any `tests/test_safety.py` file one level below a top-level
    subdirectory of each configured repo — matches the
    `<tool>/tests/test_safety.py` shape both observation-agent and
    headquarters use, without naming either tool specifically."""
    found: list[tuple[str, Path]] = []
    for repo in config.repos:
        root = Path(repo.path)
        if not root.is_dir():
            continue
        for match in sorted(root.glob("*/tests/test_safety.py")):
            found.append((repo.name, match))
    return found


def shared_safety_pattern(config: HeadquartersConfig) -> list[Finding]:
    """More than one `<tool>/tests/test_safety.py` exists anywhere in
    the configured repos — real duplication of the same static
    forbidden-pattern / write-mode scanner, discovered generically
    rather than by naming observation-agent and headquarters directly."""
    matches = discover_safety_scanners(config)
    if len(matches) < 2:
        return []
    affected = sorted({repo_name for repo_name, _ in matches})
    evidence = [
        Evidence(repo_name, str(path.relative_to(Path(config.repo_by_name(repo_name).path))))
        for repo_name, path in matches
    ]
    return [
        Finding(
            finding_id="opportunity-shared-safety-scanner",
            category="reusable_component",
            title=f"{len(matches)} tools each maintain their own copy of a safety scanner",
            description=(
                "Each `<tool>/tests/test_safety.py` found implements the same "
                "static forbidden-pattern / write-mode detector independently "
                "(same forbidden-pattern list, same self-check discipline). "
                "DRAFT candidate: factor the detector into a small shared "
                "module every tool's test suite imports, rather than "
                "independently-maintained copies drifting apart over time."
            ),
            confidence=Confidence.INSUFFICIENT_EVIDENCE,
            evidence=evidence,
            affected=affected,
            is_opportunity=True,
        )
    ]


def registry_consolidation(collected: Collected) -> list[Finding]:
    """A repository has 2+ files whose name matches "*registry*.md",
    discovered generically rather than from a hard-coded per-repo
    list, with no single index pointing between them. Not a defect —
    just an opportunity to consider."""
    findings: list[Finding] = []
    for repo_name, snap in collected.repos.items():
        matches = discover_registry_files(Path(snap.path))
        if len(matches) >= 2:
            rel_paths = [str(p.relative_to(Path(snap.path))) for p in matches]
            findings.append(
                Finding(
                    finding_id=f"opportunity-registry-index-{repo_name}",
                    category="workflow_consolidation",
                    title=f"{repo_name} maintains {len(matches)} separate registries with no cross-index",
                    description=(
                        f"{repo_name} has {len(matches)} files matching "
                        f"'*registry*.md' ({', '.join(rel_paths)}) with no single "
                        "index pointing between them. DRAFT candidate: a "
                        "lightweight index page, at the repository's own "
                        "maintainers' discretion."
                    ),
                    confidence=Confidence.INSUFFICIENT_EVIDENCE,
                    evidence=[Evidence(repo_name, p) for p in rel_paths],
                    affected=[repo_name],
                    is_opportunity=True,
                )
            )
    return findings


def changelog_size_signal(collected: Collected) -> list[Finding]:
    """A single-file CHANGELOG.md that has grown very large is a
    readability opportunity, not a defect. Threshold (1000 lines) is
    arbitrary but stated plainly as such."""
    threshold = 1000
    findings: list[Finding] = []
    for repo_name, snap in collected.repos.items():
        if snap.changelog_lines and snap.changelog_lines > threshold:
            findings.append(
                Finding(
                    finding_id=f"opportunity-changelog-size-{repo_name}",
                    category="architectural_simplification",
                    title=f"{repo_name}/CHANGELOG.md is {snap.changelog_lines} lines",
                    description=(
                        f"Exceeds this check's arbitrary {threshold}-line readability "
                        "threshold. DRAFT candidate: consider splitting by year or "
                        "quarter, at the repository's own maintainers' discretion — "
                        "this is a readability suggestion, not a claim anything is wrong."
                    ),
                    confidence=Confidence.INSUFFICIENT_EVIDENCE,
                    evidence=[Evidence(repo_name, f"CHANGELOG.md: {snap.changelog_lines} lines")],
                    affected=[repo_name],
                    is_opportunity=True,
                )
            )
    return findings


def detect_opportunities(collected: Collected, config: HeadquartersConfig) -> list[Finding]:
    findings: list[Finding] = []
    findings += shared_safety_pattern(config)
    findings += registry_consolidation(collected)
    findings += changelog_size_signal(collected)
    return findings
