import _pathsetup  # noqa: F401
import tempfile
import time
import unittest
from datetime import date
from pathlib import Path

from headquarters.collector import Collected, LedgerEntry, ObservationAgentSnapshot, RepoSnapshot
from headquarters.config import ArtifactRef, HeadquartersConfig, RepoConfig
from headquarters.drift import (
    decision_backlog_findings,
    duplicate_adr_ids,
    proposals_without_state_reference,
    registry_gaps,
    stale_adrs,
    unparseable_state_files,
)
from headquarters.models import Confidence


def _repo(name, fields=None, adr=None, path=None) -> RepoSnapshot:
    return RepoSnapshot(
        name=name, path=path or f"/fake/{name}", state_fields=fields or {}, state_file_path="STATE.md",
        purpose=None, adr_files=adr or [], changelog_lines=None,
    )


def _make_config(repos=None, proposals_repo="discovery-lab") -> HeadquartersConfig:
    return HeadquartersConfig(
        repos=repos or [RepoConfig("discovery-lab", "/x", "STATE.md", None, None, None)],
        project_registry=ArtifactRef("discovery-lab", "x"),
        recommendation_ledger=ArtifactRef("discovery-lab", "x"),
        observation_agent_reports_dir=ArtifactRef("discovery-lab", "x"),
        governance_doc=ArtifactRef("discovery-lab", "x"),
        proposals_dir=ArtifactRef(proposals_repo, "docs/proposals"),
        decision_backlog_threshold_days=3,
        stale_adr_threshold_days=30,
    )


def _collected(repos=None, ledger_entries=None, registry_rows=None, proposal_dirs=None) -> Collected:
    return Collected(
        repos=repos or {},
        project_registry_headers=["Project"] if registry_rows else [],
        project_registry_rows=registry_rows or [],
        ledger_entries=ledger_entries or [],
        ledger_metrics={},
        observation=ObservationAgentSnapshot(None, None, {}, [], [], []),
        governance_doc_present=True,
        proposal_dirs=proposal_dirs or [],
    )


class TestDuplicateAdrIds(unittest.TestCase):
    def test_flags_two_files_claiming_the_same_id(self):
        repos = {
            "discovery-lab": _repo(
                "discovery-lab",
                adr=[("ADR-0001-a.md", 0.0), ("ADR-0001-b.md", 0.0), ("ADR-0002.md", 0.0)],
            )
        }
        findings = duplicate_adr_ids(_collected(repos=repos))
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].confidence, Confidence.MISMATCH)
        self.assertEqual(len(findings[0].evidence), 2)

    def test_no_finding_when_ids_unique(self):
        repos = {"r": _repo("r", adr=[("ADR-0001.md", 0.0), ("ADR-0002.md", 0.0)])}
        self.assertEqual(duplicate_adr_ids(_collected(repos=repos)), [])


class TestStaleAdrs(unittest.TestCase):
    def test_flags_old_mtime_as_insufficient_evidence(self):
        old_mtime = time.mktime((2020, 1, 1, 0, 0, 0, 0, 0, 0))
        repos = {"r": _repo("r", adr=[("ADR-0001.md", old_mtime)])}
        findings = stale_adrs(_collected(repos=repos), threshold_days=30, now=date(2026, 7, 25))
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].confidence, Confidence.INSUFFICIENT_EVIDENCE)

    def test_no_finding_within_threshold(self):
        recent_mtime = time.mktime((2026, 7, 24, 0, 0, 0, 0, 0, 0))
        repos = {"r": _repo("r", adr=[("ADR-0001.md", recent_mtime)])}
        findings = stale_adrs(_collected(repos=repos), threshold_days=30, now=date(2026, 7, 25))
        self.assertEqual(findings, [])


