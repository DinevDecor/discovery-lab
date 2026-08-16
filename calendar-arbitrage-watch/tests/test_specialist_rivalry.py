"""S_ready and RI (Rivalry Index) - corrected 2026-08-15-2, items 2-3 and
6. Canonical formulas:

    S_ready(T_shock) = rho * sum(q_k for competitors ready by shock)
    RI = D_shock / (S_existing + S_ready)

S_ready is NOT a normalized readiness score for our own candidate. RI is
NOT a composite with demand certainty/DSI/DRR.
"""

import _pathsetup  # noqa: F401
import unittest

from calendar_arbitrage_watch import specialist
from calendar_arbitrage_watch.models import CompetitorFinish, DateBound, NumberClaim, ShockForecast, DATED, \
    OBSERVED, INSUFFICIENT_DATA


def _dated_shock(shock_date: str) -> ShockForecast:
    return ShockForecast(shock_type=DATED,
                          date_bound=DateBound(earliest=shock_date, latest=shock_date, evidence_status=OBSERVED))


def _ready_competitor(competitor_id: str, l_min_days: float, q_value: float, unit: str) -> CompetitorFinish:
    """A competitor whose earliest defensible finish is well before the
    shock (so they count as 'ready by shock' in every test below)."""
    return CompetitorFinish(
        competitor_id=competitor_id,
        l_min_remaining_as_of=NumberClaim(value=l_min_days, unit="days", evidence_status=OBSERVED),
        q=NumberClaim(value=q_value, unit=unit, evidence_status=OBSERVED),
        as_of="2026-08-15",
    )


class SReadySumTests(unittest.TestCase):
    def test_10mw_plus_100mw_is_110mw_not_two_positions(self):
        """The exact regression named in the correction request: summing
        capacity, never counting competitors as discrete 'positions'."""
        shock = _dated_shock("2027-01-01")  # ~140 days out
        competitors = [
            _ready_competitor("rival-a", l_min_days=30, q_value=10, unit="MW"),
            _ready_competitor("rival-b", l_min_days=30, q_value=100, unit="MW"),
        ]
        s_ready = specialist.compute_s_ready("2026-08-15", shock, competitors, unit="MW")
        self.assertEqual(s_ready.value, 110.0)
        self.assertNotEqual(s_ready.value, 2.0)

    def test_not_ready_competitor_excluded_from_sum(self):
        shock = _dated_shock("2026-09-01")  # ~17 days out
        competitors = [
            _ready_competitor("rival-a", l_min_days=10, q_value=10, unit="MW"),   # ready (10 < 17)
            _ready_competitor("rival-b", l_min_days=365, q_value=999, unit="MW"),  # not ready
        ]
        s_ready = specialist.compute_s_ready("2026-08-15", shock, competitors, unit="MW")
        self.assertEqual(s_ready.value, 10.0)


class RhoDefaultTests(unittest.TestCase):
    def test_rho_defaults_to_1_0_without_evidence(self):
        shock = _dated_shock("2027-01-01")
        competitors = [_ready_competitor("rival-a", l_min_days=30, q_value=10, unit="MW")]
        s_ready_no_rho = specialist.compute_s_ready("2026-08-15", shock, competitors, unit="MW", rho=None)
        s_ready_explicit_1 = specialist.compute_s_ready(
            "2026-08-15", shock, competitors, unit="MW",
            rho=NumberClaim(value=1.0, evidence_status=OBSERVED))
        self.assertEqual(s_ready_no_rho.value, 10.0)
        self.assertEqual(s_ready_no_rho.value, s_ready_explicit_1.value)

    def test_rho_below_1_when_evidence_supports_a_discount(self):
        shock = _dated_shock("2027-01-01")
        competitors = [_ready_competitor("rival-a", l_min_days=30, q_value=100, unit="MW")]
        s_ready = specialist.compute_s_ready(
            "2026-08-15", shock, competitors, unit="MW",
            rho=NumberClaim(value=0.5, evidence_status=OBSERVED))
        self.assertEqual(s_ready.value, 50.0)


