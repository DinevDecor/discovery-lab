"""Methodology delta v0.1.1 #3 + 2026-08-15 approval point 5: demand is
four separate fields (DOC, SDS, DRR, demand_suppression_risk), never one
confidence multiplier.

DSI (Date Stability Index) IS canonically defined - research v0.1.2,
DELTA v0.1.1->v0.1.2 §P5, renames SDS to DSI as an additive heuristic
index, explicitly non-Bayesian, DSI=1 at shock_type=ROLLING (provenance
corrected 2026-08-15-4; a prior draft of this test module incorrectly
claimed no such definition existed anywhere reachable). It is
deliberately NOT_IMPLEMENTED here: not needed for this 30-day minimal
watch slice, its §P5 penalty table is uncalibrated, and it has zero
scoring/lifecycle effect. Do not resurrect the earlier invented
HIGH/MEDIUM/LOW heuristic under the DSI name - implementing §P5's
actual formula is a separate, future, deliberately-scoped task.
"""

import _pathsetup  # noqa: F401
import unittest

from calendar_arbitrage_watch import specialist
from calendar_arbitrage_watch.models import DemandProfile, NumberClaim, OBSERVED, NOT_IMPLEMENTED


class DemandStabilityIndexTests(unittest.TestCase):
    def test_always_not_implemented_regardless_of_input(self):
        """Regression test for the 2026-08-15-3 correction: no matter what
        demand evidence is supplied - fully populated, empty, high/low
        certainty - DSI must return NOT_IMPLEMENTED, never a fabricated
        HIGH/MEDIUM/LOW tier."""
        cases = [
            DemandProfile(),
            DemandProfile(demand_obligation_certainty=NumberClaim(value=0.9, evidence_status=OBSERVED)),
            DemandProfile(shock_date_stability=NumberClaim(value=0.9, evidence_status=OBSERVED)),
            DemandProfile(
                demand_obligation_certainty=NumberClaim(value=0.95, evidence_status=OBSERVED),
                shock_date_stability=NumberClaim(value=0.95, evidence_status=OBSERVED),
            ),
            DemandProfile(
                demand_obligation_certainty=NumberClaim(value=0.05, evidence_status=OBSERVED),
                shock_date_stability=NumberClaim(value=0.05, evidence_status=OBSERVED),
            ),
        ]
        for demand in cases:
            self.assertEqual(specialist.compute_demand_stability_index(demand), NOT_IMPLEMENTED)

    def test_never_returns_a_fabricated_tier_string(self):
        demand = DemandProfile(
            demand_obligation_certainty=NumberClaim(value=0.9, evidence_status=OBSERVED),
            shock_date_stability=NumberClaim(value=0.75, evidence_status=OBSERVED),
        )
        result = specialist.compute_demand_stability_index(demand)
        self.assertNotIn(result, ("HIGH", "MEDIUM", "LOW"))
        self.assertEqual(result, NOT_IMPLEMENTED)

    def test_default_field_value_on_a_fresh_assessment_is_not_implemented(self):
        """models.CalendarAssessment.demand_stability_index defaults to
        NOT_IMPLEMENTED, not INSUFFICIENT_DATA - the two mean different
        things (see models.py's NOT_IMPLEMENTED docstring)."""
        from calendar_arbitrage_watch.models import CalendarAssessment
        a = CalendarAssessment(candidate_id="c1")
        self.assertEqual(a.demand_stability_index, NOT_IMPLEMENTED)


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