class TestRegistryGaps(unittest.TestCase):
    def _config(self):
        return HeadquartersConfig(
            repos=[
                RepoConfig("discovery-lab", "/x", None, None, None, None),
                RepoConfig("project-memory", "/y", None, None, None, None),
            ],
            project_registry=ArtifactRef("project-memory", "PROJECT_REGISTRY.md"),
            recommendation_ledger=ArtifactRef("discovery-lab", "x"),
            observation_agent_reports_dir=ArtifactRef("discovery-lab", "x"),
            governance_doc=ArtifactRef("discovery-lab", "x"),
            proposals_dir=ArtifactRef("discovery-lab", "x"),
            decision_backlog_threshold_days=3,
            stale_adr_threshold_days=30,
        )

    def test_flags_repo_missing_from_registry(self):
        rows = [["Project Memory", "loc", "ACTIVE"]]
        findings = registry_gaps(_collected(registry_rows=rows), self._config())
        titles = [f.title for f in findings]
        self.assertTrue(any("discovery-lab" in t for t in titles))
        self.assertFalse(any(t.startswith("project-memory ") for t in titles))

    def test_insufficient_evidence_when_registry_unreadable(self):
        findings = registry_gaps(_collected(registry_rows=[]), self._config())
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].confidence, Confidence.INSUFFICIENT_EVIDENCE)


class TestDecisionBacklogFindings(unittest.TestCase):
    def test_flags_overdue_proposed_entry_with_evidence(self):
        entries = [LedgerEntry({
            "status": "PROPOSED", "date_proposed": "2026-07-01",
            "recommendation_id": "REC-0001", "destination_repository": "kod",
            "summary": "fix it",
        })]
        findings = decision_backlog_findings(_collected(ledger_entries=entries), 3, date(2026, 7, 25))
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].confidence, Confidence.MISMATCH)
        self.assertEqual(findings[0].affected, ["kod"])

    def test_no_finding_when_recent(self):
        entries = [LedgerEntry({"status": "PROPOSED", "date_proposed": "2026-07-24"})]
        self.assertEqual(decision_backlog_findings(_collected(ledger_entries=entries), 3, date(2026, 7, 25)), [])


class TestProposalsWithoutStateReference(unittest.TestCase):
    def test_flags_unmentioned_proposal_dir(self):
        repos = {"discovery-lab": _repo("discovery-lab", fields={"current_step": "EXEC-002 done, see docs/proposals/EXEC-002-observation-agent"})}
        c = _collected(repos=repos, proposal_dirs=["EXEC-002-observation-agent", "ARCH-999-unmentioned"])
        findings = proposals_without_state_reference(c, _make_config())
        titles = [f.title for f in findings]
        self.assertTrue(any("ARCH-999-unmentioned" in t for t in titles))
        self.assertFalse(any("EXEC-002-observation-agent" in t for t in titles))
        for f in findings:
            self.assertEqual(f.confidence, Confidence.INSUFFICIENT_EVIDENCE)

    def test_uses_the_configured_proposals_repo_not_a_hardcoded_name(self):
        # Extensibility check: a different repo owning proposals_dir
        # must be respected, not silently ignored in favor of
        # "discovery-lab" being hardcoded somewhere.
        repos = {"some-other-repo": _repo("some-other-repo", fields={"status": "ACTIVE"})}
        c = _collected(repos=repos, proposal_dirs=["UNMENTIONED-INITIATIVE"])
        findings = proposals_without_state_reference(c, _make_config(proposals_repo="some-other-repo"))
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].affected, ["some-other-repo"])


class TestUnparseableStateFiles(unittest.TestCase):
    def test_flags_state_file_with_fewer_than_two_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "STATE.md").write_text("just some prose, no recognizable fields at all\n")
            config = _make_config(repos=[RepoConfig("r", str(base), "STATE.md", None, None, None)])
            repos = {"r": _repo("r", fields={}, path=str(base))}
            findings = unparseable_state_files(_collected(repos=repos), config)
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0].category, "data_quality")
            self.assertEqual(findings[0].confidence, Confidence.INSUFFICIENT_EVIDENCE)

    def test_no_finding_when_state_file_parses_fine(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "STATE.md").write_text("```yaml\nstatus: ACTIVE\nx: y\n```\n")
            config = _make_config(repos=[RepoConfig("r", str(base), "STATE.md", None, None, None)])
            repos = {"r": _repo("r", fields={"status": "ACTIVE", "x": "y"}, path=str(base))}
            self.assertEqual(unparseable_state_files(_collected(repos=repos), config), [])

    def test_no_finding_when_state_file_does_not_exist_on_disk(self):
        config = _make_config(repos=[RepoConfig("r", "/nonexistent", "STATE.md", None, None, None)])
        repos = {"r": _repo("r", fields={}, path="/nonexistent")}
        self.assertEqual(unparseable_state_files(_collected(repos=repos), config), [])


if __name__ == "__main__":
    unittest.main()
