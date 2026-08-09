import os, sys, unittest
ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(ROOT, "src"))
from ca_agents.same_mechanism_gate import GateAnomaly, profile_anomaly, _coerce_confidence


class FixedJudge:
    """Returns a fixed profile() response regardless of the prompt - only
    used to exercise profile_anomaly()'s field coercion, not gate logic."""
    def __init__(self, confidence):
        self._confidence = confidence

    def profile(self, prompt):
        return {
            "hidden_function": "reconcile",
            "failure_class": "absence",
            "failure_mechanism": "m",
            "repair": "r",
            "confidence": self._confidence,
        }

    def counterfactual(self, prompt):
        raise AssertionError("not exercised by these tests")


def mk():
    return GateAnomaly("A", "test", "process", "pain", "carrier", "failure_mode", 2, 0.8)


class TestCoerceConfidence(unittest.TestCase):
    def test_plain_float_unchanged(self):
        self.assertEqual(_coerce_confidence(0.85), 0.85)

    def test_int_unchanged(self):
        self.assertEqual(_coerce_confidence(1), 1.0)

    def test_percent_string_converted_to_fraction(self):
        # Real production crash: judge.profile() returned "85%" instead of
        # 0.85, and float("85%") raises ValueError, crashing the whole run.
        self.assertEqual(_coerce_confidence("85%"), 0.85)

    def test_numeric_string_without_percent(self):
        self.assertEqual(_coerce_confidence("0.9"), 0.9)

    def test_garbage_falls_back_to_zero_not_crash(self):
        self.assertEqual(_coerce_confidence("very confident"), 0.0)

    def test_none_falls_back_to_zero(self):
        self.assertEqual(_coerce_confidence(None), 0.0)


class TestProfileAnomalyToleratesPercentConfidence(unittest.TestCase):
    def test_percent_confidence_does_not_crash_profile_anomaly(self):
        profile = profile_anomaly(mk(), FixedJudge("85%"))
        self.assertEqual(profile.confidence, 0.85)

    def test_plain_float_confidence_still_works(self):
        profile = profile_anomaly(mk(), FixedJudge(0.85))
        self.assertEqual(profile.confidence, 0.85)


if __name__ == "__main__":
    unittest.main()
