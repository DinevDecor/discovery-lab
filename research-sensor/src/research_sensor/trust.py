"""Trust Policy (EXEC-010): "Confidence depends on: publication
quality, peer review status, independent replication, evidence
strength. Never on popularity." Independently reimplemented pattern -
similar shape to reality-sensor/src/reality_sensor/trust.py, tailored
to this domain's own evidence-level vocabulary rather than shared code.
"""

from __future__ import annotations

from .models import Confidence, EvidenceLevel

# Evidence levels strong enough to support HIGH confidence on their own.
_HIGH_CONFIDENCE_LEVELS = {
    EvidenceLevel.PEER_REVIEWED_PUBLISHED,
    EvidenceLevel.PEER_REVIEWED_ACCEPTED,
}


def assess_confidence(evidence_levels: list[str], corroborating_count: int) -> str:
    """Confidence depends only on the strongest evidence_level actually
    attached to a signal, and how many independent citations support
    it - never on which source is loudest or most numerous beyond that.
    `corroborating_count` is the number of DISTINCT evidence_levels at
    NOTABLE_LAB_PREPRINT or better supporting the same idea - this is
    the "independent replication" input the rule names, approximated
    as "more than one independent notable source agrees", not a claim
    about experimental replication of results."""
    if not evidence_levels:
        return Confidence.INSUFFICIENT_EVIDENCE

    # EXEC-010's own Trust Policy for Sources: "COMMUNITY only as
    # discovery hints." A signal whose evidence is COMMUNITY_HINT-only
    # can never be accepted at all - stricter than "capped at LOW":
    # this is enforced upstream (registry.py forces such a cluster to
    # WATCH before a Signal is even built) precisely because a
    # discovery hint is not citable evidence, not merely weak evidence.
    non_hint_levels = [
        e for e in evidence_levels
        if e not in (EvidenceLevel.COMMUNITY_HINT, EvidenceLevel.UNKNOWN)
    ]
    if not non_hint_levels:
        return Confidence.INSUFFICIENT_EVIDENCE

    if any(e in _HIGH_CONFIDENCE_LEVELS for e in non_hint_levels):
        return Confidence.HIGH

    if EvidenceLevel.NOTABLE_LAB_PREPRINT in non_hint_levels and corroborating_count >= 2:
        # Independent replication proxy: more than one distinct
        # notable-lab source converging on the same idea.
        return Confidence.HIGH

    if EvidenceLevel.NOTABLE_LAB_PREPRINT in non_hint_levels:
        return Confidence.MEDIUM

    if EvidenceLevel.PREPRINT in non_hint_levels:
        return Confidence.LOW

    return Confidence.LOW


def can_accept_signal(evidence_levels: list[str]) -> bool:
    """EXEC-010's Most Important Rule, applied structurally: a cluster
    whose only evidence is COMMUNITY_HINT can never become an accepted
    ResearchSignal - it stays a discovery hint, never a citable claim.
    Callers (registry.py) route such clusters to WATCH instead of
    building a Signal at all."""
    non_hint = [
        e for e in evidence_levels
        if e not in (EvidenceLevel.COMMUNITY_HINT, EvidenceLevel.UNKNOWN)
    ]
    return len(non_hint) > 0
