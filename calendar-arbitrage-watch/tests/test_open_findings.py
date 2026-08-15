"""2026-08-15 approval, points 4 and 7: C3 >= DC x 0.25 and
startability_gap are OPEN FINDINGS that must NEVER affect scoring/gate/
lifecycle decisions, even when a numeric value can be computed.
"""

import _pathsetup  # noqa: F401
import unittest

from calendar_arbitrage_watch import gate, specialist
from calendar_arbitrage_watch.models import (
    CalendarAssessment, DateBound, DefensiveGapAssessment, DemandProfile, DISCOVERY,
    NumberClaim, OpenFinding, ReadinessAssessment, MEASURED, OBSERVED, REVIEW_CONFIRMED,
    ShockForecast, DATED,
)


class C3GeDCThresholdOpenFindingTests(unittest.TestCase):
    def test_always_non_scoring_and_uncalibrated(self):
        finding = specialist.open_finding_pending_competition_threshold(pending_competition=None)
        self.assertFalse(finding.affects_scoring)
        self.assertIsNone(finding.value)
        self.assertEqual(finding.status, "OPEN_FINDING")

    def test_not_read_by_the_gate(self):
        """The gate must reach the same CONFIRMED/CHALLENGED/KILLED
        outcome regardless of what this finding says, since it is
        recorded but never consulted."""
        a = _confirmable_assessment()
        a.open_findings = [specialist.open_finding_pending_competition_threshold(None)]
        decision_with = gate.review(a)
        a.open_findings = []
        decision_without = gate.review(a)
        self.assertEqual(decision_with.outcome, decision_without.outcome)


class StartabilityGapOpenFindingTests(unittest.TestCase):
    def test_computed_when_inputs_available(self):
        shock = ShockForecast(shock_type=DATED,
                               date_bound=DateBound(earliest="2027-01-01", latest="2027-01-01",
                                                     evidence_status=OBSERVED))
        l_remaining_denovo = NumberClaim(value=100, evidence_status=OBSERVED)
        clock_open_date = DateBound(earliest="2026-11-01", evidence_status=OBSERVED)
        finding = specialist.open_finding_startability_gap(shock, l_remaining_denovo, clock_open_date)
        self.assertIsNotNone(finding.value)
        self.assertFalse(finding.affects_scoring)

    def test_negative_gap_flags_de_novo_already_too_late(self):
        """t_lockout_novo = 2027-01-01 - 100 days ~ 2026-09-23. If the
        procedure only opened on 2026-11-01 (after that), de-novo supply
        was already mathematically late the moment it became accessible -
        the exact regime this finding exists to catch."""
        shock = ShockForecast(shock_type=DATED,
                               date_bound=DateBound(earliest="2027-01-01", latest="2027-01-01",
                                                     evidence_status=OBSERVED))
        l_remaining_denovo = NumberClaim(value=100, evidence_status=OBSERVED)
        clock_open_date = DateBound(earliest="2026-11-01", evidence_status=OBSERVED)
        finding = specialist.open_finding_startability_gap(shock, l_remaining_denovo, clock_open_date)
        self.assertLess(finding.value, 0)
        self.assertIn("already mathematically late", finding.note)

    def test_insufficient_data_when_clock_open_date_missing(self):
        shock = ShockForecast(shock_type=DATED,
                               date_bound=DateBound(earliest="2027-01-01", latest="2027-01-01",
                                                     evidence_status=OBSERVED))
        finding = specialist.open_finding_startability_gap(
            shock, NumberClaim(value=100, evidence_status=OBSERVED), DateBound())
        self.assertIsNone(finding.value)

    def test_not_read_by_the_gate(self):
        a = _confirmable_assessment()
        shock = ShockForecast(shock_type=DATED,
                               date_bound=DateBound(earliest="2027-01-01", latest="2027-01-01",
                                                     evidence_status=OBSERVED))
        finding = specialist.open_finding_startability_gap(
            shock, NumberClaim(value=999, evidence_status=OBSERVED),  # deliberately extreme negative-gap input
            DateBound(earliest="2026-11-01", evidence_status=OBSERVED))
        self.assertLess(finding.value, 0)
        a.open_findings = [finding]
        decision = gate.review(a)
        self.assertEqual(decision.outcome, REVIEW_CONFIRMED)  # unaffected by the extreme open finding


def _confirmable_assessment() -> CalendarAssessment:
    return CalendarAssessment(
        candidate_id="cand-1", mode=DISCOVERY, category="regulatory_clock", title="Test",
        readiness=ReadinessAssessment(g_r_days=NumberClaim(value=30, provenance=MEASURED, evidence_status=OBSERVED)),
        defensive=DefensiveGapAssessment(
            g_d_novo_days=NumberClaim(value=20, provenance=MEASURED, evidence_status=OBSERVED),
            g_d_active_days=NumberClaim(value=15, provenance=MEASURED, evidence_status=OBSERVED),
        ),
        demand=DemandProfile(demand_obligation_certainty=NumberClaim(value=0.9, evidence_status=OBSERVED)),
    )


if __name__ == "__main__":
    unittest.main()
