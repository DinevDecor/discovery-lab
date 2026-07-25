"""Shared data model. Mirrors observation-agent's evidence discipline
(every claim cites where it came from) but is a separate package on
purpose — Headquarters interprets evidence, it does not re-derive it,
and keeping the two packages independent keeps that boundary real
rather than aspirational."""

from __future__ import annotations

from dataclasses import dataclass, field


class Confidence:
    MATCH = "MATCH"
    MISMATCH = "MISMATCH"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


@dataclass
class Evidence:
    source: str
    detail: str

    def citation(self) -> str:
        return f"{self.source} — {self.detail}"


@dataclass
class HealthMetric:
    name: str
    value: str
    formula: str
    evidence: list[Evidence] = field(default_factory=list)


@dataclass
class PortfolioEntry:
    name: str
    purpose: str
    current_state: str
    trend: str
    dependencies: str
    last_meaningful_progress: str
    risk_level: str
    confidence: str
    health_score: str
    evidence: list[Evidence] = field(default_factory=list)


@dataclass
class Finding:
    """Shared shape for Drift findings and Opportunities."""
    finding_id: str
    category: str
    title: str
    description: str
    confidence: str
    evidence: list[Evidence]
    affected: list[str]
    is_opportunity: bool = False


@dataclass
class Recommendation:
    hq_id: str
    title: str
    reason: str
    evidence: list[Evidence]
    reasoning: str
    expected_impact: str
    dependencies: str
    estimated_confidence: str
    estimated_risk: str
    score: int
    score_breakdown: list[str]
    status: str = "proposed"
    source_finding_id: str | None = None