class UnknownCapacityOrUnitTests(unittest.TestCase):
    def test_no_declared_unit_is_insufficient_data(self):
        shock = _dated_shock("2027-01-01")
        competitors = [_ready_competitor("rival-a", l_min_days=30, q_value=10, unit="MW")]
        s_ready = specialist.compute_s_ready("2026-08-15", shock, competitors, unit="")
        self.assertEqual(s_ready.evidence_status, INSUFFICIENT_DATA)

    def test_ready_competitor_with_unknown_q_is_insufficient_data_not_dropped(self):
        """A ready competitor whose capacity is unknown must NOT be
        silently treated as contributing zero - that would understate
        rivalry, the opposite of this package's unfavorable-by-default
        convention. The whole result is INSUFFICIENT_DATA instead."""
        shock = _dated_shock("2027-01-01")
        competitors = [
            _ready_competitor("rival-a", l_min_days=30, q_value=10, unit="MW"),
            CompetitorFinish(competitor_id="rival-b",
                              l_min_remaining_as_of=NumberClaim(value=30, unit="days", evidence_status=OBSERVED),
                              q=NumberClaim()),  # ready, but q unknown
        ]
        s_ready = specialist.compute_s_ready("2026-08-15", shock, competitors, unit="MW")
        self.assertEqual(s_ready.evidence_status, INSUFFICIENT_DATA)

    def test_ready_competitor_with_mismatched_unit_is_insufficient_data(self):
        shock = _dated_shock("2027-01-01")
        competitors = [_ready_competitor("rival-a", l_min_days=30, q_value=10, unit="units/year")]
        s_ready = specialist.compute_s_ready("2026-08-15", shock, competitors, unit="MW")
        self.assertEqual(s_ready.evidence_status, INSUFFICIENT_DATA)

    def test_no_competitors_at_all_is_insufficient_data(self):
        shock = _dated_shock("2027-01-01")
        s_ready = specialist.compute_s_ready("2026-08-15", shock, [], unit="MW")
        self.assertEqual(s_ready.evidence_status, INSUFFICIENT_DATA)

    def test_no_shock_date_is_insufficient_data(self):
        competitors = [_ready_competitor("rival-a", l_min_days=30, q_value=10, unit="MW")]
        s_ready = specialist.compute_s_ready("2026-08-15", ShockForecast(), competitors, unit="MW")
        self.assertEqual(s_ready.evidence_status, INSUFFICIENT_DATA)


class KnownCompetitorUnknownReadinessTests(unittest.TestCase):
    """Regression tests for the 2026-08-15-3 correction, item 1: a known
    competitor whose readiness cannot be assessed must NOT be silently
    excluded from S_ready - that is optimistic bias. Only a competitor
    PROVEN not ready (a defensible l_min exceeding days-to-shock) may be
    excluded."""

    def test_known_competitor_with_unknown_l_min_forces_insufficient_data(self):
        shock = _dated_shock("2027-01-01")
        competitors = [
            _ready_competitor("rival-a", l_min_days=30, q_value=10, unit="MW"),  # known, ready
            CompetitorFinish(competitor_id="rival-unknown"),  # known to exist, readiness unknown
        ]
        s_ready = specialist.compute_s_ready("2026-08-15", shock, competitors, unit="MW")
        self.assertEqual(s_ready.evidence_status, INSUFFICIENT_DATA)
        self.assertIn("rival-unknown", s_ready.note)

    def test_this_is_different_from_a_competitor_proven_not_ready(self):
        """Contrast case: a competitor with a DEFENSIBLE l_min that
        exceeds days-to-shock IS legitimately excluded (proven not
        ready) - this must still compute a real S_ready, not
        INSUFFICIENT_DATA, unlike the unknown-readiness case above."""
        shock = _dated_shock("2026-09-01")  # ~17 days out
        competitors = [
            _ready_competitor("rival-a", l_min_days=10, q_value=10, unit="MW"),   # ready
            _ready_competitor("rival-proven-late", l_min_days=365, q_value=999, unit="MW"),  # proven not ready
        ]
        s_ready = specialist.compute_s_ready("2026-08-15", shock, competitors, unit="MW")
        self.assertEqual(s_ready.value, 10.0)
        self.assertNotEqual(s_ready.evidence_status, INSUFFICIENT_DATA)

    def test_unknown_readiness_competitor_alone_is_insufficient_data(self):
        shock = _dated_shock("2027-01-01")
        competitors = [CompetitorFinish(competitor_id="rival-unknown")]
        s_ready = specialist.compute_s_ready("2026-08-15", shock, competitors, unit="MW")
        self.assertEqual(s_ready.evidence_status, INSUFFICIENT_DATA)


