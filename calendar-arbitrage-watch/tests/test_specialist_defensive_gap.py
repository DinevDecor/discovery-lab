"""Methodology delta v0.1.1 #2, corrected 2026-08-15-2 (item 1 - G_d^novo
sign/formula; item 4 - active competitor semantics). G_d must be split by
competitor posture and must never share a single scalar. Unknown
competitor finish times use L_min/L_max bounds and the UNFAVORABLE bound
to us, never a fabricated point estimate.
"""

import _pathsetup  # noqa: F401
import unittest
from datetime import date, timedelta

from calendar_arbitrage_watch import specialist
from calendar_arbitrage_watch.models import CompetitorFinish, DateBound, NumberClaim, ShockForecast, DATED, \
    OBSERVED, INSUFFICIENT_DATA


def _dated_shock(shock_date: str) -> ShockForecast:
    return ShockForecast(shock_type=DATED,
                          date_bound=DateBound(earliest=shock_date, latest=shock_date, evidence_status=OBSERVED))


class DefensiveGapNovoTests(unittest.TestCase):
    def test_g_d_novo_sign_positive_means_not_enough_time(self):
        """Regression test for the 2026-08-15-2 correction: G_d^novo =
        L_irr - T_shock. A de-novo entrant needing 24 months (730 days)
        against a shock only 100 days away has nowhere near enough time -
        G_d^novo must be POSITIVE and large."""
        shock = _dated_shock("2026-11-23")  # ~100 days from 2026-08-15
        l_irr_denovo = NumberClaim(value=730, unit="days", evidence_status=OBSERVED)  # 24 months
        g_d_novo = specialist.compute_defensive_gap_novo("2026-08-15", shock, l_irr_denovo)
        self.assertGreater(g_d_novo.value, 0)

    def test_g_d_novo_sign_negative_means_de_novo_would_make_it(self):
        """A de-novo entrant needing only 10 days against a shock 100 days
        away has plenty of time - G_d^novo must be NEGATIVE."""
        shock = _dated_shock("2026-11-23")
        l_irr_denovo = NumberClaim(value=10, unit="days", evidence_status=OBSERVED)
        g_d_novo = specialist.compute_defensive_gap_novo("2026-08-15", shock, l_irr_denovo)
        self.assertLess(g_d_novo.value, 0)

    def test_g_d_novo_increases_as_dated_shock_approaches_with_constant_l_irr(self):
        """24-month (730-day) L_irr, fixed DATED shock: as calendar time
        passes and the shock gets closer, a de-novo entrant's required
        work does NOT shrink (they haven't started) - G_d^novo must
        INCREASE monotonically. This is the exact numeric example named
        in the 2026-08-15-2 correction request."""
        shock = _dated_shock("2028-08-15")  # two years out from t0
        l_irr_denovo = NumberClaim(value=730, unit="days", evidence_status=OBSERVED)  # 24 months

        g_d_t0 = specialist.compute_defensive_gap_novo("2026-08-15", shock, l_irr_denovo)
        g_d_t1 = specialist.compute_defensive_gap_novo("2026-11-15", shock, l_irr_denovo)  # +92 days
        g_d_t2 = specialist.compute_defensive_gap_novo("2027-02-15", shock, l_irr_denovo)  # +184 days

        self.assertLess(g_d_t0.value, g_d_t1.value)
        self.assertLess(g_d_t1.value, g_d_t2.value)

    def test_g_d_novo_does_not_reuse_compute_readiness_gap(self):
        """G_r and G_d^novo must diverge for the same as_of/shock even when
        l_remaining/l_irr_denovo are numerically equal - opposite sign
        conventions, sharing the formula was the original bug."""
        shock = _dated_shock("2027-06-01")
        same_value_claim = NumberClaim(value=100, unit="days", evidence_status=OBSERVED)

        g_r = specialist.compute_readiness_gap("2026-08-15", shock, same_value_claim)
        g_d_novo = specialist.compute_defensive_gap_novo("2026-08-15", shock, same_value_claim)

        self.assertEqual(g_r.value, -g_d_novo.value)  # exact sign inversion for identical inputs

    def test_insufficient_data_without_shock_date(self):
        g_d_novo = specialist.compute_defensive_gap_novo(
            "2026-08-15", ShockForecast(), NumberClaim(value=100, evidence_status=OBSERVED))
        self.assertEqual(g_d_novo.evidence_status, INSUFFICIENT_DATA)

    def test_insufficient_data_without_l_irr_denovo(self):
        shock = _dated_shock("2027-06-01")
        g_d_novo = specialist.compute_defensive_gap_novo("2026-08-15", shock, NumberClaim())
        self.assertEqual(g_d_novo.evidence_status, INSUFFICIENT_DATA)


