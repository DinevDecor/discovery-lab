"""Methodology delta v0.1.1 #1: G_r must not automatically decrease with
elapsed time alone. If our position advances at the same rate as the
calendar, T_shock and L_remaining both fall together and G_r stays flat.
"""

import _pathsetup  # noqa: F401
import unittest
from datetime import date, timedelta

from calendar_arbitrage_watch import specialist
from calendar_arbitrage_watch.models import DateBound, NumberClaim, ShockForecast, DATED, MEASURED, OBSERVED, \
    INSUFFICIENT_DATA


def _dated_shock(shock_date: str) -> ShockForecast:
    return ShockForecast(shock_type=DATED,
                          date_bound=DateBound(earliest=shock_date, latest=shock_date, evidence_status=OBSERVED),
                          as_of="2026-08-15")


class ReadinessGapTests(unittest.TestCase):
    def test_g_r_is_insufficient_data_without_shock_date(self):
        shock = ShockForecast()  # no date_bound
        g_r = specialist.compute_readiness_gap("2026-08-15", shock, NumberClaim(value=10, evidence_status=OBSERVED))
        self.assertEqual(g_r.evidence_status, INSUFFICIENT_DATA)

    def test_g_r_is_insufficient_data_without_l_remaining(self):
        shock = _dated_shock("2027-01-01")
        g_r = specialist.compute_readiness_gap("2026-08-15", shock, NumberClaim())
        self.assertEqual(g_r.evidence_status, INSUFFICIENT_DATA)

    def test_g_r_matches_the_formula(self):
        shock = _dated_shock("2027-01-01")
        l_remaining = NumberClaim(value=100, unit="days", provenance=MEASURED, evidence_status=OBSERVED)
        g_r = specialist.compute_readiness_gap("2026-08-15", shock, l_remaining)
        expected_days_to_shock = (date(2027, 1, 1) - date(2026, 8, 15)).days
        self.assertEqual(g_r.value, expected_days_to_shock - 100)

    def test_g_r_stays_flat_when_progress_matches_calendar_pace(self):
        """The core regression this test proves: elapsed time alone must
        never move G_r. Ten days pass; T_shock is ten days closer; but our
        own remaining work ALSO shrank by exactly ten days (we kept pace)
        - so G_r at t1 must equal G_r at t0, not have silently drifted
        because ten days simply passed."""
        shock = _dated_shock("2027-06-01")
        as_of_0 = "2026-08-15"
        l_remaining_0 = NumberClaim(value=200, unit="days", provenance=MEASURED, evidence_status=OBSERVED)
        g_r_0 = specialist.compute_readiness_gap(as_of_0, shock, l_remaining_0)

        as_of_1 = (date(2026, 8, 15) + timedelta(days=10)).isoformat()
        l_remaining_1 = NumberClaim(value=190, unit="days", provenance=MEASURED, evidence_status=OBSERVED)
        g_r_1 = specialist.compute_readiness_gap(as_of_1, shock, l_remaining_1)

        self.assertEqual(g_r_0.value, g_r_1.value)

    def test_g_r_worsens_when_progress_slips_behind_calendar_pace(self):
        """If ten days pass but remaining work only shrank by four days
        (six days of slippage), G_r must shrink by six days - not stay
        flat, and not shrink by the full ten (that would be double-
        counting elapsed time, the exact bug the delta forbids)."""
        shock = _dated_shock("2027-06-01")
        l_remaining_0 = NumberClaim(value=200, unit="days", provenance=MEASURED, evidence_status=OBSERVED)
        g_r_0 = specialist.compute_readiness_gap("2026-08-15", shock, l_remaining_0)

        as_of_1 = (date(2026, 8, 15) + timedelta(days=10)).isoformat()
        l_remaining_1 = NumberClaim(value=196, unit="days", provenance=MEASURED, evidence_status=OBSERVED)  # only 4 days of progress
        g_r_1 = specialist.compute_readiness_gap(as_of_1, shock, l_remaining_1)

        self.assertEqual(g_r_0.value - g_r_1.value, 6)

    def test_unfavorable_shock_date_uses_earliest_bound(self):
        shock = ShockForecast(shock_type="ROLLING",
                               date_bound=DateBound(earliest="2027-01-01", latest="2027-06-01",
                                                     evidence_status=OBSERVED))
        self.assertEqual(specialist.unfavorable_shock_date(shock), "2027-01-01")


if __name__ == "__main__":
    unittest.main()
