import _pathsetup  # noqa: F401
import json
import os
import tempfile
import unittest

from capability_observatory.capture_intake import record_capture
from capability_observatory.storage import AppendOnlyStore
from capability_observatory_executor.human_fallback import (
    HumanSubmissionError,
    parse_human_submission,
)

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")

PANEL_ITEM = {
    "panel_item_id": "C3-009",
    "provider": "provider_c_mcmaster",
    "identity_fields": ["manufacturer", "mpn", "power_rating_hp"],
}


def _load_fixture():
    with open(os.path.join(FIXTURES, "human_fallback_example.json"), "r", encoding="utf-8") as fh:
        return json.load(fh)


class HumanSubmissionParsingTests(unittest.TestCase):
    def test_valid_template_parses(self):
        submission = parse_human_submission(_load_fixture(), identity_field_names=PANEL_ITEM["identity_fields"])
        self.assertEqual(submission.capture_method, "human")
        self.assertEqual(submission.executor, "human:jane-doe")
        self.assertEqual(submission.outcome, "ok")
        self.assertIsNotNone(submission.observation)

    def test_executor_must_use_human_prefix(self):
        data = _load_fixture()
        data["executor"] = "ai:not-actually-a-human"
        with self.assertRaises(HumanSubmissionError):
            parse_human_submission(data)

    def test_missing_required_field_is_rejected(self):
        data = _load_fixture()
        del data["raw_evidence_reference"]
        with self.assertRaises(HumanSubmissionError):
            parse_human_submission(data)

    def test_failure_outcome_never_carries_a_fabricated_observation(self):
        data = _load_fixture()
        data["outcome"] = "provider_access_blocked"
        data["raw_evidence_reference"] = "screenshots/2026-08-16-C3-009-blocked.png"
        submission = parse_human_submission(data, identity_field_names=PANEL_ITEM["identity_fields"])
        self.assertIsNone(submission.observation)


class HumanSubmissionEntersSamePipelineTests(unittest.TestCase):
    """The requirement in the task: human fallback must enter through the
    SAME ingestion validator, not a second one."""

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        d = self._tmpdir.name
        self.captures = AppendOnlyStore(os.path.join(d, "captures.jsonl"), id_field="capture_id")
        self.observations = AppendOnlyStore(os.path.join(d, "observations.jsonl"), id_field="observation_id")
        self.identity_breaks = AppendOnlyStore(os.path.join(d, "identity_breaks.jsonl"), id_field="identity_break_id")

    def tearDown(self):
        self._tmpdir.cleanup()

    def test_human_submission_records_a_capture_and_observation_via_real_c3_code(self):
        submission = parse_human_submission(_load_fixture(), identity_field_names=PANEL_ITEM["identity_fields"])
        result = record_capture(submission.to_c3_submission(), PANEL_ITEM, self.captures, self.observations, self.identity_breaks)
        self.assertTrue(result["capture_written"])
        self.assertTrue(result["observation_written"])
        stored = self.captures.read_all()[0]
        self.assertEqual(stored["executor"], "human:jane-doe")


if __name__ == "__main__":
    unittest.main()
