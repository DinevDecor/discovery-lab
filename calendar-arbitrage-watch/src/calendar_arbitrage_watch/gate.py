"""Adversarial review pass over one candidate's assessment.

Shape note: ca_agents.same_mechanism_gate.GateDecision reviews a PAIR of
anomalies (same mechanism or not). Calendar Arbitrage does not have an
equivalent pairwise-merge question in its minimal 30-day watch, so this
gate instead reviews ONE candidate's own assessment against structural
red flags and produces one of three outcomes - CONFIRMED / CHALLENGED /
KILLED - all three ALWAYS persisted (CLAUDE.md: "All gate outcomes
persist... A refused merge is the most informative output the pipeline
has produced so far" - applied here to "a refused promotion").

The review is deliberately structural/deterministic by default. An LLM
MAY be plugged in later as a second opinion (see JudgeProtocol below,
mirroring ca_agents.same_mechanism_gate.JudgeProtocol) but this module
never imports a model client itself, and this package makes no network
call in this phase (2026-08-15 approval, point 3). Whatever a future
judge returns is advisory critique, never itself evidence, and it can
only ever push a decision toward CHALLENGED/KILLED - never manufacture a
CONFIRMED past what the structural checks already allow.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Protocol

from .models import (
    CalendarAssessment,
    INSUFFICIENT_DATA,
    MAX_AUTOMATIC_STATES,
    REPEATED,
    REVIEW_CHALLENGED,
    REVIEW_CONFIRMED,
    REVIEW_KILLED,
)

GATE_VERSION = "0.1.0"


class JudgeProtocol(Protocol):
    """Optional future extension point, unused by default. Mirrors
    ca_agents.same_mechanism_gate.JudgeProtocol's shape so a real
    implementation (if ever wired) follows an established pattern rather
    than inventing a new one. Not imported or called anywhere in this
    package today."""
    def critique(self, assessment: CalendarAssessment) -> dict: ...


@dataclass(frozen=True)
class ReviewDecision:
    candidate_id: str
    outcome: str  # REVIEW_CONFIRMED | REVIEW_CHALLENGED | REVIEW_KILLED
    reasons: List[str]
    max_allowed_state: str
    gate_version: str = GATE_VERSION

    def to_dict(self) -> dict:
        return {
            "candidate_id": self.candidate_id,
            "outcome": self.outcome,
            "reasons": list(self.reasons),
            "max_allowed_state": self.max_allowed_state,
            "gate_version": self.gate_version,
        }


def review(assessment: CalendarAssessment) -> ReviewDecision:
    """Structural adversarial review. Every check either allows or caps
    the candidate's max_allowed_state; the review never itself sets
    lifecycle_state - that stays lifecycle.py's job, using this decision
    as one input.
    """
    reasons: List[str] = []
    kill_reasons: List[str] = []

    g_r = assessment.readiness.g_r_days
    g_d_novo = assessment.defensive.g_d_novo_days
    g_d_active = assessment.defensive.g_d_active_days
    doc = assessment.demand.demand_obligation_certainty

    # Rule 1: a candidate cannot be proposed past WATCH with an
    # INSUFFICIENT_DATA readiness gap - there is nothing to defend.
    if g_r.evidence_status == INSUFFICIENT_DATA:
        reasons.append("G_r is INSUFFICIENT_DATA - cannot support any state above WATCH")

    # Rule 2: demand obligation certainty missing caps at WATCH - a
    # calendar position defended by nothing but an unverified obligation
    # is not a candidate yet.
    if doc.evidence_status == INSUFFICIENT_DATA:
        reasons.append("demand_obligation_certainty is INSUFFICIENT_DATA - cannot support any state above WATCH")

    # Rule 3: independently-adopted S1 discipline (see models.py
    # NUMBER_PROVENANCE docstring) - a key number that is only REPEATED,
    # never independently MEASURED, cannot alone support a MAX_AUTOMATIC
    # state.
    repeated_only = [
        name for name, claim in (("G_r", g_r), ("G_d^novo", g_d_novo), ("G_d^active", g_d_active))
        if claim.evidence_status != INSUFFICIENT_DATA and claim.provenance == REPEATED
    ]
    if repeated_only:
        reasons.append(
            f"{', '.join(repeated_only)} carries only REPEATED provenance, not independently MEASURED - "
            "cannot alone support promotion to a MAX_AUTOMATIC state without independent verification")

    # Rule 4: both defensive gaps missing at once means the candidate has
    # no stated competitive picture at all.
    if g_d_novo.evidence_status == INSUFFICIENT_DATA and g_d_active.evidence_status == INSUFFICIENT_DATA:
        kill_reasons.append("both G_d^novo and G_d^active are INSUFFICIENT_DATA - no competitive picture asserted")

    if kill_reasons:
        return ReviewDecision(assessment.candidate_id, REVIEW_KILLED, kill_reasons + reasons, "REJECTED")
    if reasons:
        return ReviewDecision(assessment.candidate_id, REVIEW_CHALLENGED, reasons, "WATCH")
    return ReviewDecision(assessment.candidate_id, REVIEW_CONFIRMED, ["no structural red flags found"],
                           MAX_AUTOMATIC_STATES[0] if assessment.mode != "ARCHAEOLOGY" else MAX_AUTOMATIC_STATES[1])
