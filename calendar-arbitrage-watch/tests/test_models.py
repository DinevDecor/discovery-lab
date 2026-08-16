import _pathsetup  # noqa: F401
import unittest

from calendar_arbitrage_watch.models import (
    CalendarAssessment, DateBound, DemandProfile, NumberClaim, OpenFinding,
    PendingCompetitionAssessment, ReadinessAssessment, ShockForecast,
    DATED, DISCOVERY, INSUFFICIENT_DATA, OBSERVED, WATCH,
)


class RoundTripTests(unittest.TestCase):
    def test_number_claim_round_trip(self):
        c = NumberClaim(value=12.5, unit="days", provenance="MEASURED", evidence_status=OBSERVED, as_of="2026-08-15")
        self.assertEqual(NumberClaim.from_dict(c.to_dict()), c)

    def test_insufficient_data_is_a_complete_valid_record(self):
        c = NumberClaim()
        self.assertEqual(c.evidence_status, INSUFFICIENT_DATA)
        self.assertIsNone(c.value)

    def test_date_bound_is_defensible_requires_evidence_status_and_a_date(self):
        self.assertFalse(DateBound().is_defensible())
        self.assertFalse(DateBound(earliest="2026-01-01").is_defensible())  # still INSUFFICIENT_DATA by default
        self.assertTrue(DateBound(earliest="2026-01-01", evidence_status=OBSERVED).is_defensible())

    def test_calendar_assessment_round_trip_full(self):
        a = CalendarAssessment(
            candidate_id="cand-1",
            mode=DISCOVERY,
            category="regulatory_clock",
            title="Test candidate",
            shock_forecast=ShockForecast(shock_type=DATED,
                                          date_bound=DateBound(earliest="2027-01-01", latest="2027-01-01",
                                                                evidence_status=OBSERVED)),
            readiness=ReadinessAssessment(l_remaining_days=NumberClaim(value=100, unit="days",
                                                                        evidence_status=OBSERVED)),
            demand=DemandProfile(demand_obligation_certainty=NumberClaim(value=0.8, evidence_status=OBSERVED)),
            pending_competition=PendingCompetitionAssessment(
                formal_free_capacity=NumberClaim(value=5, evidence_status=OBSERVED)),
            open_findings=[OpenFinding(finding_id="x", description="d")],
            lifecycle_state=WATCH,
            evidence_ids=["ev-1"],
        )
        rebuilt = CalendarAssessment.from_dict(a.to_dict())
        self.assertEqual(rebuilt.to_dict(), a.to_dict())

    def test_from_dict_ignores_unknown_keys(self):
        data = {"candidate_id": "c1", "commentary": "authored by hand, extra field"}
        a = CalendarAssessment.from_dict(data)
        self.assertEqual(a.candidate_id, "c1")


if __name__ == "__main__":
    unittest.main()
