import _pathsetup  # noqa: F401
import os
import tempfile
import unittest

from capability_observatory.capture_intake import record_capture
from capability_observatory.storage import AppendOnlyStore
from capability_observatory_executor.envelope import EnvelopeValidationError, ExecutorSubmission

PANEL_ITEM = {
    "panel_item_id": "C3-010",
    "provider": "provider_d_digikey",
    "identity_fields": ["manufacturer", "mpn", "package"],
}


class RoundTripThroughRealC3ValidatorTests(unittest.TestCase):
    """Proves the envelope this executor produces is actually accepted by
    C3's own, unmodified validate_submission/record_capture -- not just
    internally self-consistent."""

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        d = self._tmpdir.name
        self.captures = AppendOnlyStore(os.path.join(d, "captures.jsonl"), id_field="capture_id")
        self.observations = AppendOnlyStore(os.path.join(d, "observations.jsonl"), id_field="observation_id")
        self.identity_breaks = AppendOnlyStore(os.path.join(d, "identity_breaks.jsonl"), id_field="identity_break_id")

    def tearDown(self):
        self._tmpdir.cleanup()

    def test_ok_submission_round_trips_and_produces_an_observation(self):
        submission = ExecutorSubmission(
            panel_item_id="C3-010", provider="provider_d_digikey",
            requested_url="https://api.digikey.com/products/v4/search/keyword",
            fetched_at="2026-08-16T12:00:00Z", capture_method="api",
            executor="automation:gh-actions-executor:v1", outcome="ok",
            raw_payload='{"Product": {"ManufacturerProductNumber": "ABC"}}',
            observation={
                "price": 3.42, "currency": "USD", "unit": "each", "quantity_basis": "each_qty1",
                "lead_time_days": 56.0, "availability": "in_stock", "quote_type": "list_price",
                "identity_values": {"manufacturer": "STMicroelectronics", "mpn": "ABC", "package": "LQFP-48"},
            },
        )
        result = record_capture(submission.to_c3_submission(), PANEL_ITEM, self.captures, self.observations, self.identity_breaks)
        self.assertTrue(result["capture_written"])
        self.assertTrue(result["observation_written"])

    def test_credentials_error_round_trips_without_an_observation(self):
        submission = ExecutorSubmission(
            panel_item_id="C3-010", provider="provider_d_digikey",
            requested_url="https://www.digikey.com/", fetched_at="2026-08-16T12:00:00Z",
            capture_method="api", executor="automation:gh-actions-executor:v1",
            outcome="credentials_error", error_category="missing_credentials",
        )
        result = record_capture(submission.to_c3_submission(), PANEL_ITEM, self.captures, self.observations, self.identity_breaks)
        self.assertTrue(result["capture_written"])
        self.assertFalse(result["observation_written"])
        stored = self.captures.read_all()[0]
        self.assertEqual(stored["capture_outcome"], "credentials_error")
        self.assertIn("error_category=missing_credentials", stored["notes"])


class ValidationTests(unittest.TestCase):
    def test_rejects_unknown_capture_method(self):
        with self.assertRaises(EnvelopeValidationError):
            ExecutorSubmission(
                panel_item_id="C3-010", provider="provider_d_digikey", requested_url="https://x.test",
                fetched_at="2026-08-16T12:00:00Z", capture_method="browser-stealth",
                executor="automation:x", outcome="ok", raw_payload="x",
            ).validate()

    def test_rejects_unknown_outcome(self):
        with self.assertRaises(EnvelopeValidationError):
            ExecutorSubmission(
                panel_item_id="C3-010", provider="provider_d_digikey", requested_url="https://x.test",
                fetched_at="2026-08-16T12:00:00Z", capture_method="api",
                executor="automation:x", outcome="totally_fine_actually", raw_payload="x",
            ).validate()

    def test_rejects_observation_on_a_failure_outcome(self):
        with self.assertRaises(EnvelopeValidationError):
            ExecutorSubmission(
                panel_item_id="C3-010", provider="provider_d_digikey", requested_url="https://x.test",
                fetched_at="2026-08-16T12:00:00Z", capture_method="api",
                executor="automation:x", outcome="timeout",
                observation={"price": 1.0, "identity_values": {}},
            ).validate()

    def test_rejects_completely_empty_evidence(self):
        with self.assertRaises(EnvelopeValidationError):
            ExecutorSubmission(
                panel_item_id="C3-010", provider="provider_d_digikey", requested_url="https://x.test",
                fetched_at="2026-08-16T12:00:00Z", capture_method="api",
                executor="automation:x", outcome="timeout",
            ).validate()

    def test_error_category_alone_is_sufficient_evidence(self):
        # A timeout genuinely has no raw bytes -- error_category is enough,
        # to_c3_submission() synthesizes an honest raw_content description.
        submission = ExecutorSubmission(
            panel_item_id="C3-010", provider="provider_d_digikey", requested_url="https://x.test",
            fetched_at="2026-08-16T12:00:00Z", capture_method="api",
            executor="automation:x", outcome="timeout", error_category="oauth_token_timeout",
        )
        submission.validate()
        c3_submission = submission.to_c3_submission()
        self.assertIn("error_category=oauth_token_timeout", c3_submission["raw_content"])


class NotesCompositionTests(unittest.TestCase):
    def test_final_url_only_appears_when_it_differs_from_requested(self):
        same = ExecutorSubmission(
            panel_item_id="C3-010", provider="provider_d_digikey", requested_url="https://x.test",
            final_url="https://x.test", fetched_at="2026-08-16T12:00:00Z", capture_method="html",
            executor="automation:x", outcome="ok", raw_payload="<html></html>",
            observation={"identity_values": {}},
        )
        self.assertNotIn("final_url=", same.to_c3_submission()["notes"])

        redirected = ExecutorSubmission(
            panel_item_id="C3-010", provider="provider_d_digikey", requested_url="https://x.test",
            final_url="https://x.test/redirected", fetched_at="2026-08-16T12:00:00Z", capture_method="html",
            executor="automation:x", outcome="ok", raw_payload="<html></html>",
            observation={"identity_values": {}},
        )
        self.assertIn("final_url=https://x.test/redirected", redirected.to_c3_submission()["notes"])


if __name__ == "__main__":
    unittest.main()
