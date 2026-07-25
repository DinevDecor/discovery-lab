import _pathsetup  # noqa: F401
import tempfile
import unittest
from pathlib import Path

from headquarters.history import RunSnapshot, load_history, previous_scores, save_history, trend_line


def _snapshot(overall=70.0, scores=None) -> RunSnapshot:
    return RunSnapshot(
        timestamp="2026-07-25T00:00:00+00:00",
        overall_health_pct=overall,
        recommendation_backlog=6,
        decision_backlog=0,
        project_health_scores=scores or {"a": 0.5},
        top_recommendation_hq_id="HQ-0001",
    )


class TestHistoryRoundtrip(unittest.TestCase):
    def test_save_and_load_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "history.json"
            save_history(path, [_snapshot()])
            loaded = load_history(path)
            self.assertEqual(len(loaded), 1)
            self.assertEqual(loaded[0].overall_health_pct, 70.0)

    def test_missing_file_returns_empty(self):
        self.assertEqual(load_history(Path("/nonexistent/history.json")), [])

    def test_keeps_only_last_n_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "history.json"
            snapshots = [_snapshot(overall=float(i)) for i in range(5)]
            save_history(path, snapshots, keep_last=2)
            loaded = load_history(path)
            self.assertEqual(len(loaded), 2)
            self.assertEqual(loaded[-1].overall_health_pct, 4.0)


class TestPreviousScores(unittest.TestCase):
    def test_empty_history_returns_empty_dict(self):
        self.assertEqual(previous_scores([]), {})

    def test_returns_last_run_scores(self):
        history = [_snapshot(scores={"a": 0.3}), _snapshot(scores={"a": 0.8})]
        self.assertEqual(previous_scores(history), {"a": 0.8})


class TestTrendLine(unittest.TestCase):
    def test_first_run_is_na(self):
        self.assertIn("N/A", trend_line(70.0, None, "Overall Health"))

    def test_improvement_detected(self):
        self.assertIn("improvement", trend_line(80.0, 60.0, "Overall Health"))

    def test_regression_detected(self):
        self.assertIn("regression", trend_line(50.0, 80.0, "Overall Health"))

    def test_stable_within_one_point(self):
        self.assertIn("stable", trend_line(70.5, 70.0, "Overall Health"))


if __name__ == "__main__":
    unittest.main()
