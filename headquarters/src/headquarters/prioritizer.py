"""Attention Engine — Headquarters' primary responsibility. Selects
exactly one highest-value candidate, never a list. The scoring rubric
below is deliberately simple and fully shown in each recommendation's
own `score_breakdown`, so "why this and not that" is always inspectable
rather than a black box.

Guiding principle, operationalized directly in the weights: a
candidate that *finishes* something already in flight (a pending
decision, a mechanical fix) scores higher than a candidate that would
*start* something new (a DRAFT opportunity), which is why opportunities
carry a negative weight rather than merely a low positive one.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .collector import Collected, LedgerEntry
from .models import Confidence, Finding, Recommendation

_FINISHABLE_CATEGORIES = {"decision_backlog", "duplicated_infrastructure"}


@dataclass
class Candidate:
    key: str
    title: str
    description: str
    confidence: str
    affected: list[str]
    is_opportunity: bool
    category: str
    source: str  # "ledger" | "drift" | "opportunity"
    evidence: list = field(default_factory=list)
    ledger_fields: dict[str, str] | None = None


def _from_ledger(entries: list[LedgerEntry]) -> list[Candidate]:
    out = []
    for e in entries:
        if e.fields.get("status") != "PROPOSED":
            continue
        rec_id = e.fields.get("recommendation_id", "?")
        out.append(
            Candidate(
                key=f"ledger-{rec_id}",
                title=f"Deliver {rec_id} to {e.fields.get('destination_repository', '?')} for a decision",
                description=e.fields.get("summary", ""),
                confidence=Confidence.MISMATCH,
                affected=[e.fields.get("destination_repository", "?")],
                is_opportunity=False,
                category="pending_ledger_decision",
                source="ledger",
                evidence=[],
                ledger_fields=e.fields,
            )
        )
    return out


def _from_findings(findings: list[Finding]) -> list[Candidate]:
    out = []
    for f in findings:
        out.append(
            Candidate(
                key=f"finding-{f.finding_id}",
                title=f.title,
                description=f.description,
                confidence=f.confidence,
                affected=f.affected,
                is_opportunity=f.is_opportunity,
                category=f.category,
                source="opportunity" if f.is_opportunity else "drift",
                evidence=f.evidence,
            )
        )
    return out


def build_candidates(
    collected: Collected, drift_findings: list[Finding], opportunity_findings: list[Finding]
) -> list[Candidate]:
    return (
        _from_ledger(collected.ledger_entries)
        + _from_findings(drift_findings)
        + _from_findings(opportunity_findings)
    )


def score(candidate: Candidate) -> tuple[int, list[str]]:
    breakdown: list[str] = []
    total = 0

    if candidate.confidence == Confidence.MISMATCH:
        total += 3
        breakdown.append("+3 confirmed (MISMATCH-confidence evidence)")
    elif candidate.confidence == Confidence.INSUFFICIENT_EVIDENCE:
        total += 1
        breakdown.append("+1 real signal, not yet confirmed (INSUFFICIENT_EVIDENCE)")

    if candidate.category in _FINISHABLE_CATEGORIES:
        total += 2
        breakdown.append("+2 small/mechanical to finish (aligns with the guiding principle)")

    if candidate.category == "pending_ledger_decision" or candidate.category == "decision_backlog":
        total += 2
        breakdown.append("+2 unblocks the Recommendation Ledger's own acceptance_rate metric")

    breadth = min(len(set(candidate.affected)), 2)
    if breadth:
        total += breadth
        breakdown.append(f"+{breadth} breadth ({len(set(candidate.affected))} repo(s) affected, capped at 2)")

    if candidate.is_opportunity:
        total -= 1
        breakdown.append("-1 this is a new-work opportunity, not a finish-existing-work item")

    return total, breakdown


def select_top(candidates: list[Candidate]) -> tuple[Candidate, int, list[str]] | None:
    if not candidates:
        return None
    scored = [(c, *score(c)) for c in candidates]
    scored.sort(key=lambda t: (-t[1], t[0].key))
    top = scored[0]
    return top


def to_recommendation(candidate: Candidate, hq_id: str, score_value: int, breakdown: list[str]) -> Recommendation:
    """Turn the selected Candidate into the fully-explained
    Recommendation the Executive Brief renders — every field EXEC-004
    §11 requires (Evidence, Reasoning, Dependencies, Confidence,
    Expected Impact, Estimated Risk) is populated here, never left out."""
    if candidate.source == "ledger":
        f = candidate.ledger_fields or {}
        dependencies = f"Requires {f.get('destination_repository', 'the destination repository')}'s own maintainers to respond — Discovery Lab has no authority to decide this itself (Principle 0)."
        expected_impact = "Advances the Recommendation Ledger's acceptance_rate metric from its current undefined state toward a real, computable value."
        estimated_risk = "LOW — the action requested is a human decision, not a code or repository change."
    elif candidate.category == "duplicated_infrastructure":
        dependencies = "None outside the affected repository's own maintainers choosing which file to keep."
        expected_impact = "Removes a genuine ID collision so the ADR sequence in this repository is unambiguous again."
        estimated_risk = "LOW — a rename/removal of one duplicate file, not a design change."
    elif candidate.is_opportunity:
        dependencies = "None — this is a DRAFT suggestion only; taking it up is entirely optional and unscheduled."
        expected_impact = "Speculative — a possible future readability/maintenance improvement, not a current problem."
        estimated_risk = "N/A — no action is being recommended to take now, only to consider."
    else:
        dependencies = "See evidence citations for the specific artifact(s) this finding references."
        expected_impact = "Closes a real gap this run's evidence surfaced; impact is scoped to the affected repository/repositories."
        estimated_risk = "MEDIUM — INSUFFICIENT_EVIDENCE findings need human interpretation before the right fix is obvious." if candidate.confidence != Confidence.MISMATCH else "LOW-MEDIUM — mechanically confirmed, but the fix itself still needs human judgment."

    return Recommendation(
        hq_id=hq_id,
        title=candidate.title,
        reason=candidate.description[:280] or candidate.title,
        evidence=candidate.evidence,
        reasoning=" ".join(breakdown),
        expected_impact=expected_impact,
        dependencies=dependencies,
        estimated_confidence=candidate.confidence,
        estimated_risk=estimated_risk,
        score=score_value,
        score_breakdown=breakdown,
        source_finding_id=candidate.key,
    )
