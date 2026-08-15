"""S_ready (same unit as demand) and RI (Readiness Index) - documented
working-definition ASSUMPTIONS pending review (see specialist.py
docstrings and the implementation report). These tests pin down the
CURRENT behavior so a future review can see exactly what would change.
"""

import _pathsetup  # noqa: F401
import unittest

from calendar_arbitrage_watch import specialist
from calendar_arbitrage_watch.models import DemandProfile, NumberClaim, OBSERVED, INSUFFICIENT_DATA


class SReadyTests(unittest.TestCase):
    def test_insufficient_data_without_g_r(self):
        s = specialist.compute_s_ready(NumberClaim(), 100)
        self.assertEqual(s.evidence_status, INSUFFICIENT_DATA)

    def test_insufficient_data_without_horizon(self):
        g_r = NumberClaim(value=50, evidence_status=OBSERVED)
        s = specialist.compute_s_ready(g_r, None)
        self.assertEqual(s.evidence_status, INSUFFICIENT_DATA)

    def test_same_unit_as_demand_fields(self):
        """S_ready must land on the same 0..1 scale demand fields use."""
        g_r = NumberClaim(value=50, evidence_status=OBSERVED)
        s = specialist.compute_s_ready(g_r, 100)
        self.assertEqual(s.unit, "ratio")
        self.assertGreaterEqual(s.value, 0.0)
        self.assertLessEqual(s.value, 1.0)

    def test_clamped_at_one_when_g_r_exceeds_horizon(self):
        g_r = NumberClaim(value=500, evidence_status=OBSERVED)
        s = specialist.compute_s_ready(g_r, 100)
        self.assertEqual(s.value, 1.0)

    def test_clamped_at_zero_when_g_r_is_negative(self):
        g_r = NumberClaim(value=-50, evidence_status=OBSERVED)
        s = specialist.compute_s_ready(g_r, 100)
        self.assertEqual(s.value, 0.0)


class ReadinessIndexTests(unittest.TestCase):
    def test_insufficient_data_without_s_ready(self):
        ri = specialist.compute_readiness_index(NumberClaim(), DemandProfile())
        self.assertEqual(ri.evidence_status, INSUFFICIENT_DATA)

    def test_insufficient_data_without_demand_certainty(self):
        s = NumberClaim(value=0.5, evidence_status=OBSERVED)
        ri = specialist.compute_readiness_index(s, DemandProfile())
        self.assertEqual(ri.evidence_status, INSUFFICIENT_DATA)

    def test_high_readiness_with_uncertain_demand_is_penalized(self):
        s = NumberClaim(value=1.0, evidence_status=OBSERVED)
        demand_certain = DemandProfile(demand_obligation_certainty=NumberClaim(value=0.9, evidence_status=OBSERVED))
        demand_uncertain = DemandProfile(demand_obligation_certainty=NumberClaim(value=0.2, evidence_status=OBSERVED))
        ri_certain = specialist.compute_readiness_index(s, demand_certain)
        ri_uncertain = specialist.compute_readiness_index(s, demand_uncertain)
        self.assertGreater(ri_certain.value, ri_uncertain.value)


if __name__ == "__main__":
    unittest.main()
