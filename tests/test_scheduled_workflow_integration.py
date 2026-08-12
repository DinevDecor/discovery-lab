"""Proves the scheduled GitHub Actions workflow is wired to the production
orchestrator (run_daily_pipeline.py) rather than invoking Constraint
Archaeology's run_daily.py directly - the integration gap this change
closes.

Parsed as plain text, not with a YAML library: the workflow file's exact
line shape is what CI actually executes, and this repo has no PyYAML
dependency anywhere (constraint-change-observatory/tests/test_safety.py
treats "import yaml" as a forbidden third-party import for its own
sources). This test does not execute the workflow - GitHub Actions only
runs on GitHub - matching CLAUDE.md's "no network, no model calls in
tests".
"""

import os
import re
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_WORKFLOW_PATH = os.path.join(_ROOT, ".github", "workflows", "constraint-archaeology-daily.yml")


def _read_workflow():
    with open(_WORKFLOW_PATH, encoding="utf-8") as f:
        return f.read()


class WorkflowEntrypointTests(unittest.TestCase):
    def setUp(self):
        self.text = _read_workflow()

    def test_workflow_invokes_root_orchestrator(self):
        self.assertIn(
            "run: python3 run_daily_pipeline.py", self.text,
            "workflow must invoke the root run_daily_pipeline.py orchestrator",
        )

    def test_workflow_does_not_invoke_ca_run_daily_directly_as_production_entrypoint(self):
        production_lines = [
            line for line in self.text.splitlines()
            if re.search(r"run:.*\brun_daily\.py\b", line) and "run_daily_pipeline.py" not in line
        ]
        self.assertEqual(
            production_lines, [],
            "constraint-archaeology-agents/run_daily.py must no longer be the "
            "workflow's direct production entrypoint - only run_daily_pipeline.py "
            "(which itself calls it as a gated subprocess) may do so",
        )

    def test_orchestrator_step_receives_required_secrets(self):
        # The orchestrator step is the "Run daily pipeline..." step; its env
        # block sits between its own header and the next "- name:" step.
        match = re.search(
            r"- name: Run daily pipeline.*?\n(?P<body>.*?)(?=\n\s*- name:|\Z)",
            self.text, re.DOTALL,
        )
        self.assertIsNotNone(match, "expected a 'Run daily pipeline' step")
        body = match.group("body")
        self.assertIn("ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}", body)
        self.assertIn("PRODUCT_HUNT_TOKEN: ${{ secrets.PRODUCT_HUNT_TOKEN }}", body)
        self.assertIn("run_daily_pipeline.py", body)


class CommitStepCoverageTests(unittest.TestCase):
    def setUp(self):
        self.text = _read_workflow()
        match = re.search(r"git add(?P<paths>(?:[^\n]*\\\n)*[^\n]*)\n", self.text)
        self.assertIsNotNone(match, "expected a 'git add' line in the commit step")
        self.add_paths = match.group("paths").replace("\\", "").split()

    def test_commit_step_includes_ca_outputs(self):
        self.assertIn("constraint-archaeology-agents/data", self.add_paths)
        self.assertIn("constraint-archaeology-agents/reports", self.add_paths)

    def test_commit_step_includes_bca_outputs(self):
        self.assertIn("business-candidate-analyst/data", self.add_paths)
        self.assertIn("business-candidate-analyst/reports", self.add_paths)

    def test_commit_step_includes_pipeline_status_report(self):
        self.assertIn(
            "reports", self.add_paths,
            "the root reports/ dir (pipeline-status-<date>.json) must be committed",
        )


class UnchangedSchedulingBehaviorTests(unittest.TestCase):
    def setUp(self):
        self.text = _read_workflow()

    def test_concurrency_group_unchanged(self):
        self.assertIn("group: constraint-archaeology-daily-${{ github.ref }}", self.text)

    def test_cancel_in_progress_still_false(self):
        self.assertIn("cancel-in-progress: false", self.text)

    def test_cron_schedule_unchanged(self):
        self.assertIn("cron: '0 22 * * *'", self.text)

    def test_contents_write_permission_unchanged(self):
        self.assertIn("contents: write", self.text)


if __name__ == "__main__":
    unittest.main()
