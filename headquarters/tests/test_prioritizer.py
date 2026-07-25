import _pathsetup  # noqa: F401
import unittest

from headquarters.collector import Collected, LedgerEntry, ObservationAgentSnapshot
from headquarters.models import Confidence, Finding
from headquarters.prioritizer import Candidate, build_candidates, score, select_top, to_recommendation


def _collected(ledger_entries=None) -> Collected:
    return Collected({}, [], [], ledger_entries or [], {}, ObservationAgentSnapshot(None, None, {}, [], [], []), False, [])


class TestBuildCandidates(unittest.TestCase):
    def test_only_proposed_ledger_entries_become_candidates(self):
        entries = [
            LedgerEntry({"status": "PROPOSED", "recommendation_id": "REC-0001", "destination_repository": "kod"}),
            LedgerEntry({"status": "ACCEPTED", "recommendation_id": "REC-0002", "destination_repository": "kod"}),
        ]
        candidates = build_candidates(_collected(entries), [], [])
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].source, "ledger")


class TestScore(unittest.TestCase):
    def test_mismatch_scores_higher_than_insufficient_evidence(self):
        mismatch = Finding("f1", "cat", "t", "d", Confidence.MISMATCH, [], ["a"])
        insufficient = Finding("f2", "cat", "t", "d", Confidence.INSUFFICIENT_EVIDENCE, [], ["a"])
        candidates = build_candidates(_collected(), [mismatch, insufficient], [])
        scores = {c.key: score(c)[0] for c in candidates}
        self.assertGreater(scores["finding-f1"], scores["finding-f2"])

    def test_opportunity_scores_lower_than_equivalent_drift_finding(self):
        drift = Candidate("d", "t", "d", Confidence.INSUFFICIENT_EVIDENCE, ["a"], False, "cat", "drift")
        opportunity = Candidate("o", "t", "d", Confidence.INSUFFICIENT_EVIDENCE, ["a"], True, "cat", "opportunity")
        self.assertGreater(score(drift)[0], score(opportunity)[0])

    def test_finishable_category_gets_a_bonus(self):
        finishable = Candidate("f", "t", "d", Confidence.MISMATCH, ["a"], False, "decision_backlog", "drift")
        other = Candidate("o", "t", "d", Confidence.MISMATCH, ["a"], False, "governance_inconsistency", "drift")
        self.assertGreater(score(finishable)[0], score(other)[0])


class TestSelectTop(unittest.TestCase):
    def test_returns_exactly_one_candidate(self):
        findings = [
            Finding("f1", "cat", "t1", "d", Confidence.MISMATCH, [], ["a"]),
            Finding("f2", "cat", "t2", "d", Confidence.INSUFFICIENT_EVIDENCE, [], ["a"]),
        ]
        candidates = build_candidates(_collected(), findings, [])
        result = select_top(candidates)
        self.assertIsNotNone(result)
        top_candidate, top_score, breakdown = result
        self.assertEqual(top_candidate.key, "finding-f1")

    def test_none_when_no_candidates(self):
        self.assertIsNone(select_top([]))

    def test_deterministic_tiebreak(self):
        findings = [
            Finding("z", "cat", "t", "d", Confidence.MISMATCH, [], ["a"]),
            Finding("a", "cat", "t", "d", Confidence.MISMATCH, [], ["a"]),
        ]
        candidates = build_candidates(_collected(), findings, [])
        result1 = select_top(candidates)
        result2 = select_top(list(reversed(candidates)))
        self.assertEqual(result1[0].key, result2[0].key)


class TestToRecommendation(unittest.TestCase):
    def test_all_explainability_fields_populated(self):
        finding = Finding("f1", "cat", "t", "d", Confidence.MISMATCH, [], ["a"])
        candidates = build_candidates(_collected(), [finding], [])
        top_candidate, top_score, breakdown = select_top(candidates)
        rec = to_recommendation(top_candidate, "HQ-0001", top_score, breakdown)
        for attr in ("title", "reason", "reasoning", "expected_impact", "dependencies", "estimated_confidence", "estimated_risk"):
            self.assertTrue(getattr(rec, attr), f"{attr} is empty")


if __name__ == "__main__":
    unittest.main()
