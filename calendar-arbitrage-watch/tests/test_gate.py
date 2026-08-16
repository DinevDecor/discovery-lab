"""Adversarial review outcomes are always returned as a persisted decision
(CLAUDE.md: 'All gate outcomes persist').

Corrected 2026-08-15-6 (approved gate-policy decision): both defensive
gaps being INSUFFICIENT_DATA is a data-completeness state, not a
falsification, so it is an ordinary CHALLENGED reason - never KILLED.
REVIEW_KILLED/REJECTED stays available as the terminal path for a future
genuine falsification rule, but no rule in gate.py produces it today;
see test_gate_insufficient_vs_falsification.py for the direct coverage
of that contract (INSUFFICIENT_DATA != falsified, and REJECTED still
behaves as terminal when a KILLED decision IS supplied).
"""

import _pathsetup  # noqa: F401
import unittest

from calendar_arbitrage_watch import gate
from calendar_arbitrage_watch.models import (
    CalendarAssessment, DateBound, DefensiveGapAssessment, DemandProfile, DISCOVERY,
    MAX_AUTOMATIC_STATES, NumberClaim, ReadinessAssessment, MEASURED, OBSERVED, REPEATED,
    REVIEW_CHALLENGED, REVIEW_CONFIRMED, REVIEW_KILLED, START_CLOCK_CANDIDATE,
)


def _base_assessment(**overrides) -> CalendarAssessment:
    a = CalendarAssessment(
        candidate_id="cand-1",
        mode=DISCOVERY,
        category="regulatory_clock",
        title="Test",
        readiness=ReadinessAssessment(g_r_days=NumberClaim(value=30, provenance=MEASURED, evidence_status=OBSERVED)),
        defensive=DefensiveGapAssessment(
            g_d_novo_days=NumberClaim(value=20, provenance=MEASURED, evidence_status=OBSERVED),
            g_d_active_days=NumberClaim(value=15, provenance=MEASURED, evidence_status=OBSERVED),
        ),
        demand=DemandProfile(demand_obligation_certainty=NumberClaim(value=0.9, evidence_status=OBSERVED)),
    )
    for k, v in overrides.items():
        setattr(a, k, v)
    return a


class GateTests(unittest.TestCase):
    def test_confirmed_when_no_red_flags(self):
        a = _base_assessment()
        decision = gate.review(a)
        self.assertEqual(decision.outcome, REVIEW_CONFIRMED)
        self.assertEqual(decision.max_allowed_state, START_CLOCK_CANDIDATE)

    def test_confirmed_ceiling_is_buy_calendar_candidate_for_archaeology_mode(self):
        a = _base_assessment(mode="ARCHAEOLOGY")
        decision = gate.review(a)
        self.assertEqual(decision.outcome, REVIEW_CONFIRMED)
        self.assertEqual(decision.max_allowed_state, "BUY_CALENDAR_CANDIDATE")

    def test_challenged_when_g_r_insufficient_data(self):
        a = _base_assessment(readiness=ReadinessAssessment())  # g_r_days defaults to INSUFFICIENT_DATA
        decision = gate.review(a)
        self.assertEqual(decision.outcome, REVIEW_CHALLENGED)
        self.assertEqual(decision.max_allowed_state, "WATCH")

    def test_challenged_when_demand_certainty_missing(self):
        a = _base_assessment(demand=DemandProfile())
        decision = gate.review(a)
        self.assertEqual(decision.outcome, REVIEW_CHALLENGED)

    def test_challenged_when_key_number_is_only_repeated(self):
        a = _base_assessment(readiness=ReadinessAssessment(
            g_r_days=NumberClaim(value=30, provenance=REPEATED, evidence_status=OBSERVED)))
        decision = gate.review(a)
        self.assertEqual(decision.outcome, REVIEW_CHALLENGED)
        self.assertTrue(any("REPEATED" in r for r in decision.reasons))

    def test_challenged_not_killed_when_both_defensive_gaps_missing(self):
        """Corrected 2026-08-15-6: missing evidence caps at WATCH via
        CHALLENGED - it must never terminally REJECT the candidate."""
        a = _base_assessment(defensive=DefensiveGapAssessment())
        decision = gate.review(a)
        self.assertEqual(decision.outcome, REVIEW_CHALLENGED)
        self.assertEqual(decision.max_allowed_state, "WATCH")

    def test_both_gaps_missing_reason_does_not_claim_no_evidence_was_asserted(self):
        """The old wording ('no competitive picture asserted') was wrong
        whenever a submission actually supplied structured competitor
        evidence that simply hadn't been derived yet (REAL-CASE-001). The
        corrected wording only claims absence of a quantitative result."""
        a = _base_assessment(defensive=DefensiveGapAssessment())
        decision = gate.review(a)
        self.assertTrue(any("cannot yet be quantitatively assessed" in r for r in decision.reasons))
        self.assertFalse(any("no competitive picture asserted" in r for r in decision.reasons))

    def test_decision_reasons_are_never_empty(self):
        """Even CONFIRMED must record why - a refused promotion or an
        unremarkable pass are both information worth keeping."""
        for a in (_base_assessment(), _base_assessment(readiness=ReadinessAssessment()),
                  _base_assessment(defensive=DefensiveGapAssessment())):
            decision = gate.review(a)
            self.assertTrue(decision.reasons)

    def test_confirmed_and_challenged_are_both_reachable(self):
        outcomes = {
            gate.review(_base_assessment()).outcome,
            gate.review(_base_assessment(readiness=ReadinessAssessment())).outcome,
            gate.review(_base_assessment(defensive=DefensiveGapAssessment())).outcome,
        }
        self.assertEqual(outcomes, {REVIEW_CONFIRMED, REVIEW_CHALLENGED})

    def test_killed_is_not_produced_by_any_current_rule(self):
        """Accepted consequence of the 2026-08-15-6 correction: no rule
        in gate.py fabricates a kill just to keep REVIEW_KILLED reachable.
        The outcome and its terminal lifecycle handling remain available
        (see test_gate_insufficient_vs_falsification.py) for the next
        rule that has a real falsification case to encode."""
        scenarios = [
            _base_assessment(),
            _base_assessment(readiness=ReadinessAssessment()),
            _base_assessment(demand=DemandProfile()),
            _base_assessment(defensive=DefensiveGapAssessment()),
            _base_assessment(readiness=ReadinessAssessment(), demand=DemandProfile(),
                              defensive=DefensiveGapAssessment()),
        ]
        for a in scenarios:
            self.assertNotEqual(gate.review(a).outcome, REVIEW_KILLED)


if __name__ == "__main__":
    unittest.main()
