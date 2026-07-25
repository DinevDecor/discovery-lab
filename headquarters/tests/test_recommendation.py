import _pathsetup  # noqa: F401
import tempfile
import unittest
from datetime import date
from pathlib import Path

from headquarters.models import Confidence
from headquarters.prioritizer import Candidate
from headquarters.recommendation import (
    assign_id,
    evaluate,
    load_decisions,
    load_log,
    save_log,
)


def _candidate(key="c1") -> Candidate:
    return Candidate(key, "title", "desc", Confidence.MISMATCH, ["a"], False, "cat", "drift")


class TestAssignId(unittest.TestCase):
    def test_first_candidate_gets_hq_0001(self):
        hq_id, records = assign_id(_candidate(), [], date(2026, 7, 25))
        self.assertEqual(hq_id, "HQ-0001")
        self.assertEqual(len(records), 1)

    def test_second_distinct_candidate_gets_hq_0002(self):
        _, records = assign_id(_candidate("c1"), [], date(2026, 7, 25))
        hq_id, records = assign_id(_candidate("c2"), records, date(2026, 7, 25))
        self.assertEqual(hq_id, "HQ-0002")

    def test_recurring_candidate_reuses_its_id(self):
        _, records = assign_id(_candidate("c1"), [], date(2026, 7, 25))
        hq_id, records = assign_id(_candidate("c1"), records, date(2026, 7, 26))
        self.assertEqual(hq_id, "HQ-0001")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].times_proposed, 2)
        self.assertEqual(records[0].last_proposed, "2026-07-26")


class TestLogRoundtrip(unittest.TestCase):
    def test_save_and_load_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "log.json"
            _, records = assign_id(_candidate(), [], date(2026, 7, 25))
            save_log(path, records)
            loaded = load_log(path)
            self.assertEqual(loaded[0].hq_id, "HQ-0001")

    def test_missing_file_returns_empty_list(self):
        self.assertEqual(load_log(Path("/nonexistent/log.json")), [])


class TestEvaluate(unittest.TestCase):
    def test_no_decisions_is_insufficient_evidence(self):
        result = evaluate([], {})
        self.assertIn("INSUFFICIENT_EVIDENCE", result["status"])

    def test_counts_recorded_decisions(self):
        decisions = {
            "HQ-0001": {"accepted": True, "implemented": True, "useful": True},
            "HQ-0002": {"accepted": False, "rejected": True},
        }
        result = evaluate([], decisions)
        self.assertEqual(result["decisions_recorded"], 2)
        self.assertEqual(result["accepted"], 1)
        self.assertEqual(result["implemented"], 1)

    def test_load_decisions_missing_file_returns_empty(self):
        self.assertEqual(load_decisions(Path("/nonexistent/decisions.json")), {})


if __name__ == "__main__":
    unittest.main()
