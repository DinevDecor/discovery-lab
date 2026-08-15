import _pathsetup  # noqa: F401
import json
import os
import tempfile
import unittest

from calendar_arbitrage_watch import intake


def _valid_submission(**overrides):
    base = {
        "candidate_id": "cand-regclock-1",
        "mode": "DISCOVERY",
        "category": "regulatory_clock",
        "title": "Test regulatory clock",
        "evidence_ids": ["ev-1"],
        "shock_forecast": {
            "shock_type": "DATED",
            "date_bound": {"earliest": "2027-01-01", "latest": "2027-01-01", "evidence_status": "OBSERVED"},
            "as_of": "2026-08-15",
        },
    }
    base.update(overrides)
    return base


class ValidateSubmissionTests(unittest.TestCase):
    def test_valid_submission_passes(self):
        result = intake.validate_submission(_valid_submission())
        self.assertTrue(result.ok, result.violations)
        self.assertEqual(result.assessment.candidate_id, "cand-regclock-1")

    def test_missing_required_field_is_rejected(self):
        data = _valid_submission()
        del data["title"]
        result = intake.validate_submission(data)
        self.assertFalse(result.ok)
        self.assertTrue(any("title" in v for v in result.violations))

    def test_unknown_mode_is_rejected(self):
        result = intake.validate_submission(_valid_submission(mode="SPECULATION"))
        self.assertFalse(result.ok)

    def test_unknown_category_is_rejected(self):
        result = intake.validate_submission(_valid_submission(category="not_a_real_category"))
        self.assertFalse(result.ok)

    def test_dated_shock_with_mismatched_interval_is_rejected(self):
        data = _valid_submission()
        data["shock_forecast"]["date_bound"] = {
            "earliest": "2027-01-01", "latest": "2027-06-01", "evidence_status": "OBSERVED",
        }
        result = intake.validate_submission(data)
        self.assertFalse(result.ok)
        self.assertTrue(any("DATED requires earliest == latest" in v for v in result.violations))

    def test_rolling_shock_with_interval_is_accepted(self):
        data = _valid_submission()
        data["shock_forecast"] = {
            "shock_type": "ROLLING",
            "date_bound": {"earliest": "2027-01-01", "latest": "2027-09-01", "evidence_status": "OBSERVED"},
            "as_of": "2026-08-15",
        }
        result = intake.validate_submission(data)
        self.assertTrue(result.ok, result.violations)

    def test_no_evidence_and_no_provenance_is_rejected(self):
        data = _valid_submission()
        del data["evidence_ids"]
        result = intake.validate_submission(data)
        self.assertFalse(result.ok)

    def test_provenance_alone_satisfies_the_evidence_requirement(self):
        data = _valid_submission()
        del data["evidence_ids"]
        data["provenance"] = ["human research session, 2026-08-15"]
        result = intake.validate_submission(data)
        self.assertTrue(result.ok, result.violations)

    def test_load_submissions_single_object(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "sub.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(_valid_submission(), f)
            loaded = intake.load_submissions(path)
            self.assertEqual(len(loaded), 1)

    def test_load_submissions_array(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "sub.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump([_valid_submission(), _valid_submission(candidate_id="cand-2")], f)
            loaded = intake.load_submissions(path)
            self.assertEqual(len(loaded), 2)

    def test_load_submissions_malformed_json_raises_intake_error(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "bad.json")
            with open(path, "w", encoding="utf-8") as f:
                f.write("{not valid json")
            with self.assertRaises(intake.IntakeError):
                intake.load_submissions(path)


if __name__ == "__main__":
    unittest.main()
