"""Approved gate-policy correction (2026-08-15-6): INSUFFICIENT_DATA on
both defensive gaps means the competitive position is not yet
quantitatively assessable - it must never be treated as falsification.

Before this correction, that condition produced REVIEW_KILLED ->
REJECTED, and REJECTED is terminal (lifecycle.apply_review never revives
it) - so missing evidence could become an irreversible negative verdict,
exactly what REAL-CASE-001 hit. The fix keeps things deliberately small:
reuse the existing REVIEW_CHALLENGED outcome for this case (no new
REVIEW_INSUFFICIENT outcome, no new lifecycle state), and leave
REVIEW_KILLED -> REJECTED's terminal handling completely intact for
whichever future rule has a genuine falsification case to encode.

This file is the direct regression coverage for that contract, end to
end through both gate.review() and lifecycle.apply_review() together -
test_gate.py covers gate.review() in isolation.
"""

import _pathsetup  # noqa: F401
import unittest

from calendar_arbitrage_watch import gate
from calendar_arbitrage_watch.lifecycle import apply_review
from calendar_arbitrage_watch.models import (
    CalendarAssessment, DefensiveGapAssessment, DemandProfile, DISCOVERY,
    CHEAP_TEST, MEASURED, NumberClaim, OBSERVED, REJECTED, REPEATED,
    ReadinessAssessment, REVIEW_CHALLENGED, REVIEW_CONFIRMED, REVIEW_KILLED, WATCH,
)


def _assessment_with_insufficient_defensive_gaps(**overrides) -> CalendarAssessment:
    a = CalendarAssessment(
        candidate_id="insufficient-vs-falsified-1",
        mode=DISCOVERY, category="regulatory_clock", title="Test",
        readiness=ReadinessAssessment(g_r_days=NumberClaim(value=30, provenance=MEASURED, evidence_status=OBSERVED)),
        defensive=DefensiveGapAssessment(),  # g_d_novo_days / g_d_active_days both default to INSUFFICIENT_DATA
        demand=DemandProfile(demand_obligation_certainty=NumberClaim(value=0.9, evidence_status=OBSERVED)),
    )
    for k, v in overrides.items():
        setattr(a, k, v)
    return a


def _assessment_with_sufficient_defensive_gaps(**overrides) -> CalendarAssessment:
    """Same candidate, a later revision where the competitive picture HAS
    become quantitatively assessable - real, independently MEASURED
    defensive-gap values now present."""
    a = _assessment_with_insufficient_defensive_gaps(**overrides)
    a.defensive = DefensiveGapAssessment(
        g_d_novo_days=NumberClaim(value=20, provenance=MEASURED, evidence_status=OBSERVED),
        g_d_active_days=NumberClaim(value=15, provenance=MEASURED, evidence_status=OBSERVED),
    )
    return a


class InsufficientDataIsNotFalsificationTests(unittest.TestCase):
    def test_1_both_gaps_insufficient_data_yields_challenged_not_killed(self):
        a = _assessment_with_insufficient_defensive_gaps()
        decision = gate.review(a)
        self.assertEqual(decision.outcome, REVIEW_CHALLENGED)
        self.assertNotEqual(decision.outcome, REVIEW_KILLED)

    def test_2_lifecycle_stays_at_watch_not_rejected(self):
        a = _assessment_with_insufficient_defensive_gaps(lifecycle_state=WATCH)
        decision = gate.review(a)
        new_state, reason = apply_review(a, decision)
        self.assertEqual(new_state, WATCH)
        self.assertNotEqual(new_state, REJECTED)
        self.assertIn("cannot yet be quantitatively assessed", reason)

    def test_3_a_later_revision_with_sufficient_evidence_can_be_promoted_normally(self):
        """The revivability this correction exists to prove: a candidate
        held at WATCH for lack of evidence is NOT stuck there forever -
        once a later revision supplies real defensive-gap evidence, the
        gate can CONFIRM it and lifecycle can advance it normally. Under
        the pre-correction behavior this was structurally impossible: the
        first round would have terminally REJECTED the candidate and
        apply_review refuses to revive a REJECTED candidate."""
        # Round 1: insufficient evidence -> CHALLENGED -> held at WATCH.
        v1 = _assessment_with_insufficient_defensive_gaps(lifecycle_state=WATCH)
        state_after_v1, _ = apply_review(v1, gate.review(v1))
        self.assertEqual(state_after_v1, WATCH)

        # Round 2 (same candidate_id, a later revision): real evidence now
        # exists. Carries forward the state round 1 actually reached.
        v2 = _assessment_with_sufficient_defensive_gaps(lifecycle_state=state_after_v1)
        decision_v2 = gate.review(v2)
        self.assertEqual(decision_v2.outcome, REVIEW_CONFIRMED)
        state_after_v2, reason_v2 = apply_review(v2, decision_v2)
        self.assertEqual(state_after_v2, CHEAP_TEST)  # WATCH -> CHEAP_TEST, a real promotion
        self.assertIn("CONFIRMED", reason_v2)

    def test_4_an_explicitly_supplied_killed_decision_still_maps_to_terminal_rejected(self):
        """REVIEW_KILLED -> REJECTED's terminal lifecycle semantics are
        completely unchanged by this correction - gate.review() simply
        doesn't produce KILLED today. A ReviewDecision carrying KILLED
        (as a future genuine falsification rule would produce) must still
        terminally reject, and REJECTED must still refuse to revive."""
        a = _assessment_with_insufficient_defensive_gaps(lifecycle_state=WATCH)
        synthetic_kill = gate.ReviewDecision(
            candidate_id=a.candidate_id, outcome=REVIEW_KILLED,
            reasons=["synthetic fatal-veto evidence for this regression test"],
            max_allowed_state="REJECTED",
        )
        new_state, reason = apply_review(a, synthetic_kill)
        self.assertEqual(new_state, REJECTED)
        self.assertIn("KILLED", reason)

        # Terminality: a REJECTED candidate does not revive even given a
        # subsequent CONFIRMED decision.
        rejected_assessment = _assessment_with_sufficient_defensive_gaps(lifecycle_state=REJECTED)
        confirmed_decision = gate.review(rejected_assessment)
        self.assertEqual(confirmed_decision.outcome, REVIEW_CONFIRMED)
        state_after, revival_reason = apply_review(rejected_assessment, confirmed_decision)
        self.assertEqual(state_after, REJECTED)
        self.assertIn("out of scope", revival_reason)


if __name__ == "__main__":
    unittest.main()