def _competitor(l_min=None, l_max=None) -> CompetitorFinish:
    return CompetitorFinish(
        competitor_id="rival-1",
        l_min_remaining_as_of=(NumberClaim(value=l_min, unit="days", evidence_status=OBSERVED)
                                if l_min is not None else NumberClaim()),
        l_max_remaining_as_of=(NumberClaim(value=l_max, unit="days", evidence_status=OBSERVED)
                                if l_max is not None else NumberClaim()),
    )


class DefensiveGapActiveTests(unittest.TestCase):
    def test_no_defensible_l_min_yields_insufficient_data(self):
        claim = specialist.compute_defensive_gap_active(
            _competitor(), NumberClaim(value=50, evidence_status=OBSERVED))
        self.assertEqual(claim.evidence_status, INSUFFICIENT_DATA)

    def test_missing_our_l_remaining_yields_insufficient_data(self):
        claim = specialist.compute_defensive_gap_active(_competitor(l_min=40), NumberClaim())
        self.assertEqual(claim.evidence_status, INSUFFICIENT_DATA)

    def test_screens_at_l_min_not_l_max(self):
        """Screening must use L_min (the earliest/fastest defensible
        competitor finish - most threatening to us), never L_max, even
        when both are present."""
        competitor = _competitor(l_min=40, l_max=200)
        claim = specialist.compute_defensive_gap_active(competitor, NumberClaim(value=50, evidence_status=OBSERVED))
        self.assertEqual(claim.value, 40 - 50)  # uses l_min=40, not l_max=200

    def test_no_double_counting_of_elapsed_competitor_time(self):
        """Regression test for the 2026-08-15-2 correction, item 4: if a
        competitor's l_min_remaining_as_of is ALREADY an 'as of today'
        remaining estimate (e.g. asserted directly from their own status
        page), this function must NOT additionally subtract any elapsed
        time computed from a separate start-date bound - there is no
        start_bound parameter in this function's signature at all, making
        a second subtraction structurally impossible. The result must be
        the exact, unadjusted difference."""
        competitor = _competitor(l_min=40)
        our_l_remaining = NumberClaim(value=15, evidence_status=OBSERVED)
        claim = specialist.compute_defensive_gap_active(competitor, our_l_remaining)
        self.assertEqual(claim.value, 25.0)  # exactly 40 - 15, nothing else subtracted

    def test_g_d_active_and_g_d_novo_never_share_a_value(self):
        shock = _dated_shock("2027-06-01")
        l_irr_denovo = NumberClaim(value=150, unit="days", evidence_status=OBSERVED)
        g_d_novo = specialist.compute_defensive_gap_novo("2026-08-15", shock, l_irr_denovo)

        competitor = _competitor(l_min=120)
        g_d_active = specialist.compute_defensive_gap_active(competitor, NumberClaim(value=50, evidence_status=OBSERVED))

        self.assertIsNotNone(g_d_novo.value)
        self.assertIsNotNone(g_d_active.value)
        self.assertNotEqual(g_d_novo.value, g_d_active.value)

    def test_earlier_finishing_competitor_worsens_our_relative_position(self):
        our_l_remaining = NumberClaim(value=50, evidence_status=OBSERVED)
        fast_competitor = _competitor(l_min=30)
        slow_competitor = _competitor(l_min=120)

        g_d_fast = specialist.compute_defensive_gap_active(fast_competitor, our_l_remaining)
        g_d_slow = specialist.compute_defensive_gap_active(slow_competitor, our_l_remaining)

        self.assertLess(g_d_fast.value, g_d_slow.value)


class DeriveRemainingFromStartTests(unittest.TestCase):
    def test_derives_once_from_start_and_nominal_duration(self):
        remaining = specialist.derive_remaining_from_start("2026-08-15", "2026-06-01", 365)
        elapsed = (date(2026, 8, 15) - date(2026, 6, 1)).days
        self.assertEqual(remaining, 365 - elapsed)

    def test_none_when_start_unparseable(self):
        self.assertIsNone(specialist.derive_remaining_from_start("2026-08-15", None, 365))

    def test_competitor_finish_from_start_and_duration_uses_earliest_for_l_min(self):
        """Earliest start = most elapsed = LEAST remaining = L_min (most
        threatening to us); latest start = least elapsed = MOST
        remaining = L_max."""
        start_bound = DateBound(earliest="2026-01-01", latest="2026-06-01", evidence_status=OBSERVED)
        cf = specialist.competitor_finish_from_start_and_duration(
            "rival-1", "2026-08-15", start_bound, NumberClaim(value=365, evidence_status=OBSERVED),
            NumberClaim(value=10, unit="MW", evidence_status=OBSERVED))
        self.assertLess(cf.l_min_remaining_as_of.value, cf.l_max_remaining_as_of.value)


if __name__ == "__main__":
    unittest.main()
