import _pathsetup  # noqa: F401
import json
import tempfile
import unittest
from pathlib import Path

from research_sensor.capture import load_raw_captures


class TestMalformedFeeds(unittest.TestCase):
    def test_not_valid_json_is_reported_not_raised(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text("{not valid json", encoding="utf-8")
            captures, reasons = load_raw_captures(path)
            self.assertEqual(captures, [])
            self.assertIn("not valid JSON", reasons[0])

    def test_not_a_list_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text(json.dumps({"not": "a list"}), encoding="utf-8")
            captures, reasons = load_raw_captures(path)
            self.assertEqual(captures, [])
            self.assertIn("must be a JSON list", reasons[0])

    def test_missing_required_field_is_skipped_not_fatal(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "captures.json"
            path.write_text(json.dumps([{"title": "X"}]), encoding="utf-8")
            captures, reasons = load_raw_captures(path)
            self.assertEqual(captures, [])
            self.assertIn("missing required field", reasons[0])

    def test_one_good_one_bad_entry_keeps_the_good_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "captures.json"
            good = {
                "title": "A Real Paper",
                "authors": ["A. Researcher"],
                "publication": "arXiv",
                "date": "2026-07-10",
                "source_name": "arXiv cs.AI Recent",
                "source_url": "https://arxiv.org/abs/1234.5678",
                "source_trust": "PRIMARY",
                "evidence_level": "PREPRINT",
                "domain": "AI_FOR_SCIENTIFIC_DISCOVERY",
                "raw_abstract": "We propose a method.",
                "problem_addressed": "slow hypothesis generation",
                "main_contribution": "a faster method",
            }
            path.write_text(json.dumps([good, {"bad": "entry"}]), encoding="utf-8")
            captures, reasons = load_raw_captures(path)
            self.assertEqual(len(captures), 1)
            self.assertEqual(len(reasons), 1)

    def test_missing_file_is_reported_not_raised(self):
        captures, reasons = load_raw_captures("/nonexistent/path.json")
        self.assertEqual(captures, [])
        self.assertIn("not found", reasons[0])


class TestEmptyResultHandling(unittest.TestCase):
    def test_empty_list_is_valid_and_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "captures.json"
            path.write_text("[]", encoding="utf-8")
            captures, reasons = load_raw_captures(path)
            self.assertEqual(captures, [])
            self.assertEqual(reasons, [])


if __name__ == "__main__":
    unittest.main()
