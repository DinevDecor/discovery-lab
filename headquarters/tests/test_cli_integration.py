"""End-to-end integration test against a small fabricated ecosystem
(tempdir fixtures, not the real repositories) — proves the whole
pipeline (collect -> drift -> opportunities -> health -> portfolio ->
prioritize -> recommend -> brief -> persist) runs together without
touching anything outside its own reports directory."""

import _pathsetup  # noqa: F401
import json
import tempfile
import unittest
from pathlib import Path

from headquarters.cli import run


def _build_fixture_ecosystem(root: Path) -> Path:
    repo_a = root / "repo-a"
    repo_a.mkdir()
    (repo_a / "STATE.md").write_text("```yaml\nstatus: ACTIVE\nupdated_at: 2026-07-20\n```\n")
    (repo_a / "README.md").write_text("# Repo A\n\nDoes a thing.\n")
    (repo_a / "adr").mkdir()
    (repo_a / "adr" / "ADR-0001-a.md").write_text("x")
    (repo_a / "adr" / "ADR-0001-b.md").write_text("y")  # deliberate duplicate ID
    (repo_a / "docs").mkdir()
    (repo_a / "docs" / "investigations").mkdir()
    (repo_a / "docs" / "investigations" / "RECOMMENDATION-LEDGER.md").write_text(
        "## Entries\n\n```\nrecommendation_id: REC-0001\n"
        "destination_repository: repo-a\ndate_proposed: 2026-01-01\n"
        "status: PROPOSED\nsummary: fix something\n```\n"
    )
    (repo_a / "observation-agent").mkdir()
    (repo_a / "observation-agent" / "reports").mkdir()
    (repo_a / "observation-agent" / "reports" / "observation-report-1.md").write_text(
        "## Confidence\n\nMATCH: 0 · MISMATCH: 1 · INSUFFICIENT_EVIDENCE: 0.\n"
    )
    (repo_a / "observation-agent" / "reports" / "execution-log-1.md").write_text("- SCAN repo-a: /x\n")
    (repo_a / "docs" / "ai-organization").mkdir()
    (repo_a / "docs" / "ai-organization" / "GOVERNANCE.md").write_text("x")
    (repo_a / "docs" / "proposals").mkdir()
    (repo_a / "PROJECT_REGISTRY.md").write_text("| Project | Status |\n|---|---|\n| Repo A | ACTIVE |\n")

    config = {
        "repos": [
            {"name": "repo-a", "path": str(repo_a), "state_file": "STATE.md", "adr_dir": "adr", "readme": "README.md", "changelog": None}
        ],
        "project_registry": {"repo": "repo-a", "path": "PROJECT_REGISTRY.md"},
        "recommendation_ledger": {"repo": "repo-a", "path": "docs/investigations/RECOMMENDATION-LEDGER.md"},
        "observation_agent_reports_dir": {"repo": "repo-a", "path": "observation-agent/reports"},
        "governance_doc": {"repo": "repo-a", "path": "docs/ai-organization/GOVERNANCE.md"},
        "proposals_dir": {"repo": "repo-a", "path": "docs/proposals"},
        "decision_backlog_threshold_days": 3,
        "stale_adr_threshold_days": 30,
    }
    config_path = root / "config.json"
    config_path.write_text(json.dumps(config))
    return config_path


class TestCliIntegration(unittest.TestCase):
    def test_full_run_produces_a_brief_and_a_recommendation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_path = _build_fixture_ecosystem(root)
            reports_dir = root / "hq-reports"
            reports_dir.mkdir()

            result = run(config_path, reports_dir)

            self.assertIn("## Most Important Recommendation", result["brief_text"])
            self.assertIsNotNone(result["top_recommendation"])
            self.assertEqual(result["top_recommendation"].hq_id, "HQ-0001")

    def test_recurring_run_reuses_the_same_hq_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_path = _build_fixture_ecosystem(root)
            reports_dir = root / "hq-reports"
            reports_dir.mkdir()

            from headquarters.recommendation import save_log
            from headquarters.history import save_history

            first = run(config_path, reports_dir)
            save_log(first["log_path"], first["records"])
            save_history(first["history_path"], first["history"])

            second = run(config_path, reports_dir)
            self.assertEqual(first["top_recommendation"].hq_id, second["top_recommendation"].hq_id)

    def test_run_does_not_write_inside_the_fixture_repository(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_path = _build_fixture_ecosystem(root)
            repo_a = root / "repo-a"
            before = sorted(p.relative_to(repo_a) for p in repo_a.rglob("*"))

            reports_dir = root / "hq-reports"
            reports_dir.mkdir()
            run(config_path, reports_dir)

            after = sorted(p.relative_to(repo_a) for p in repo_a.rglob("*"))
            self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
