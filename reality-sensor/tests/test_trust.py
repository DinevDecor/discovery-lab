import _pathsetup  # noqa: F401
import unittest

from reality_sensor.models import Confidence, TrustLevel, Urgency
from reality_sensor.trust import assess_confidence, assess_urgency


class TestConfidenceRules(unittest.TestCase):
    def test_primary_evidence_gives_high(self):
        self.assertEqual(assess_confidence([TrustLevel.PRIMARY]), Confidence.HIGH)

    def test_official_evidence_gives_high(self):
        self.assertEqual(assess_confidence([TrustLevel.OFFICIAL]), Confidence.HIGH)

    def test_community_alone_never_gives_high(self):
        # The one explicit rule EXEC-008 states: "Never assign HIGH
        # confidence from COMMUNITY alone."
        self.assertEqual(assess_confidence([TrustLevel.COMMUNITY]), Confidence.LOW)
        self.assertEqual(
            assess_confidence([TrustLevel.COMMUNITY, TrustLevel.COMMUNITY, TrustLevel.COMMUNITY]),
            Confidence.LOW,
        )

    def test_community_plus_primary_can_reach_high(self):
        # The rule is "from COMMUNITY alone" — a primary source present
        # alongside community chatter still supports HIGH.
        self.assertEqual(
            assess_confidence([TrustLevel.COMMUNITY, TrustLevel.PRIMARY]), Confidence.HIGH
        )

    def test_research_alone_gives_medium_not_high(self):
        self.assertEqual(assess_confidence([TrustLevel.RESEARCH]), Confidence.MEDIUM)

    def test_zero_evidence_gives_insufficient_evidence(self):
        self.assertEqual(assess_confidence([]), Confidence.INSUFFICIENT_EVIDENCE)

    def test_unknown_alone_gives_low_not_high(self):
        self.assertEqual(assess_confidence([TrustLevel.UNKNOWN]), Confidence.LOW)


class TestUrgency(unittest.TestCase):
    def test_deprecation_keyword_forces_high_urgency(self):
        self.assertEqual(
            assess_urgency("AGENT_INFRASTRUCTURE", Confidence.HIGH, "This API is now deprecated"),
            Urgency.HIGH,
        )

    def test_insufficient_evidence_never_urgent(self):
        self.assertEqual(
            assess_urgency("RESEARCH", Confidence.INSUFFICIENT_EVIDENCE, "some vague claim"),
            Urgency.LOW,
        )

    def test_high_confidence_without_urgent_keywords_is_medium(self):
        self.assertEqual(
            assess_urgency("FOUNDATION_MODEL_RELEASES", Confidence.HIGH, "new model launched"),
            Urgency.MEDIUM,
        )


if __name__ == "__main__":
    unittest.main()
