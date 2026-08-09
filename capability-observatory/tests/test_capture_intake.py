import _pathsetup  # noqa: F401
import os
import tempfile
import unittest

from capability_observatory.capture_intake import CaptureValidationError, record_capture
from capability_observatory.storage import AppendOnlyStore

PANEL_ITEM = {
    "panel_item_id": "C3-001",
    "provider": "provider_a_automationdirect",
    "identity_fields": ["manufacturer", "mpn", "io_count"],
}


def base_submission(**overrides):
    submission = {
        "panel_item_id": "C3-001",
        "source": "provider_a_automationdirect",
        "source_url": "https://example-distributor.test/product/abc-123",
        "fetched_at": "2026-08-09T12:00:00Z",
        "capture_outcome": "ok",
        "executor": "test-executor",
        "raw_content": "<html>Price: $199.00, Ships in 5 days</html>",
        "observation": {
            "price": 199.0,
            "currency": "USD",
            "unit": "each",
            "quantity_basis": "each_qty1",
            "lead_time_days": 5,
            "availability": "in_stock",
            "quote_type": "list_price",
            "identity_values": {"manufacturer": "Acme", "mpn": "ABC-123", "io_count": 16},
        },
    }
    submission.update(overrides)
    return submission


class CaptureIntakeTestCase(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        d = self._tmpdir.name
        self.captures = AppendOnlyStore(os.path.join(d, "captures.jsonl"), id_field="capture_id")
        self.observations = AppendOnlyStore(os.path.join(d, "observations.jsonl"), id_field="observation_id")
        self.identity_breaks = AppendOnlyStore(os.path.join(d, "identity_breaks.jsonl"), id_field="identity_break_id")

    def tearDown(self):
        self._tmpdir.cleanup()

    def _record(self, submission):
        return record_capture(submission, PANEL_ITEM, self.captures, self.observations, self.identity_breaks)


class OkCaptureTests(CaptureIntakeTestCase):
    def test_ok_capture_creates_a_capture_and_an_observation(self):
        result = self._record(base_submission())
        self.assertTrue(result["capture_written"])
        self.assertTrue(result["observation_written"])
        self.assertIsNone(result["identity_break_id"])
        self.assertEqual(self.captures.known_count, 1)
        self.assertEqual(self.observations.known_count, 1)

    def test_observation_carries_the_expected_fields(self):
        self._record(base_submission())
        row = self.observations.read_all()[0]
        self.assertEqual(row["price"], 199.0)
        self.assertEqual(row["currency"], "USD")
        self.assertEqual(row["lead_time_days"], 5)
        self.assertEqual(row["availability"], "in_stock")
        self.assertEqual(row["origin"], "captured")
        self.assertIsNotNone(row["spec_fingerprint"])


class FailedCaptureTests(CaptureIntakeTestCase):
    def test_access_blocked_capture_is_persisted_without_an_observation(self):
        submission = base_submission(
            capture_outcome="access_blocked",
            raw_content="<html>Access denied - 403</html>",
            notes="bot detection page returned",
        )
        del submission["observation"]
        result = self._record(submission)
        self.assertTrue(result["capture_written"])
        self.assertFalse(result["observation_written"])
        self.assertIsNone(result["observation_id"])
        self.assertEqual(self.captures.known_count, 1)
        self.assertEqual(self.observations.known_count, 0)
        stored = self.captures.read_all()[0]
        self.assertEqual(stored["capture_outcome"], "access_blocked")

    def test_parse_error_capture_is_persisted_without_an_observation(self):
        submission = base_submission(
            capture_outcome="parse_error",
            raw_content="<html>totally different layout, extractor could not find price</html>",
        )
        del submission["observation"]
        result = self._record(submission)
        self.assertTrue(result["capture_written"])
        self.assertFalse(result["observation_written"])

    def test_source_missing_capture_is_persisted_without_an_observation(self):
        submission = base_submission(capture_outcome="source_missing", raw_content="404 Not Found")
        del submission["observation"]
        result = self._record(submission)
        self.assertTrue(result["capture_written"])
        self.assertFalse(result["observation_written"])

    def test_a_failed_capture_never_becomes_a_missing_record(self):
        """Failure is longitudinal evidence -- it is never silently dropped."""
        submission = base_submission(capture_outcome="access_blocked", raw_content="blocked")
        del submission["observation"]
        self._record(submission)
        self.assertEqual(self.captures.known_count, 1)


class UnavailableOutcomeTests(CaptureIntakeTestCase):
    def test_unavailable_outcome_still_produces_an_observation(self):
        submission = base_submission(
            capture_outcome="unavailable",
            raw_content="<html>This item has been discontinued.</html>",
            observation={
                "availability": "discontinued",
                "identity_values": {"manufacturer": "Acme", "mpn": "ABC-123", "io_count": 16},
            },
        )
        result = self._record(submission)
        self.assertTrue(result["observation_written"])
        row = self.observations.read_all()[0]
        self.assertEqual(row["availability"], "discontinued")
        self.assertIsNone(row["price"])  # never fabricated


class NoHallucinationTests(CaptureIntakeTestCase):
    def test_missing_optional_fields_stay_null_not_defaulted_to_a_guess(self):
        submission = base_submission(
            observation={
                "price": 199.0,
                # currency, unit, quantity_basis, lead_time_days deliberately absent
                "availability": "in_stock",
                "identity_values": {"manufacturer": "Acme", "mpn": "ABC-123", "io_count": 16},
            }
        )
        self._record(submission)
        row = self.observations.read_all()[0]
        self.assertIsNone(row["currency"])
        self.assertIsNone(row["unit"])
        self.assertIsNone(row["quantity_basis"])
        self.assertIsNone(row["lead_time_days"])

    def test_missing_availability_defaults_to_the_explicit_unknown_value_not_a_guess(self):
        submission = base_submission(
            observation={
                "price": 199.0,
                "identity_values": {"manufacturer": "Acme", "mpn": "ABC-123", "io_count": 16},
            }
        )
        self._record(submission)
        row = self.observations.read_all()[0]
        self.assertEqual(row["availability"], "unknown")

    def test_incomplete_identity_fields_yield_null_fingerprint_not_a_placeholder(self):
        submission = base_submission(
            observation={
                "price": 199.0,
                "availability": "in_stock",
                "identity_values": {"manufacturer": "Acme"},  # mpn, io_count missing
            }
        )
        self._record(submission)
        row = self.observations.read_all()[0]
        self.assertIsNone(row["spec_fingerprint"])


class IdentityContinuityTests(CaptureIntakeTestCase):
    def test_first_ever_observation_creates_no_identity_break(self):
        result = self._record(base_submission())
        self.assertIsNone(result["identity_break_id"])
        self.assertEqual(self.identity_breaks.known_count, 0)

    def test_repeated_identical_identity_does_not_create_a_break(self):
        self._record(base_submission(fetched_at="2026-08-09T12:00:00Z"))
        second = base_submission(fetched_at="2026-08-16T12:00:00Z")
        second["observation"]["price"] = 210.0  # price moved, identity did not
        result = self._record(second)
        self.assertIsNone(result["identity_break_id"])
        self.assertEqual(self.identity_breaks.known_count, 0)
        self.assertEqual(self.observations.known_count, 2)

    def test_fingerprint_change_creates_an_identity_break(self):
        self._record(base_submission(fetched_at="2026-08-09T12:00:00Z"))
        changed = base_submission(fetched_at="2026-08-16T12:00:00Z")
        changed["observation"]["identity_values"]["mpn"] = "ABC-999"  # different part
        result = self._record(changed)
        self.assertIsNotNone(result["identity_break_id"])
        self.assertEqual(self.identity_breaks.known_count, 1)
        break_row = self.identity_breaks.read_all()[0]
        self.assertEqual(break_row["status"], "UNRESOLVED")
        self.assertEqual(break_row["panel_item_id"], "C3-001")
        self.assertNotEqual(break_row["previous_fingerprint"], break_row["new_fingerprint"])

    def test_fingerprint_change_does_not_silently_continue_the_series(self):
        """Both observations remain on record under their own fingerprints --
        the break makes the discontinuity visible, it does not merge or
        drop either observation."""
        self._record(base_submission(fetched_at="2026-08-09T12:00:00Z"))
        changed = base_submission(fetched_at="2026-08-16T12:00:00Z")
        changed["observation"]["identity_values"]["mpn"] = "ABC-999"
        self._record(changed)

        rows = sorted(self.observations.read_all(), key=lambda r: r["observed_at"])
        self.assertEqual(len(rows), 2)
        self.assertNotEqual(rows[0]["spec_fingerprint"], rows[1]["spec_fingerprint"])
        # No field anywhere asserts these two rows are the same continuous
        # entity -- that assertion would have to come from a separate,
        # future, human/analyst-authored resolution, which this module
        # never writes.

    def test_incomplete_identity_never_triggers_a_break(self):
        self._record(base_submission(fetched_at="2026-08-09T12:00:00Z"))
        incomplete = base_submission(fetched_at="2026-08-16T12:00:00Z")
        incomplete["observation"]["identity_values"] = {"manufacturer": "Acme"}  # incomplete
        result = self._record(incomplete)
        self.assertIsNone(result["identity_break_id"])
        self.assertEqual(self.identity_breaks.known_count, 0)

    def test_resubmitting_the_identical_capture_is_idempotent(self):
        submission = base_submission()
        first = self._record(submission)
        second = self._record(submission)
        self.assertTrue(first["capture_written"])
        self.assertFalse(second["capture_written"])
        self.assertEqual(self.captures.known_count, 1)
        self.assertEqual(self.observations.known_count, 1)

    def test_idempotent_resubmission_after_a_break_does_not_double_count_it(self):
        self._record(base_submission(fetched_at="2026-08-09T12:00:00Z"))
        changed = base_submission(fetched_at="2026-08-16T12:00:00Z")
        changed["observation"]["identity_values"]["mpn"] = "ABC-999"
        self._record(changed)
        self._record(changed)  # identical resubmission
        self.assertEqual(self.identity_breaks.known_count, 1)


class ValidationTests(CaptureIntakeTestCase):
    def test_unknown_capture_outcome_is_rejected(self):
        with self.assertRaises(CaptureValidationError):
            self._record(base_submission(capture_outcome="totally_fine_actually"))

    def test_missing_required_field_is_rejected(self):
        submission = base_submission()
        del submission["fetched_at"]
        with self.assertRaises(CaptureValidationError):
            self._record(submission)

    def test_observation_payload_on_a_non_observation_producing_outcome_is_rejected(self):
        submission = base_submission(capture_outcome="parse_error")
        # observation payload deliberately left in place -- should be rejected
        with self.assertRaises(CaptureValidationError):
            self._record(submission)

    def test_invalid_availability_value_is_rejected(self):
        submission = base_submission()
        submission["observation"]["availability"] = "probably_fine"
        with self.assertRaises(CaptureValidationError):
            self._record(submission)

    def test_invalid_quote_type_is_rejected(self):
        submission = base_submission()
        submission["observation"]["quote_type"] = "negotiated"
        with self.assertRaises(CaptureValidationError):
            self._record(submission)

    def test_mismatched_panel_item_id_is_rejected(self):
        submission = base_submission(panel_item_id="C3-999")
        with self.assertRaises(CaptureValidationError):
            self._record(submission)


if __name__ == "__main__":
    unittest.main()
