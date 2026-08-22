import _pathsetup  # noqa: F401
import os
import tempfile
import unittest

from capability_observatory.capture_intake import record_capture
from capability_observatory.storage import AppendOnlyStore
from capability_observatory_executor.envelope import ExecutorSubmission
from capability_observatory_executor.health import ProviderAttempt, classify_attempt
from capability_observatory_executor.outcomes import is_executor_side_failure, is_provider_side_failure

PANEL_ITEM = {
    "panel_item_id": "C3-001",
    "provider": "provider_a_automationdirect",
    "identity_fields": ["manufacturer", "mpn", "io_count"],
}


class InfrastructureFailureIsNotMarketEvidenceTests(unittest.TestCase):
    """The core regression test for the week-2026-08-09 incident: an
    executor-side network failure must never produce an Observation, and
    must be distinguishable from a provider-side denial -- not folded into
    one ambiguous bucket the way the original 20 captures were."""

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        d = self._tmpdir.name
        self.captures = AppendOnlyStore(os.path.join(d, "captures.jsonl"), id_field="capture_id")
        self.observations = AppendOnlyStore(os.path.join(d, "observations.jsonl"), id_field="observation_id")
        self.identity_breaks = AppendOnlyStore(os.path.join(d, "identity_breaks.jsonl"), id_field="identity_break_id")

    def tearDown(self):
        self._tmpdir.cleanup()

    def test_executor_network_blocked_never_produces_an_observation(self):
        submission = ExecutorSubmission(
            panel_item_id="C3-001", provider="provider_a_automationdirect",
            requested_url="https://www.automationdirect.com/", fetched_at="2026-08-16T07:30:00Z",
            capture_method="html", executor="automation:gh-actions-executor:v1",
            outcome="executor_network_blocked", error_category="probe_failed",
        )
        result = record_capture(submission.to_c3_submission(), PANEL_ITEM, self.captures, self.observations, self.identity_breaks)
        self.assertTrue(result["capture_written"])
        self.assertFalse(result["observation_written"])

    def test_provider_and_executor_blocks_are_distinguishable_by_outcome(self):
        executor_side = ExecutorSubmission(
            panel_item_id="C3-001", provider="provider_a_automationdirect",
            requested_url="https://www.automationdirect.com/", fetched_at="2026-08-16T07:30:00Z",
            capture_method="html", executor="automation:x", outcome="executor_network_blocked",
            error_category="probe_failed",
        ).to_c3_submission()
        provider_side = ExecutorSubmission(
            panel_item_id="C3-001", provider="provider_a_automationdirect",
            requested_url="https://www.automationdirect.com/", fetched_at="2026-08-16T08:30:00Z",
            capture_method="html", executor="automation:x", outcome="provider_access_blocked",
            raw_payload="<html>Access denied - please complete a CAPTCHA</html>",
        ).to_c3_submission()

        self.assertNotEqual(executor_side["capture_outcome"], provider_side["capture_outcome"])
        self.assertTrue(is_executor_side_failure(executor_side["capture_outcome"]))
        self.assertTrue(is_provider_side_failure(provider_side["capture_outcome"]))

        record_capture(executor_side, PANEL_ITEM, self.captures, self.observations, self.identity_breaks)
        record_capture(provider_side, PANEL_ITEM, self.captures, self.observations, self.identity_breaks)
        stored = {row["capture_outcome"] for row in self.captures.read_all()}
        self.assertEqual(stored, {"executor_network_blocked", "provider_access_blocked"})


class HealthClassificationTests(unittest.TestCase):
    def test_executor_side_failure_classifies_as_executor_failure(self):
        self.assertEqual(classify_attempt("html", "executor_network_blocked"), "EXECUTOR_FAILURE")
        self.assertEqual(classify_attempt("api", "timeout"), "EXECUTOR_FAILURE")
        self.assertEqual(classify_attempt("api", "credentials_error"), "EXECUTOR_FAILURE")

    def test_provider_side_failure_classifies_as_provider_blocked(self):
        self.assertEqual(classify_attempt("html", "provider_access_blocked"), "PROVIDER_BLOCKED")

    def test_success_classifies_as_automated_ok_for_non_human_methods(self):
        self.assertEqual(classify_attempt("api", "ok"), "AUTOMATED_OK")
        self.assertEqual(classify_attempt("html", "unavailable"), "AUTOMATED_OK")

    def test_human_method_always_classifies_as_human_fallback_required(self):
        self.assertEqual(classify_attempt("human", "ok"), "HUMAN_FALLBACK_REQUIRED")
        self.assertEqual(classify_attempt("human", "not_attempted"), "HUMAN_FALLBACK_REQUIRED")


if __name__ == "__main__":
    unittest.main()
