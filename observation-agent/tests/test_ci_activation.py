"""EXEC-003 — tests for the scheduled-invocation configuration and
workflow glue added to activate the Observation Agent. Covers what is
practical to test without actually running GitHub Actions: that the
CI-only config loads and points discovery-lab at its own checkout
while leaving the other 4 repositories as documented, safely-skipped
placeholders; that ci_summary.py classifies a run's outcome correctly;
and that the workflow file itself declares read-only permissions and
never contains a write/commit/push/PR action, using the same detector
test_safety.py already uses for the agent's own source.
"""

import _pathsetup  # noqa: F401
import re
import tempfile
import unittest
from pathlib import Path

import test_safety
from observation_agent.config import load_config

_OBSERVATION_AGENT_ROOT = Path(__file__).resolve().parents[1]
_CI_CONFIG_PATH = _OBSERVATION_AGENT_ROOT / "config.ci.json"
_LOCAL_CONFIG_PATH = _OBSERVATION_AGENT_ROOT / "config.json"
_WORKFLOW_PATH = (
    _OBSERVATION_AGENT_ROOT.parent / ".github" / "workflows" / "observation-agent.yml"
)


class TestCiConfig(unittest.TestCase):
    def test_ci_config_loads(self):
        config = load_config(_CI_CONFIG_PATH)
        self.assertEqual(len(config.repos), 5)

    def test_discovery_lab_points_at_its_own_checkout(self):
        # The workflow's run step uses `working-directory: observation-agent`,
        # so ".." (the parent of observation-agent/, i.e. the repo root as
        # checked out by actions/checkout) is the correct path, not ".".
        config = load_config(_CI_CONFIG_PATH)
        by_name = {r.name: r for r in config.repos}
        self.assertIn("discovery-lab", by_name)
        self.assertEqual(by_name["discovery-lab"].path, "..")

    def test_other_four_repos_are_placeholder_paths_not_present_on_disk(self):
        # These must not accidentally resolve to a real path on whatever
        # machine runs the test suite (dev container or CI runner) — if
        # they did, the "expected to SKIP" documentation would be wrong.
        config = load_config(_CI_CONFIG_PATH)
        for repo in config.repos:
            if repo.name == "discovery-lab":
                continue
            self.assertFalse(
                Path(repo.path).exists(),
                f"{repo.name}'s CI placeholder path {repo.path!r} unexpectedly "
                "exists — config.ci.json's SKIP-by-design assumption is broken",
            )


class TestCiSummary(unittest.TestCase):
    def _import_ci_summary(self):
        import importlib
        import sys

        sys.path.insert(0, str(_OBSERVATION_AGENT_ROOT))
        try:
            if "ci_summary" in sys.modules:
                importlib.reload(sys.modules["ci_summary"])
            import ci_summary

            return ci_summary
        finally:
            sys.path.remove(str(_OBSERVATION_AGENT_ROOT))

    def test_no_report_is_failure(self):
        ci_summary = self._import_ci_summary()
        with tempfile.TemporaryDirectory() as tmp:
            text = ci_summary.build_summary(tmp)
            self.assertIn("STATUS: FAILURE", text)

    def test_clean_run_is_success(self):
        ci_summary = self._import_ci_summary()
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "observation-report-1.md").write_text(
                "# Report\n\n## Confidence\n\nMATCH: 0 · MISMATCH: 0 · "
                "INSUFFICIENT_EVIDENCE: 0.\n"
            )
            (Path(tmp) / "execution-log-1.md").write_text(
                "SCAN discovery-lab: .\n  orphan_files: 0 observation(s) in 0.01s\n"
            )
            text = ci_summary.build_summary(tmp)
            self.assertIn("STATUS: SUCCESS", text)
            self.assertIn("MISMATCH: 0", text)

    def test_skipped_repo_is_partial(self):
        ci_summary = self._import_ci_summary()
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "observation-report-1.md").write_text(
                "# Report\n\n## Confidence\n\nMATCH: 0 · MISMATCH: 0 · "
                "INSUFFICIENT_EVIDENCE: 0.\n"
            )
            (Path(tmp) / "execution-log-1.md").write_text(
                "SKIP kod: path /not-checked-out-in-ci/kod does not exist "
                "or is not accessible\n"
            )
            text = ci_summary.build_summary(tmp)
            self.assertIn("STATUS: PARTIAL", text)

    def test_check_error_is_partial(self):
        ci_summary = self._import_ci_summary()
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "observation-report-1.md").write_text(
                "# Report\n\n## Confidence\n\nMATCH: 0 · MISMATCH: 0 · "
                "INSUFFICIENT_EVIDENCE: 0.\n"
            )
            (Path(tmp) / "execution-log-1.md").write_text(
                "  ERROR in orphan_files for discovery-lab: OSError()\n"
            )
            text = ci_summary.build_summary(tmp)
            self.assertIn("STATUS: PARTIAL", text)