class RivalryIndexDimensionalConsistencyTests(unittest.TestCase):
    def test_computes_when_all_three_share_a_unit(self):
        d_shock = NumberClaim(value=100, unit="MW", evidence_status=OBSERVED)
        s_existing = NumberClaim(value=30, unit="MW", evidence_status=OBSERVED)
        s_ready = NumberClaim(value=20, unit="MW", evidence_status=OBSERVED)
        ri = specialist.compute_rivalry_index(d_shock, s_existing, s_ready, unit="MW")
        self.assertEqual(ri.value, 100 / (30 + 20))

    def test_mismatched_unit_is_insufficient_data(self):
        d_shock = NumberClaim(value=100, unit="MW", evidence_status=OBSERVED)
        s_existing = NumberClaim(value=30, unit="units/year", evidence_status=OBSERVED)  # wrong unit
        s_ready = NumberClaim(value=20, unit="MW", evidence_status=OBSERVED)
        ri = specialist.compute_rivalry_index(d_shock, s_existing, s_ready, unit="MW")
        self.assertEqual(ri.evidence_status, INSUFFICIENT_DATA)

    def test_no_declared_common_unit_is_insufficient_data(self):
        """Regression for the 2026-08-15-3 correction, item 2: an empty
        declared `unit` must be rejected outright, even if all three
        operands happen to carry a matching (but here empty) unit."""
        d_shock = NumberClaim(value=100, unit="", evidence_status=OBSERVED)
        s_existing = NumberClaim(value=30, unit="", evidence_status=OBSERVED)
        s_ready = NumberClaim(value=20, unit="", evidence_status=OBSERVED)
        ri = specialist.compute_rivalry_index(d_shock, s_existing, s_ready, unit="")
        self.assertEqual(ri.evidence_status, INSUFFICIENT_DATA)

    def test_operand_with_empty_unit_against_a_declared_unit_is_insufficient_data(self):
        """Regression for the 2026-08-15-3 correction, item 2: the
        previous check (`if unit and claim.unit and ...`) silently
        passed when an operand's own `.unit` was empty, because the
        `and` short-circuited. Each operand's unit must now match the
        declared unit EXACTLY, empty or not."""
        d_shock = NumberClaim(value=100, unit="MW", evidence_status=OBSERVED)
        s_existing = NumberClaim(value=30, unit="MW", evidence_status=OBSERVED)
        s_ready = NumberClaim(value=20, unit="", evidence_status=OBSERVED)  # missing unit on this operand only
        ri = specialist.compute_rivalry_index(d_shock, s_existing, s_ready, unit="MW")
        self.assertEqual(ri.evidence_status, INSUFFICIENT_DATA)

    def test_missing_unit_on_each_operand_individually_is_insufficient_data(self):
        base = dict(value=10, unit="MW", evidence_status=OBSERVED)
        for missing in ("d_shock", "s_existing", "s_ready"):
            operands = {
                "d_shock": NumberClaim(**base),
                "s_existing": NumberClaim(**base),
                "s_ready": NumberClaim(**base),
            }
            operands[missing] = NumberClaim(value=10, unit="", evidence_status=OBSERVED)
            ri = specialist.compute_rivalry_index(operands["d_shock"], operands["s_existing"],
                                                    operands["s_ready"], unit="MW")
            self.assertEqual(ri.evidence_status, INSUFFICIENT_DATA, f"missing unit on {missing} was accepted")

    def test_missing_s_ready_is_insufficient_data(self):
        d_shock = NumberClaim(value=100, unit="MW", evidence_status=OBSERVED)
        s_existing = NumberClaim(value=30, unit="MW", evidence_status=OBSERVED)
        ri = specialist.compute_rivalry_index(d_shock, s_existing, NumberClaim(), unit="MW")
        self.assertEqual(ri.evidence_status, INSUFFICIENT_DATA)

    def test_zero_total_supply_is_insufficient_data_not_infinity(self):
        d_shock = NumberClaim(value=100, unit="MW", evidence_status=OBSERVED)
        s_existing = NumberClaim(value=0, unit="MW", evidence_status=OBSERVED)
        s_ready = NumberClaim(value=0, unit="MW", evidence_status=OBSERVED)
        ri = specialist.compute_rivalry_index(d_shock, s_existing, s_ready, unit="MW")
        self.assertEqual(ri.evidence_status, INSUFFICIENT_DATA)

    def test_ri_is_never_a_composite_with_demand_certainty(self):
        """Two scenarios with identical D_shock/S_existing/S_ready but
        different (hypothetical) demand certainty must produce the exact
        same RI - RI has no demand-certainty term at all."""
        d_shock = NumberClaim(value=100, unit="MW", evidence_status=OBSERVED)
        s_existing = NumberClaim(value=30, unit="MW", evidence_status=OBSERVED)
        s_ready = NumberClaim(value=20, unit="MW", evidence_status=OBSERVED)
        ri_a = specialist.compute_rivalry_index(d_shock, s_existing, s_ready, unit="MW")
        ri_b = specialist.compute_rivalry_index(d_shock, s_existing, s_ready, unit="MW")
        self.assertEqual(ri_a.value, ri_b.value)  # deterministic, no hidden demand-certainty input


if __name__ == "__main__":
    unittest.main()
