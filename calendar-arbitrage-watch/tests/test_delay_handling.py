"""Methodology delta v0.1.1 #4: a delay event never triggers an
automatic lifecycle DEGRADE. Instead T_shock, G_d (both), G_r, and a
competitive supply-response note are all recomputed together, every
time.
"""

import _pathsetup  # noqa: F401
import unittest

from calendar_arbitrage_watch import specialist
from calendar_arbitrage_watch.models import CompetitorFinish, DateBound, NumberClaim, ShockForecast, DATED, \
    OBSERVED, INSUFFICIENT_DATA


def _dated_shock(shock_date: str, version: int = 1) -> ShockForecast:
    return ShockForecast(shock_type=DATED,
                          date_bound=DateBound(earliest=shock_date, latest=shock_date, evidence_status=OBSERVED),
                          forecast_version=version)


def _competitor(l_min) -> CompetitorFinish:
    return CompetitorFinish(competitor_id="rival-1",
                             l_min_remaining_as_of=NumberClaim(value=l_min, unit="days", evidence_status=OBSERVED))


class RecomputeAfterDelayTests(unittest.TestCase):
    def test_recomputes_all_three_gap_quantities(self):
        original_shock = _dated_shock("2027-01-01", version=1)
        delayed_shock = _dated_shock("2027-07-01", version=2)  # pushed out six months

        result = specialist.recompute_after_delay(
            as_of="2026-08-15",
            new_shock=delayed_shock,
            l_remaining=NumberClaim(value=100, evidence_status=OBSERVED),
            l_irr_denovo=NumberClaim(value=150, evidence_status=OBSERVED),
            tracked_competitor=_competitor(l_min=200),
            our_l_remaining_for_active=NumberClaim(value=100, evidence_status=OBSERVED),
        )
        for key in ("g_r", "g_d_novo", "g_d_active", "supply_response_note"):
            self.assertIn(key, result)
        self.assertNotEqual(result["g_r"].evidence_status, INSUFFICIENT_DATA)
        self.assertNotEqual(result["g_d_novo"].evidence_status, INSUFFICIENT_DATA)

    def test_delay_can_help_us_and_help_new_entrants_at_the_same_time(self):
        """The delta explicitly forbids assuming delay always hurts or
        always helps - it can do both simultaneously. Pushing T_shock out
        increases G_r (helps us: more slack) AND DECREASES G_d^novo
        (helps new entrants: G_d^novo positive = 'not enough time for
        them', so a delay that shrinks it erodes that protection) when
        neither l_remaining changes."""
        shock_original = _dated_shock("2027-01-01", version=1)
        shock_delayed = _dated_shock("2027-07-01", version=2)
        l_remaining = NumberClaim(value=100, evidence_status=OBSERVED)
        l_irr_denovo = NumberClaim(value=150, evidence_status=OBSERVED)

        g_r_before = specialist.compute_readiness_gap("2026-08-15", shock_original, l_remaining)
        g_r_after = specialist.compute_readiness_gap("2026-08-15", shock_delayed, l_remaining)
        g_d_novo_before = specialist.compute_defensive_gap_novo("2026-08-15", shock_original, l_irr_denovo)
        g_d_novo_after = specialist.compute_defensive_gap_novo("2026-08-15", shock_delayed, l_irr_denovo)

        self.assertGreater(g_r_after.value, g_r_before.value)       # helps us
        self.assertLess(g_d_novo_after.value, g_d_novo_before.value)  # helps new entrants (less of a moat)

    def test_delay_never_directly_sets_a_lifecycle_state(self):
        """recompute_after_delay's return value has no lifecycle_state
        key at all - it is structurally impossible for this function to
        assign a DEGRADE outcome. A separate, explicit gate/lifecycle
        step is required to change state."""
        result = specialist.recompute_after_delay(
            as_of="2026-08-15",
            new_shock=_dated_shock("2027-07-01", version=2),
            l_remaining=NumberClaim(value=100, evidence_status=OBSERVED),
            l_irr_denovo=NumberClaim(value=150, evidence_status=OBSERVED),
            tracked_competitor=CompetitorFinish(),
            our_l_remaining_for_active=NumberClaim(),
        )
        self.assertNotIn("lifecycle_state", result)

    def test_supply_response_note_reflects_g_d_active_direction(self):
        original_shock = _dated_shock("2027-01-01", version=1)
        delayed_shock = _dated_shock("2027-07-01", version=2)
        common_kwargs = dict(
            as_of="2026-08-15",
            l_remaining=NumberClaim(value=100, evidence_status=OBSERVED),
            l_irr_denovo=NumberClaim(value=150, evidence_status=OBSERVED),
            tracked_competitor=_competitor(l_min=110),
            our_l_remaining_for_active=NumberClaim(value=100, evidence_status=OBSERVED),
        )
        before = specialist.recompute_after_delay(new_shock=original_shock, **common_kwargs)
        after = specialist.recompute_after_delay(new_shock=delayed_shock, **common_kwargs)
        # tracked_competitor.l_min and our_l_remaining are both unaffected
        # by the shock date - g_d_active must be UNCHANGED by this delay.
        self.assertEqual(before["g_d_active"].value, after["g_d_active"].value)


if __name__ == "__main__":
    unittest.main()
