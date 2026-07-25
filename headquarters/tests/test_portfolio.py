import _pathsetup  # noqa: F401
import unittest

from headquarters.collector import Collected, ObservationAgentSnapshot, RepoSnapshot
from headquarters.models import Confidence, Evidence, Finding
from headquarters.portfolio import build_portfolio, project_health_score, risk_level


def _repo(name, fields=None) -> RepoSnapshot:
    return RepoSnapshot(name=name, path=f"/x/{name}", state_fields=fields or {}, state_file_path="STATE.md", purpose="Does X.", adr_files=[], changelog_lines=None)


def _collected(repos, scanned=None, skipped=None) -> Collected:
    return Collected(
        repos, [], [], [], {},
        ObservationAgentSnapshot("r.md", "l.md", {}, scanned or [], skipped or [], []),
        False, [],
    )


class TestProjectHealthScore(unittest.TestCase):
    def test_full_score_when_healthy(self):
        snap = _repo("a", {"status": "ACTIVE", "x": "y"})
        score = project_health_score("a", snap, [], scanned=["a"], has_log=True)
        self.assertEqual(score, 1.0)

    def test_lower_score_with_mismatch_finding(self):
        snap = _repo("a", {"status": "ACTIVE", "x": "y"})
        finding = Finding("f", "cat", "t", "d", Confidence.MISMATCH, [], ["a"])
        score = project_health_score("a", snap, [finding], scanned=["a"], has_log=True)
        self.assertLess(score, 1.0)


class TestRiskLevel(unittest.TestCase):
    def test_high_when_mismatch_finding_present(self):
        snap = _repo("a", {"status": "ACTIVE", "x": "y"})
        finding = Finding("f", "cat", "t", "d", Confidence.MISMATCH, [], ["a"])
        self.assertEqual(risk_level("a", snap, [finding], skipped=[]), "HIGH")

    def test_low_when_clean(self):
        snap = _repo("a", {"status": "ACTIVE", "x": "y"})
        self.assertEqual(risk_level("a", snap, [], skipped=[]), "LOW")


class TestBuildPortfolio(unittest.TestCase):
    def test_one_entry_per_repo(self):
        repos = {"a": _repo("a", {"status": "ACTIVE", "x": "y"}), "b": _repo("b")}
        entries = build_portfolio(_collected(repos, scanned=["a", "b"]), [])
        self.assertEqual(len(entries), 2)

    def test_first_run_trend_is_na(self):
        repos = {"a": _repo("a", {"status": "ACTIVE", "x": "y"})}
        entries = build_portfolio(_collected(repos, scanned=["a"]), [])
        self.assertIn("N/A", entries[0].trend)

    def test_trend_improving_when_score_rose(self):
        repos = {"a": _repo("a", {"status": "ACTIVE", "x": "y"})}
        entries = build_portfolio(_collected(repos, scanned=["a"]), [], previous_scores={"a": 0.2})
        self.assertIn("Improving", entries[0].trend)

    def test_every_entry_has_required_fields(self):
        repos = {"a": _repo("a", {"status": "ACTIVE", "x": "y"})}
        entries = build_portfolio(_collected(repos, scanned=["a"]), [])
        e = entries[0]
        for attr in ("purpose", "current_state", "trend", "dependencies", "last_meaningful_progress", "risk_level", "confidence", "health_score"):
            self.assertTrue(getattr(e, attr))


if __name__ == "__main__":
    unittest.main()
