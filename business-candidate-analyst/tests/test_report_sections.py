"""Confirms the report keeps Mode A and Mode B in separate, correctly
labeled top-level sections and never merges them - the task's explicit
"do not merge the two conceptually" rule, checked at the output layer."""

import _pathsetup  # noqa: F401
import os
import shutil
import tempfile
import unittest

from business_candidate_analyst.analyst import run_analysis as run_mode_a
from business_candidate_analyst.config import load_rearchitecture_thresholds
from business_candidate_analyst.rearchitecture.analyst import run_analysis as run_mode_b
from business_candidate_analyst.report import render

_FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


class ReportSectionTests(unittest.TestCase):
    def setUp(self):
        self.data_dir = tempfile.mkdtemp()
        self.report_path = os.path.join(self.data_dir, "report.md")

    def tearDown(self):
        shutil.rmtree(self.data_dir, ignore_errors=True)

    def test_both_sections_present_and_ordered(self):
        a = run_mode_a(os.path.join(_FIXTURES, "ca_rearch_run1"), self.data_dir, now="2026-08-08T00:00:00Z")
        cfg = load_rearchitecture_thresholds()
        b = run_mode_b(os.path.join(_FIXTURES, "ca_rearch_run1"), self.data_dir, cfg, now="2026-08-08T00:00:00Z")
        render(self.report_path, a, b)
        with open(self.report_path, encoding="utf-8") as f:
            text = f.read()
        self.assertIn("## New Market Candidates", text)
        self.assertIn("## Legacy Business Rearchitecture Candidates", text)
        self.assertLess(text.index("## New Market Candidates"), text.index("## Legacy Business Rearchitecture"))
        # The bank-branch candidate's required fields must all appear.
        self.assertIn("Historical constraint", text)
        self.assertIn("Evidence gaps", text)
        self.assertIn("Provenance", text)

    def test_report_renders_without_mode_b_result(self):
        a = run_mode_a(os.path.join(_FIXTURES, "ca_rearch_run1"), self.data_dir, now="2026-08-08T00:00:00Z")
        render(self.report_path, a, None)
        with open(self.report_path, encoding="utf-8") as f:
            text = f.read()
        self.assertIn("Mode B was not run for this report", text)


if __name__ == "__main__":
    unittest.main()
