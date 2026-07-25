"""Trust Policy (EXEC-008's Source Trust Levels + Confidence Rules).

The one hard rule EXEC-008 states explicitly: "Never assign HIGH
confidence from COMMUNITY alone." Everything below is the smallest,
most literal implementation of that rule plus the evidence-enforcement
rule implied by the Signal Model itself (a signal with zero evidence
cannot be anything but INSUFFICIENT_EVIDENCE) — no additional scoring
logic is invented beyond what EXEC-008 actually specifies.
"""

from __future__ import annotations

from .models import Confidence, TrustLevel, Urgency

# Trust levels strong enough to support HIGH confidence on their own.
_HIGH_CONFIDENCE_TRUST = {TrustLevel.PRIMARY, TrustLevel.OFFICIAL}


def assess_confidence(evidence_trust_levels: list[str]) -> str:
    """Confidence depends only on the trust levels of the evidence
    actually attached to a signal - never on how many articles repeat
    a claim, never on category, never on urgency."""
    if not evidence_trust_levels:
        return Confidence.INSUFFICIENT_EVIDENCE

    if any(t in _HIGH_CONFIDENCE_TRUST for t in evidence_trust_levels):
        return Confidence.HIGH

    if any(t == TrustLevel.RESEARCH for t in evidence_trust_levels):
        # A research paper alone is a real claim, not yet independently
        # corroborated by a primary/official source - MEDIUM, not HIGH.
        return Confidence.MEDIUM

    if any(t == TrustLevel.SECONDARY for t in evidence_trust_levels):
        return Confidence.MEDIUM

    if all(t == TrustLevel.COMMUNITY for t in evidence_trust_levels):
        # The literal rule EXEC-008 states: never HIGH from COMMUNITY alone.
        return Confidence.LOW

    # UNKNOWN-only evidence: cannot support more than LOW.
    return Confidence.LOW


# Keyword signals a human would recognize as "look at this soon" versus
# "fine to read in the weekly roundup" - transparent, documented, and
# the only inputs this function uses (mirrors the Attention Engine's
# own "fully shown, documented rubric" discipline in
# headquarters/src/headquarters/prioritizer.py).
_HIGH_URGENCY_KEYWORDS = (
    "deprecat",
    "sunset",
    "breaking change",
    "end of life",
    "security",
    "vulnerability",
    "shutdown",
)
_LOW_URGENCY_CATEGORY_HINTS = ("preprint", "workshop paper", "position paper")


def assess_urgency(category: str, confidence: str, summary_text: str) -> str:
    text = summary_text.lower()
    if any(kw in text for kw in _HIGH_URGENCY_KEYWORDS):
        return Urgency.HIGH
    if confidence == Confidence.INSUFFICIENT_EVIDENCE:
        return Urgency.LOW
    if any(hint in text for hint in _LOW_URGENCY_CATEGORY_HINTS):
        return Urgency.LOW
    if confidence == Confidence.HIGH:
        return Urgency.MEDIUM
    return Urgency.LOW
