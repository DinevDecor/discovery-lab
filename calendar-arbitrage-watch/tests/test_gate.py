"""All three adversarial review outcomes must be reachable and are always
returned as a persisted decision (CLAUDE.md: 'All gate outcomes
persist').
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

    def test_killed_when_both_defensive_gaps_missing(self):
        a = _base_assessment(defensive=DefensiveGapAssessment())
        decision = gate.review(a)
        self.assertEqual(decision.outcome, REVIEW_KILLED)
        self.assertEqual(decision.max_allowed_state, "REJECTED")

    def test_decision_reasons_are_never_empty(self):
        """Even CONFIRMED must record why - a refused promotion or an
        unremarkable pass are both information worth keeping."""
        for a in (_base_assessment(), _base_assessment(readiness=ReadinessAssessment()),
                  _base_assessment(defensive=DefensiveGapAssessment())):
            decision = gate.review(a)
            self.assertTrue(decision.reasons)

    def test_all_three_outcomes_are_reachable(self):
        outcomes = {
            gate.review(_base_assessment()).outcome,
            gate.review(_base_assessment(readiness=ReadinessAssessment())).outcome,
            gate.review(_base_assessment(defensive=DefensiveGapAssessment())).outcome,
        }
        self.assertEqual(outcomes, {REVIEW_CONFIRMED, REVIEW_CHALLENGED, REVIEW_KILLED})


if __name__ == "__main__":
    unittest.main()
