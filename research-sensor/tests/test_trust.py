import _pathsetup  # noqa: F401
import unittest

from research_sensor.models import Confidence, EvidenceLevel
from research_sensor.trust import assess_confidence, can_accept_signal


class TestConfidenceRules(unittest.TestCase):
    def test_peer_reviewed_published_gives_high(self):
        self.assertEqual(
            assess_confidence([EvidenceLevel.PEER_REVIEWED_PUBLISHED], 1), Confidence.HIGH
        )

    def test_peer_reviewed_accepted_gives_high(self):
        self.assertEqual(
            assess_confidence([EvidenceLevel.PEER_REVIEWED_ACCEPTED], 1), Confidence.HIGH
        )

    def test_single_notable_lab_preprint_gives_medium_not_high(self):
        self.assertEqual(
            assess_confidence([EvidenceLevel.NOTABLE_LAB_PREPRINT], 1), Confidence.MEDIUM
        )

    def test_two_independent_notable_lab_preprints_reach_high(self):
        # "independent replication" proxy: >=2 distinct notable-lab sources
        self.assertEqual(
            assess_confidence(
                [EvidenceLevel.NOTABLE_LAB_PREPRINT, EvidenceLevel.NOTABLE_LAB_PREPRINT], 2
            ),
            Confidence.HIGH,
        )

    def test_plain_preprint_gives_low(self):
        self.assertEqual(assess_confidence([EvidenceLevel.PREPRINT], 1), Confidence.LOW)

    def test_community_hint_alone_never_accepted_never_high(self):
        # EXEC-010: "COMMUNITY only as discovery hints" - stricter than
        # "capped at LOW": never even reaches acceptance.
        self.assertEqual(
            assess_confidence([EvidenceLevel.COMMUNITY_HINT], 0), Confidence.INSUFFICIENT_EVIDENCE
        )
        self.assertFalse(can_accept_signal([EvidenceLevel.COMMUNITY_HINT]))

    def test_community_hint_plus_primary_evidence_can_still_be_accepted(self):
        self.assertTrue(
            can_accept_signal([EvidenceLevel.COMMUNITY_HINT, EvidenceLevel.PEER_REVIEWED_ACCEPTED])
        )

    def test_zero_evidence_gives_insufficient_evidence(self):
        self.assertEqual(assess_confidence([], 0), Confidence.INSUFFICIENT_EVIDENCE)
        self.assertFalse(can_accept_signal([]))

    def test_never_depends_on_count_alone_for_low_tier_evidence(self):
        # Many plain PREPRINTs (not notable-lab) still only reach LOW -
        # "never on popularity."
        many_preprints = [EvidenceLevel.PREPRINT] * 10
        self.assertEqual(assess_confidence(many_preprints, 0), Confidence.LOW)


if __name__ == "__main__":
    unittest.main()
