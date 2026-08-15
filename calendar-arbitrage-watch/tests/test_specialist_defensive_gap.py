"""Methodology delta v0.1.1 #2: G_d must be split by competitor posture
(de-novo vs already-active) and must never share a single scalar. Unknown
competitor start dates use an interval and the UNFAVORABLE bound
(2026-08-15 approval, points 5 and 8), never a fabricated point estimate.
"""

import _pathsetup  # noqa: F401
import unittest
from datetime import date, timedelta

from calendar_arbitrage_watch import specialist
from calendar_arbitrage_watch.models import DateBound, NumberClaim, ShockForecast, DATED, OBSERVED, \
    INSUFFICIENT_DATA


def _dated_shock(shock_date: str) -> ShockForecast:
    return ShockForecast(shock_type=DATED,
                          date_bound=DateBound(earliest=shock_date, latest=shock_date, evidence_status=OBSERVED))


class DefensiveGapNovoTests(unittest.TestCase):
    def test_g_d_novo_decreases_monotonically_as_shock_approaches_with_constant_l_remaining(self):
        """A de-novo entrant hasn't started, so their required work does
        not shrink with calendar time - correct DATED dynamics means
        G_d^novo shrinks purely because the shock date gets closer, even
        though nothing about the competitive picture changed."""
        shock = _dated_shock("2027-06-01")
        l_remaining_denovo = NumberClaim(value=150, unit="days", evidence_status=OBSERVED)

        g_d_t0 = specialist.compute_defensive_gap_novo("2026-08-15", shock, l_remaining_denovo)
        g_d_t1 = specialist.compute_defensive_gap_novo("2026-09-15", shock, l_remaining_denovo)
        g_d_t2 = specialist.compute_defensive_gap_novo("2026-10-15", shock, l_remaining_denovo)

        self.assertGreater(g_d_t0.value, g_d_t1.value)
        self.assertGreater(g_d_t1.value, g_d_t2.value)

    def test_g_d_novo_and_g_r_are_computed_independently(self):
        """Same formula shape is fine internally, but the two must never
        be forced to share a value - different l_remaining inputs must
        produce different results."""
        shock = _dated_shock("2027-06-01")
        l_remaining_ours = NumberClaim(value=50, unit="days", evidence_status=OBSERVED)
        l_remaining_denovo_reference = NumberClaim(value=200, unit="days", evidence_status=OBSERVED)

        g_r = specialist.compute_readiness_gap("2026-08-15", shock, l_remaining_ours)
        g_d_novo = specialist.compute_defensive_gap_novo("2026-08-15", shock, l_remaining_denovo_reference)

        self.assertNotEqual(g_r.value, g_d_novo.value)


class DefensiveGapActiveTests(unittest.TestCase):
    def test_no_defensible_bound_yields_insufficient_data(self):
        shock = _dated_shock("2027-06-01")
        claim, bound_used = specialist.compute_defensive_gap_active(
            "2026-08-15", shock, DateBound(), NumberClaim(value=50, evidence_status=OBSERVED),
            NumberClaim(value=50, evidence_status=OBSERVED))
        self.assertEqual(claim.evidence_status, INSUFFICIENT_DATA)
        self.assertEqual(bound_used, "")

    def test_uses_earliest_bound_when_both_present(self):
        shock = _dated_shock("2027-06-01")
        bound = DateBound(earliest="2026-01-01", latest="2026-03-01", evidence_status=OBSERVED)
        claim, bound_used = specialist.compute_defensive_gap_active(
            "2026-08-15", shock, bound, NumberClaim(value=200, evidence_status=OBSERVED),
            NumberClaim(value=50, evidence_status=OBSERVED))
        self.assertEqual(bound_used, "earliest")
        self.assertNotEqual(claim.evidence_status, INSUFFICIENT_DATA)

    def test_falls_back_to_latest_bound_when_earliest_missing(self):
        shock = _dated_shock("2027-06-01")
        bound = DateBound(latest="2026-03-01", evidence_status=OBSERVED)
        claim, bound_used = specialist.compute_defensive_gap_active(
            "2026-08-15", shock, bound, NumberClaim(value=200, evidence_status=OBSERVED),
            NumberClaim(value=50, evidence_status=OBSERVED))
        self.assertEqual(bound_used, "latest")

    def test_g_d_active_and_g_d_novo_never_share_a_value(self):
        shock = _dated_shock("2027-06-01")
        l_remaining_denovo = NumberClaim(value=150, unit="days", evidence_status=OBSERVED)
        g_d_novo = specialist.compute_defensive_gap_novo("2026-08-15", shock, l_remaining_denovo)

        bound = DateBound(earliest="2026-01-01", evidence_status=OBSERVED)
        g_d_active, _ = specialist.compute_defensive_gap_active(
            "2026-08-15", shock, bound, NumberClaim(value=120, evidence_status=OBSERVED),
            NumberClaim(value=50, evidence_status=OBSERVED))

        self.assertIsNotNone(g_d_novo.value)
        self.assertIsNotNone(g_d_active.value)
        self.assertNotEqual(g_d_novo.value, g_d_active.value)

    def test_earlier_competitor_start_worsens_our_relative_position(self):
        """A competitor who started earlier (more banked progress) should
        never look BETTER for us than one who started later, all else
        equal - sanity check on the sign/direction of the formula."""
        shock = _dated_shock("2027-06-01")
        competitor_l_remaining = NumberClaim(value=200, evidence_status=OBSERVED)
        our_l_remaining = NumberClaim(value=50, evidence_status=OBSERVED)

        early_bound = DateBound(earliest="2025-01-01", evidence_status=OBSERVED)
        late_bound = DateBound(earliest="2026-06-01", evidence_status=OBSERVED)

        g_d_early, _ = specialist.compute_defensive_gap_active(
            "2026-08-15", shock, early_bound, competitor_l_remaining, our_l_remaining)
        g_d_late, _ = specialist.compute_defensive_gap_active(
            "2026-08-15", shock, late_bound, competitor_l_remaining, our_l_remaining)

        self.assertLess(g_d_early.value, g_d_late.value)


if __name__ == "__main__":
    unittest.main()
