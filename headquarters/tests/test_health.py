import _pathsetup  # noqa: F401
import unittest
from datetime import date

from headquarters.collector import Collected, LedgerEntry, ObservationAgentSnapshot, RepoSnapshot
from headquarters.health import compute_health
from headquarters.models import Confidence, Finding


def _empty_collected(repos=None, ledger_entries=None, obs=None) -> Collected:
    return Collected(
        repos=repos or {},
        project_registry_headers=[],
        project_registry_rows=[],
        ledger_entries=ledger_entries or [],
        ledger_metrics={},
        observation=obs or ObservationAgentSnapshot(None, None, {}, [], [], []),
        governance_doc_present=False,
        proposal_dirs=[],
    )


def _repo(name, fields=None, adr=None) -> RepoSnapshot:
    return RepoSnapshot(
        name=name, path=f"/fake/{name}", state_fields=fields or {}, state_file_path="STATE.md",
        purpose=None, adr_files=adr or [], changelog_lines=None,
    )


class TestHealth(unittest.TestCase):
    def test_state_visibility_counts_only_repos_with_two_plus_fields(self):
        repos = {
            "a": _repo("a", {"status": "ACTIVE", "x": "y"}),
            "b": _repo("b", {}),
        }
        metrics = compute_health(_empty_collected(repos=repos), [], 3, now=date(2026, 7, 25))
        self.assertIn("1/2", metrics["state_visibility"].value)

    def test_observation_cleanliness_insufficient_evidence_when_no_report(self):
        metrics = compute_health(_empty_collected(), [], 3, now=date(2026, 7, 25))
        self.assertIn("INSUFFICIENT_EVIDENCE", metrics["observation_cleanliness"].value)

    def test_decision_currency_flags_overdue_proposed_entries(self):
        entries = [
            LedgerEntry({"status": "PROPOSED", "date_proposed": "2026-07-01"}),
            LedgerEntry({"status": "PROPOSED", "date_proposed": "2026-07-24"}),
        ]
        metrics = compute_health(_empty_collected(ledger_entries=entries), [], 3, now=date(2026, 7, 25))
        self.assertIn("1/2", metrics["decision_currency"].value)

    def test_decision_backlog_counts_only_overdue(self):
        entries = [LedgerEntry({"status": "PROPOSED", "date_proposed": "2026-07-01", "recommendation_id": "REC-0001"})]
        metrics = compute_health(_empty_collected(ledger_entries=entries), [], 3, now=date(2026, 7, 25))
        self.assertEqual(metrics["decision_backlog"].value, "1")

    def test_recommendation_backlog_counts_proposed_only(self):
        entries = [
            LedgerEntry({"status": "PROPOSED"}),
            LedgerEntry({"status": "ACCEPTED"}),
        ]
        metrics = compute_health(_empty_collected(ledger_entries=entries), [], 3, now=date(2026, 7, 25))
        self.assertEqual(metrics["recommendation_backlog"].value, "1")

    def test_governance_integrity_reflects_mismatch_findings(self):
        findings = [
            Finding("f1", "cat", "t", "d", Confidence.MISMATCH, [], ["a"]),
            Finding("f2", "cat", "t", "d", Confidence.INSUFFICIENT_EVIDENCE, [], ["a"]),
        ]
        metrics = compute_health(_empty_collected(), findings, 3, now=date(2026, 7, 25))
        self.assertIn("50%", metrics["governance_integrity"].value)

    def test_overall_health_excludes_unavailable_subscores(self):
        metrics = compute_health(_empty_collected(), [], 3, now=date(2026, 7, 25))
        self.assertNotIn("INSUFFICIENT_EVIDENCE", metrics["overall_health"].value)

    def test_every_metric_carries_a_formula(self):
        metrics = compute_health(_empty_collected(), [], 3, now=date(2026, 7, 25))
        for m in metrics.values():
            self.assertTrue(m.formula, f"{m.name} has no formula documented")


if __name__ == "__main__":
    unittest.main()
