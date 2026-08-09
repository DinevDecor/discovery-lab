import _pathsetup  # noqa: F401
import unittest

from capability_observatory import metrics


def _obs(count, target=15):
    return {"observed_count": count, "meets_target": count >= target}


def _success(rate, target=0.60):
    return {"rate": rate, "meets_target": rate >= target}


def _backlog(count, trigger=3):
    return {"unresolved_item_count": count, "exceeds_trigger": count > trigger}


class StopRuleATests(unittest.TestCase):
    def test_fires_when_both_capture_success_and_observability_are_below_target(self):
        result = metrics.evaluate_stop_rules(_obs(10), _success(0.40), _backlog(0))
        self.assertTrue(result["rule_a_capture_mechanism_failing"])
        self.assertTrue(result["kill_or_redesign"])

    def test_does_not_fire_when_only_capture_success_is_low(self):
        # Observability still healthy -- capture success alone is not enough.
        result = metrics.evaluate_stop_rules(_obs(16), _success(0.40), _backlog(0))
        self.assertFalse(result["rule_a_capture_mechanism_failing"])

    def test_does_not_fire_when_only_observability_is_low(self):
        result = metrics.evaluate_stop_rules(_obs(10), _success(0.80), _backlog(0))
        self.assertFalse(result["rule_a_capture_mechanism_failing"])

    def test_does_not_fire_when_both_are_healthy(self):
        result = metrics.evaluate_stop_rules(_obs(18), _success(0.90), _backlog(0))
        self.assertFalse(result["rule_a_capture_mechanism_failing"])
        self.assertFalse(result["kill_or_redesign"])


class StopRuleBTests(unittest.TestCase):
    def test_fires_above_three_unresolved_identity_breaks(self):
        result = metrics.evaluate_stop_rules(_obs(18), _success(0.90), _backlog(4))
        self.assertTrue(result["rule_b_identity_design_failing"])
        self.assertTrue(result["kill_or_redesign"])

    def test_does_not_fire_at_exactly_three(self):
        result = metrics.evaluate_stop_rules(_obs(18), _success(0.90), _backlog(3))
        self.assertFalse(result["rule_b_identity_design_failing"])
        self.assertFalse(result["kill_or_redesign"])

    def test_fires_independently_of_rule_a(self):
        # Capture mechanism perfectly healthy, but identity design is not.
        result = metrics.evaluate_stop_rules(_obs(20), _success(1.0), _backlog(5))
        self.assertFalse(result["rule_a_capture_mechanism_failing"])
        self.assertTrue(result["rule_b_identity_design_failing"])
        self.assertTrue(result["kill_or_redesign"])


class ZeroStateChangeDoesNotKillTests(unittest.TestCase):
    def test_a_healthy_run_with_zero_state_changes_is_not_killed(self):
        """state_changes is intentionally not an input to evaluate_stop_rules
        at all -- this test proves a run with perfect observability, capture
        success, and zero identity backlog is never killed, regardless of
        how little price/lead-time movement occurred."""
        healthy_obs = _obs(20)
        healthy_success = _success(1.0)
        healthy_backlog = _backlog(0)

        # Zero state changes would be reflected here if it were ever wired in:
        zero_changes = metrics.state_changes([], [])
        self.assertEqual(zero_changes["total_raw_state_changes"], 0)

        result = metrics.evaluate_stop_rules(healthy_obs, healthy_success, healthy_backlog)
        self.assertFalse(result["kill_or_redesign"])
        self.assertIn("does not, by itself, trigger", result["note"])


if __name__ == "__main__":
    unittest.main()
