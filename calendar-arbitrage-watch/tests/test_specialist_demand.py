"""Methodology delta v0.1.1 #3 + 2026-08-15 approval point 5: demand is
four separate fields (DOC, SDS, DRR, demand_suppression_risk), never one
confidence multiplier. DSI is a rule-based heuristic tier, never a
Bayesian posterior.
"""

import _pathsetup  # noqa: F401
import unittest

from calendar_arbitrage_watch import specialist
from calendar_arbitrage_watch.models import DemandProfile, NumberClaim, OBSERVED, INSUFFICIENT_DATA


class DemandStabilityIndexTests(unittest.TestCase):
    def test_missing_doc_yields_insufficient_data(self):
        demand = DemandProfile(shock_date_stability=NumberClaim(value=0.9, evidence_status=OBSERVED))
        self.assertEqual(specialist.compute_demand_stability_index(demand), INSUFFICIENT_DATA)

    def test_missing_sds_yields_insufficient_data(self):
        demand = DemandProfile(demand_obligation_certainty=NumberClaim(value=0.9, evidence_status=OBSERVED))
        self.assertEqual(specialist.compute_demand_stability_index(demand), INSUFFICIENT_DATA)

    def test_high_tier(self):
        demand = DemandProfile(
            demand_obligation_certainty=NumberClaim(value=0.9, evidence_status=OBSERVED),
            shock_date_stability=NumberClaim(value=0.75, evidence_status=OBSERVED),
        )
        self.assertEqual(specialist.compute_demand_stability_index(demand), "HIGH")

    def test_low_tier_dragged_down_by_the_weaker_field(self):
        """Almost-certain obligation with an unstable date must NOT read
        as HIGH just because one field is high - this is the exact
        'obligation nearly certain, date gets postponed' example from the
        task, and DSI must be sensitive to it."""
        demand = DemandProfile(
            demand_obligation_certainty=NumberClaim(value=0.95, evidence_status=OBSERVED),
            shock_date_stability=NumberClaim(value=0.1, evidence_status=OBSERVED),
        )
        self.assertEqual(specialist.compute_demand_stability_index(demand), "LOW")

    def test_dsi_is_not_a_probability_product(self):
        """A Bayesian-style combination (e.g. multiplying the two
        certainties) would produce 0.9*0.75=0.675 - a number. DSI must
        instead be a discrete tier string, never a float."""
        demand = DemandProfile(
            demand_obligation_certainty=NumberClaim(value=0.9, evidence_status=OBSERVED),
            shock_date_stability=NumberClaim(value=0.75, evidence_status=OBSERVED),
        )
        result = specialist.compute_demand_stability_index(demand)
        self.assertIsInstance(result, str)
        self.assertIn(result, ("HIGH", "MEDIUM", "LOW", INSUFFICIENT_DATA))


class DeadlineReliefVsSuppressionTests(unittest.TestCase):
    def test_fields_are_independently_settable_and_never_merged(self):
        demand = DemandProfile(
            demand_obligation_certainty=NumberClaim(value=0.9, evidence_status=OBSERVED),
            deadline_relief_risk=NumberClaim(value=0.6, evidence_status=OBSERVED),      # date might move
            demand_suppression_risk=NumberClaim(value=0.05, evidence_status=OBSERVED),  # obligation itself is solid
        )
        self.assertNotEqual(demand.deadline_relief_risk.value, demand.demand_suppression_risk.value)
        # Nothing in the model computes one from the other.
        self.assertEqual(demand.deadline_relief_risk.value, 0.6)
        self.assertEqual(demand.demand_suppression_risk.value, 0.05)


if __name__ == "__main__":
    unittest.main()
