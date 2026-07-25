import _pathsetup  # noqa: F401
import tempfile
import unittest
from pathlib import Path

from headquarters.collector import collect_ledger, collect_observation_agent, collect_repo, collect_project_registry
from headquarters.config import ArtifactRef, HeadquartersConfig, RepoConfig


def _config(base: Path, **overrides) -> HeadquartersConfig:
    defaults = dict(
        repos=[],
        project_registry=ArtifactRef("r", "REGISTRY.md"),
        recommendation_ledger=ArtifactRef("r", "LEDGER.md"),
        observation_agent_reports_dir=ArtifactRef("r", "reports"),
        governance_doc=ArtifactRef("r", "GOVERNANCE.md"),
        proposals_dir=ArtifactRef("r", "proposals"),
        decision_backlog_threshold_days=3,
        stale_adr_threshold_days=30,
    )
    defaults.update(overrides)
    defaults["repos"] = [RepoConfig("r", str(base), None, None, None, None)]
    return HeadquartersConfig(**defaults)


class TestCollectRepo(unittest.TestCase):
    def test_reads_state_file_readme_and_adrs(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "STATE.md").write_text("```yaml\nstatus: ACTIVE\nx: y\n```\n")
            (base / "README.md").write_text("# Repo\n\nDoes a thing.\n")
            (base / "adr").mkdir()
            (base / "adr" / "ADR-0001.md").write_text("x")
            repo = RepoConfig("r", str(base), "STATE.md", "adr", "README.md", None)
            snap = collect_repo(repo)
            self.assertEqual(snap.state_fields["status"], "ACTIVE")
            self.assertEqual(snap.purpose, "Does a thing.")
            self.assertEqual(len(snap.adr_files), 1)

    def test_missing_files_produce_empty_not_a_crash(self):
        repo = RepoConfig("r", "/nonexistent/path", "STATE.md", "adr", "README.md", "CHANGELOG.md")
        snap = collect_repo(repo)
        self.assertEqual(snap.state_fields, {})
        self.assertIsNone(snap.purpose)
        self.assertEqual(snap.adr_files, [])
        self.assertIsNone(snap.changelog_lines)


class TestCollectLedger(unittest.TestCase):
    def test_parses_entries_and_metrics_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "LEDGER.md").write_text(
                "```\nrecommendation_id: REC-0001\nstatus: PROPOSED\n```\n"
                "```\ntotal: 1\naccepted: 0\n```\n"
            )
            entries, metrics = collect_ledger(_config(base))
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0].fields["recommendation_id"], "REC-0001")
            self.assertEqual(metrics["total"], "1")

    def test_missing_ledger_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            entries, metrics = collect_ledger(_config(Path(tmp)))
            self.assertEqual(entries, [])
            self.assertEqual(metrics, {})


class TestCollectObservationAgent(unittest.TestCase):
    def test_finds_latest_report_and_parses_confidence_and_decisions(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            reports = base / "reports"
            reports.mkdir()
            (reports / "observation-report-20260101T000000Z.md").write_text(
                "## Confidence\n\nMATCH: 1 · MISMATCH: 2 · INSUFFICIENT_EVIDENCE: 3.\n\n"
                "## Human Decisions Required\n\n- do X\n- do Y\n\n## Next\n"
            )
            (reports / "observation-report-20260102T000000Z.md").write_text(
                "## Confidence\n\nMATCH: 5 · MISMATCH: 0 · INSUFFICIENT_EVIDENCE: 0.\n"
            )
            (reports / "execution-log-20260102T000000Z.md").write_text(
                "- SCAN a: /x\n- SKIP b: not found\n"
            )
            snap = collect_observation_agent(_config(base))
            self.assertEqual(snap.confidence_counts["MATCH"], 5)
            self.assertIn("a", snap.scanned_repos)
            self.assertIn("b", snap.skipped_repos)

    def test_missing_reports_dir_is_empty_not_a_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            snap = collect_observation_agent(_config(Path(tmp)))
            self.assertEqual(snap.confidence_counts, {})
            self.assertEqual(snap.scanned_repos, [])


class TestCollectProjectRegistry(unittest.TestCase):
    def test_parses_table(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "REGISTRY.md").write_text("| Project | Status |\n|---|---|\n| A | ACTIVE |\n")
            headers, rows = collect_project_registry(_config(base))
            self.assertEqual(headers, ["Project", "Status"])
            self.assertEqual(rows, [["A", "ACTIVE"]])


if __name__ == "__main__":
    unittest.main()
