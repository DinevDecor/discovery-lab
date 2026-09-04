import _pathsetup  # noqa: F401
import unittest

from capability_observatory.models import CAPTURE_OUTCOMES, OBSERVATION_PRODUCING_OUTCOMES
from capability_observatory_executor import outcomes


class BackwardCompatibilityTests(unittest.TestCase):
    def test_all_legacy_outcomes_still_present(self):
        for legacy in ("ok", "unavailable", "access_blocked", "parse_error", "source_missing"):
            self.assertIn(legacy, CAPTURE_OUTCOMES)

    def test_legacy_observation_producing_outcomes_unchanged(self):
        self.assertEqual(OBSERVATION_PRODUCING_OUTCOMES, ("ok", "unavailable"))

    def test_access_blocked_is_classified_legacy_ambiguous(self):
        self.assertTrue(outcomes.is_legacy_ambiguous("access_blocked"))
        self.assertFalse(outcomes.is_executor_side_failure("access_blocked"))
        self.assertFalse(outcomes.is_provider_side_failure("access_blocked"))


class NewOutcomeTests(unittest.TestCase):
    def test_new_outcomes_are_present(self):
        for new in ("provider_access_blocked", "executor_network_blocked", "timeout",
                    "credentials_error", "api_quota_error"):
            self.assertIn(new, CAPTURE_OUTCOMES)

    def test_new_outcomes_never_produce_observations(self):
        for new in ("provider_access_blocked", "executor_network_blocked", "timeout",
                    "credentials_error", "api_quota_error"):
            self.assertNotIn(new, OBSERVATION_PRODUCING_OUTCOMES)

    def test_executor_side_vs_provider_side_are_disjoint(self):
        self.assertEqual(set(outcomes.EXECUTOR_SIDE_OUTCOMES) & set(outcomes.PROVIDER_SIDE_OUTCOMES), set())

    def test_every_capture_outcome_is_classified_exactly_once(self):
        classified = (
            set(outcomes.EXECUTOR_SIDE_OUTCOMES)
            | set(outcomes.PROVIDER_SIDE_OUTCOMES)
            | set(outcomes.LEGACY_AMBIGUOUS_OUTCOMES)
            | set(OBSERVATION_PRODUCING_OUTCOMES)
        )
        self.assertEqual(classified, set(CAPTURE_OUTCOMES))

    def test_is_success_matches_observation_producing_outcomes(self):
        for outcome in CAPTURE_OUTCOMES:
            self.assertEqual(outcomes.is_success(outcome), outcome in OBSERVATION_PRODUCING_OUTCOMES)


if __name__ == "__main__":
    unittest.main()
