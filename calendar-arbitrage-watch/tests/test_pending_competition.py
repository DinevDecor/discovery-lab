"""Methodology delta v0.1.1 #5: formal free capacity alone is
insufficient for infrastructure candidates - pending_applications,
issued_connection_opinions, known_queue_ahead, and
committed_competing_projects are all tracked as separate, never-collapsed
fields.
"""

import _pathsetup  # noqa: F401
import unittest

from calendar_arbitrage_watch.models import NumberClaim, PendingCompetitionAssessment, OBSERVED, INSUFFICIENT_DATA


class PendingCompetitionTests(unittest.TestCase):
    def test_large_pending_queue_against_nominal_free_capacity_is_representable(self):
        """The exact scenario the delta names: nominal free capacity
        looks generous, but a known queue ahead of us means it is not
        actually a free calendar slot. Both facts must be simultaneously
        visible, not collapsed into one 'availability' number."""
        pc = PendingCompetitionAssessment(
            formal_free_capacity=NumberClaim(value=50, unit="MW", evidence_status=OBSERVED),
            known_queue_ahead=NumberClaim(value=48, unit="MW", evidence_status=OBSERVED),
            committed_competing_projects=NumberClaim(value=6, unit="projects", evidence_status=OBSERVED),
        )
        d = pc.to_dict()
        self.assertEqual(d["formal_free_capacity"]["value"], 50)
        self.assertEqual(d["known_queue_ahead"]["value"], 48)
        self.assertEqual(d["committed_competing_projects"]["value"], 6)
        # No derived "true_availability" or similar single-number field exists on the dataclass.
        self.assertNotIn("availability", d)
        self.assertNotIn("true_free_capacity", d)

    def test_unknown_pending_queue_is_insufficient_data_not_zero(self):
        pc = PendingCompetitionAssessment(formal_free_capacity=NumberClaim(value=50, evidence_status=OBSERVED))
        self.assertEqual(pc.known_queue_ahead.evidence_status, INSUFFICIENT_DATA)
        self.assertIsNone(pc.known_queue_ahead.value)

    def test_round_trip(self):
        pc = PendingCompetitionAssessment(
            formal_free_capacity=NumberClaim(value=10, evidence_status=OBSERVED),
            pending_applications=NumberClaim(value=3, evidence_status=OBSERVED),
            issued_connection_opinions=NumberClaim(value=2, evidence_status=OBSERVED),
            known_queue_ahead=NumberClaim(value=1, evidence_status=OBSERVED),
            committed_competing_projects=NumberClaim(value=1, evidence_status=OBSERVED),
        )
        self.assertEqual(PendingCompetitionAssessment.from_dict(pc.to_dict()), pc)


if __name__ == "__main__":
    unittest.main()