class TestCiSummarySafety(unittest.TestCase):
    # ci_summary.py lives outside src/, so test_safety.py's own scan
    # does not cover it. Reuse the same detector here rather than
    # trusting a second, separate read of the same file.
    def test_no_forbidden_call_in_ci_summary(self):
        text = (_OBSERVATION_AGENT_ROOT / "ci_summary.py").read_text(encoding="utf-8")
        for pattern in test_safety._FORBIDDEN_ANYWHERE:
            self.assertIsNone(
                re.search(pattern, text),
                f"Forbidden pattern {pattern!r} found in ci_summary.py",
            )

    def test_ci_summary_only_writes_the_step_summary_target(self):
        text = (_OBSERVATION_AGENT_ROOT / "ci_summary.py").read_text(encoding="utf-8")
        matches = test_safety._WRITE_MODE_PATTERN.findall(text)
        self.assertEqual(len(matches), 1)


class TestWorkflowFile(unittest.TestCase):
    def setUp(self):
        self.text = _WORKFLOW_PATH.read_text(encoding="utf-8")

    def test_workflow_file_exists(self):
        self.assertTrue(_WORKFLOW_PATH.is_file())

    def test_declares_read_only_contents_permission(self):
        self.assertIn("contents: read", self.text)
        self.assertNotIn("contents: write", self.text)

    def test_has_daily_schedule_and_manual_trigger(self):
        self.assertIn("schedule:", self.text)
        self.assertIn("cron:", self.text)
        self.assertIn("workflow_dispatch:", self.text)

    def test_uploads_an_artifact(self):
        self.assertIn("actions/upload-artifact", self.text)

    def test_never_writes_or_pushes_or_opens_a_pull_request(self):
        forbidden_substrings = [
            "git push",
            "git commit",
            "git merge",
            "create-pull-request",
            "actions/create-release",
            "git-auto-commit",
        ]
        lowered = self.text.lower()
        for needle in forbidden_substrings:
            self.assertNotIn(needle.lower(), lowered)

    def test_checkout_does_not_persist_credentials(self):
        self.assertIn("persist-credentials: false", self.text)


class TestExcludedPathsEquivalence(unittest.TestCase):
    """EXEC-006 — local and CI configs must agree on which tool
    output directories to exclude, so a local run and a scheduled CI
    run of the same check produce equivalent logical findings (never
    flagging either tool's own report output as repository content),
    even though only the local config actually encounters the
    scenario in practice (CI never commits its own output, so has no
    memory between runs to rediscover)."""

    def test_both_configs_exclude_observation_agents_own_reports_dir(self):
        local = load_config(_LOCAL_CONFIG_PATH)
        ci = load_config(_CI_CONFIG_PATH)
        self.assertIn("observation-agent/reports", local.excluded_paths)
        self.assertIn("observation-agent/reports", ci.excluded_paths)

    def test_both_configs_exclude_headquarters_reports_dir(self):
        local = load_config(_LOCAL_CONFIG_PATH)
        ci = load_config(_CI_CONFIG_PATH)
        self.assertIn("headquarters/reports", local.excluded_paths)
        self.assertIn("headquarters/reports", ci.excluded_paths)


if __name__ == "__main__":
    unittest.main()
