import _pathsetup  # noqa: F401
import os
import tempfile
import unittest

from capability_observatory.capture_intake import record_capture
from capability_observatory.storage import AppendOnlyStore
from capability_observatory_executor.envelope import ExecutorSubmission

PANEL_ITEM = {
    "panel_item_id": "C3-010",
    "provider": "provider_d_digikey",
    "identity_fields": ["manufacturer", "mpn", "package"],
}


class IdempotentRerunTests(unittest.TestCase):
    """C3's own idempotency (deterministic capture_id, AppendOnlyStore
    no-op on a known id) is untouched by this package -- these tests prove
    the executor's envelope doesn't break it when a submission produced by
    this package is processed twice, e.g. a GitHub Actions job re-dispatched
    after a crash reprocesses the same already-written incoming/ file."""

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        d = self._tmpdir.name
        self.captures = AppendOnlyStore(os.path.join(d, "captures.jsonl"), id_field="capture_id")
        self.observations = AppendOnlyStore(os.path.join(d, "observations.jsonl"), id_field="observation_id")
        self.identity_breaks = AppendOnlyStore(os.path.join(d, "identity_breaks.jsonl"), id_field="identity_break_id")

    def tearDown(self):
        self._tmpdir.cleanup()

    def _submission(self):
        return ExecutorSubmission(
            panel_item_id="C3-010", provider="provider_d_digikey",
            requested_url="https://api.digikey.com/products/v4/search/keyword",
            fetched_at="2026-08-16T12:00:00Z", capture_method="api",
            executor="automation:gh-actions-executor:v1", outcome="ok",
            raw_payload='{"Product": {"ManufacturerProductNumber": "ABC"}}',
            observation={
                "price": 3.42, "currency": "USD", "availability": "in_stock", "quote_type": "list_price",
                "identity_values": {"manufacturer": "STMicroelectronics", "mpn": "ABC", "package": "LQFP-48"},
            },
        )

    def test_rerunning_the_same_run_output_does_not_duplicate_a_capture(self):
        submission = self._submission().to_c3_submission()
        first = record_capture(submission, PANEL_ITEM, self.captures, self.observations, self.identity_breaks)
        second = record_capture(submission, PANEL_ITEM, self.captures, self.observations, self.identity_breaks)

        self.assertTrue(first["capture_written"])
        self.assertFalse(second["capture_written"])
        self.assertEqual(self.captures.known_count, 1)
        self.assertEqual(self.observations.known_count, 1)

    def test_two_genuinely_different_fetch_attempts_are_both_kept(self):
        """A retry at a DIFFERENT fetched_at (a distinct real attempt, not a
        re-processing of the same output) is legitimate new evidence and is
        NOT deduplicated -- only literally-identical (id, fetched_at,
        content-hash) resubmissions are."""
        first = self._submission()
        second_dict = self._submission().to_c3_submission()
        second_dict["fetched_at"] = "2026-08-16T13:00:00Z"

        record_capture(first.to_c3_submission(), PANEL_ITEM, self.captures, self.observations, self.identity_breaks)
        record_capture(second_dict, PANEL_ITEM, self.captures, self.observations, self.identity_breaks)

        self.assertEqual(self.captures.known_count, 2)


if __name__ == "__main__":
    unittest.main()
