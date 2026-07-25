"""Inconsistency classification (EXEC-004 Additional Execution
Directive). Whenever a Drift finding surfaces a real inconsistency,
Headquarters does not silently fix it and does not modify anything —
it records and classifies it into one of five categories, each with
the artifact affected, the observed evidence, its operational impact,
and a recommended future action. Opportunities are not classified
here: they are positive, optional suggestions, not inconsistencies —
this module only ever processes Drift findings.

The mapping from a Drift check to a category is a judgment call, made
once, here, and documented — not re-derived per run. `Implementation
Issue` has no current check mapping to it in v1.0 (see README); it
stays in the taxonomy because a future check might reasonably produce
one, not because this run invented an example to fill the category.
"""

from __future__ import annotations

from dataclasses import dataclass

from .models import Evidence, Finding


class Category:
    IMPLEMENTATION_ISSUE = "Implementation Issue"
    DOCUMENTATION_ISSUE = "Documentation Issue"
    GOVERNANCE_ISSUE = "Governance Issue"
    DATA_QUALITY_ISSUE = "Data Quality Issue"
    UNKNOWN = "Unknown"


# finding.category -> (taxonomy category, why)
_CATEGORY_MAP: dict[str, tuple[str, str]] = {
    "duplicated_infrastructure": (
        Category.GOVERNANCE_ISSUE,
        "An ADR records a governance decision; two files claiming the same ID is a decision-record integrity problem, not a code defect.",
    ),
    "stale_specification": (
        Category.DOCUMENTATION_ISSUE,
        "A specification document's own freshness is in question — a documentation-currency concern, not a governance or implementation one.",
    ),
    "governance_inconsistency": (
        Category.GOVERNANCE_ISSUE,
        "The ecosystem's own governance registry does not reflect reality.",
    ),
    "decision_backlog": (
        Category.GOVERNANCE_ISSUE,
        "A proposed recommendation awaiting a destination repository's own governance decision.",
    ),
    "possibly_abandoned_initiative": (
        Category.UNKNOWN,
        "A missing name-check in STATE.md cannot distinguish 'abandoned' from 'finished and folded into later work without a mention' — genuinely unknown from this evidence alone.",
    ),
    "data_quality": (
        Category.DATA_QUALITY_ISSUE,
        "A configured artifact exists but does not parse into the shape this ecosystem's own tooling expects from it.",
    ),
}

_IMPACT_TEMPLATES: dict[str, str] = {
    "duplicated_infrastructure": "Any reference to this ADR ID is ambiguous — a reader or tool cannot tell which decision is meant.",
    "stale_specification": "Reduced confidence that this document reflects the repository's current state; not confirmed stale, only old by one weak signal.",
    "governance_inconsistency": "This repository's real status is invisible to anyone consulting the ecosystem's own registry of record.",
    "decision_backlog": "The Recommendation Ledger's own acceptance_rate metric cannot move past 'undefined' while this stays undecided.",
    "possibly_abandoned_initiative": "Ambiguous: no operational impact if the initiative genuinely finished; a real information gap if it did not.",
    "data_quality": "Every Headquarters metric or Portfolio field that depends on this artifact degrades to INSUFFICIENT_EVIDENCE rather than a real value.",
}

_ACTION_TEMPLATES: dict[str, str] = {
    "duplicated_infrastructure": "A human familiar with this repository should rename or renumber one of the colliding files.",
    "stale_specification": "A human should confirm whether the document is genuinely current before treating its age as meaningful.",
    "governance_inconsistency": "A human with authority over the registry should add or correct the missing entry.",
    "decision_backlog": "The destination repository's own maintainers should record an explicit accept/reject decision.",
    "possibly_abandoned_initiative": "A human familiar with this initiative's history should confirm its real status and update STATE.md if it is in fact finished.",
    "data_quality": "A human should inspect the artifact directly and either fix its shape or confirm it is intentionally different from what this tool expects.",
}


@dataclass
class Inconsistency:
    category: str
    category_rationale: str
    affected_artifact: str
    observed_evidence: list[Evidence]
    operational_impact: str
    recommended_future_action: str
    finding_id: str
    title: str


def classify(finding: Finding) -> Inconsistency:
    category, rationale = _CATEGORY_MAP.get(finding.category, (Category.UNKNOWN, "No mapping exists yet for this check's category — reported as Unknown rather than guessed."))
    impact = _IMPACT_TEMPLATES.get(finding.category, "Not yet characterized for this check category.")
    action = _ACTION_TEMPLATES.get(finding.category, "A human should review this finding directly; no default action is defined for its category.")
    return Inconsistency(
        category=category,
        category_rationale=rationale,
        affected_artifact=", ".join(finding.affected) or "(unspecified)",
        observed_evidence=finding.evidence,
        operational_impact=impact,
        recommended_future_action=action,
        finding_id=finding.finding_id,
        title=finding.title,
    )


def classify_all(drift_findings: list[Finding]) -> list[Inconsistency]:
    """Drift findings only — Opportunities are never classified as
    inconsistencies (see module docstring)."""
    return [classify(f) for f in drift_findings if not f.is_opportunity]
