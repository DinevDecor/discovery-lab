"""Opportunity Detector. Every result is DRAFT and evidence-cited;
none is ever auto-approved, escalated, or acted on — Headquarters is
advisory only (see CONTRACT.md). v1.0 implements three mechanical,
low-overreach heuristics rather than a larger, fuzzier set; each is
named honestly as a candidate for a human to consider, not a claim
that the opportunity is definitely worth taking."""

from __future__ import annotations

from pathlib import Path

from .collector import Collected
from .config import HeadquartersConfig
from .models import Confidence, Evidence, Finding


def shared_safety_pattern(config: HeadquartersConfig) -> list[Finding]:
    """Both observation-agent and headquarters implement their own
    static write/commit/push/subprocess-detection safety scanner
    (tests/test_safety.py). Real duplication, cheaply verifiable by
    checking both files exist."""
    dl = config.repo_by_name("discovery-lab")
    if not dl:
        return []
    base = Path(dl.path)
    oa_safety = base / "observation-agent" / "tests" / "test_safety.py"
    hq_safety = base / "headquarters" / "tests" / "test_safety.py"
    if oa_safety.is_file() and hq_safety.is_file():
        return [
            Finding(
                finding_id="opportunity-shared-safety-scanner",
                category="reusable_component",
                title="Extract the shared safety scanner used by both tools",
                description=(
                    "observation-agent and headquarters each maintain their own "
                    "copy of a static forbidden-pattern / write-mode scanner "
                    "(same forbidden-pattern list, same self-check discipline). "
                    "DRAFT candidate: factor the detector into a small shared "
                    "module both tools' test suites import, rather than two "
                    "independently-maintained copies drifting apart over time."
                ),
                confidence=Confidence.INSUFFICIENT_EVIDENCE,
                evidence=[
                    Evidence("discovery-lab", str(oa_safety.relative_to(base))),
                    Evidence("discovery-lab", str(hq_safety.relative_to(base))),
                ],
                affected=["discovery-lab"],
                is_opportunity=True,
            )
        ]
    return []


def registry_consolidation(collected: Collected) -> list[Finding]:
    """More than one non-project-level registry exists with no
    cross-index between them (kod: PRINCIPLE_REGISTRY + IDEA_REGISTRY;
    discovery-lab: ORB-REGISTRY + EMPLOYEE-REGISTRY + MEMORY-SOURCE
    registry). Not a defect — just an opportunity to consider."""
    known_registries = {
        "kod": ["Knowledge/PRINCIPLE_REGISTRY.md", "Knowledge/IDEA_REGISTRY.md"],
        "discovery-lab": [
            "docs/ai-organization/ORB/ORB-REGISTRY.md",
            "docs/ai-organization/EMPLOYEE-REGISTRY.md",
        ],
    }
    findings: list[Finding] = []
    for repo_name, paths in known_registries.items():
        snap = collected.repos.get(repo_name)
        if not snap:
            continue
        existing = [p for p in paths if (Path(snap.path) / p).is_file()]
        if len(existing) >= 2:
            findings.append(
                Finding(
                    finding_id=f"opportunity-registry-index-{repo_name}",
                    category="workflow_consolidation",
                    title=f"{repo_name} maintains {len(existing)} separate registries with no cross-index",
                    description=(
                        f"{repo_name} has {len(existing)} distinct registry files "
                        f"({', '.join(existing)}) with no single index pointing "
                        "between them. DRAFT candidate: a lightweight index page, "
                        "at the repository's own maintainers' discretion."
                    ),
                    confidence=Confidence.INSUFFICIENT_EVIDENCE,
                    evidence=[Evidence(repo_name, p) for p in existing],
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
