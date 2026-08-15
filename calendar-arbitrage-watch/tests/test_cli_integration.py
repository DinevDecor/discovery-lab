"""End-to-end wiring test: intake -> ledger -> gate -> lifecycle ->
snapshot -> report, using only the synthetic fixtures (see
tests/fixtures/README.md - never the real, unlocated research baseline).
"""

import _pathsetup  # noqa: F401
import json
import os
import shutil
import tempfile
import unittest

from calendar_arbitrage_watch import cli, ledger

_FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


class CliIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.tmpdir, "data"))
        os.makedirs(os.path.join(self.tmpdir, "reports"))

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_add_dated_fixture_end_to_end(self):
        path = os.path.join(_FIXTURES, "synthetic_submission_dated.json")
        rc = cli.cmd_add(self.tmpdir, [path])
        self.assertEqual(rc, 0)

        events_path = os.path.join(self.tmpdir, "data", "calendar_events.jsonl")
        self.assertTrue(os.path.exists(events_path))
        with open(events_path) as f:
            lines = f.readlines()
        # one line for the specialist assessment, one for the post-review state
        self.assertEqual(len(lines), 2)

        snapshot_path = os.path.join(self.tmpdir, "data", "calendar_candidates.json")
        with open(snapshot_path) as f:
            snapshot = json.load(f)
        self.assertEqual(len(snapshot["current"]), 1)
        self.assertEqual(snapshot["current"][0]["candidate_id"], "synthetic-regclock-0001")

        report_files = os.listdir(os.path.join(self.tmpdir, "reports"))
        self.assertEqual(len(report_files), 1)

    def test_rerun_over_unchanged_evidence_is_idempotent(self):
        path = os.path.join(_FIXTURES, "synthetic_submission_dated.json")
        cli.cmd_add(self.tmpdir, [path])
        events_path = os.path.join(self.tmpdir, "data", "calendar_events.jsonl")
        with open(events_path) as f:
            count_after_first = len(f.readlines())

        cli.cmd_add(self.tmpdir, [path])
        with open(events_path) as f:
            count_after_second = len(f.readlines())

        self.assertEqual(count_after_first, count_after_second)

    def test_add_rolling_archaeology_fixture(self):
        path = os.path.join(_FIXTURES, "synthetic_submission_rolling.json")
        rc = cli.cmd_add(self.tmpdir, [path])
        self.assertEqual(rc, 0)
        led = ledger.CalendarLedger(os.path.join(self.tmpdir, "data", "calendar_events.jsonl"))
        snapshot = ledger.rebuild_snapshot(led.all_entries())
        record = snapshot["current"][0]
        self.assertEqual(record["mode"], "ARCHAEOLOGY")
        self.assertEqual(record["shock_forecast"]["shock_type"], "ROLLING")

    def test_second_run_with_no_new_submissions_reports_no_material_change(self):
        path = os.path.join(_FIXTURES, "synthetic_submission_dated.json")
        cli.cmd_add(self.tmpdir, [path])
        rc = cli.cmd_report(self.tmpdir)
        self.assertEqual(rc, 0)
        report_files = sorted(os.listdir(os.path.join(self.tmpdir, "reports")))
        with open(os.path.join(self.tmpdir, "reports", report_files[-1])) as f:
            text = f.read()
        self.assertIn("NO MATERIAL CALENDAR CHANGE", text)

    def test_rejected_submission_returns_nonzero_and_writes_nothing(self):
        bad_path = os.path.join(self.tmpdir, "bad.json")
        with open(bad_path, "w", encoding="utf-8") as f:
            json.dump({"candidate_id": "bad-1"}, f)  # missing required fields
        rc = cli.cmd_add(self.tmpdir, [bad_path])
        self.assertEqual(rc, 1)
        events_path = os.path.join(self.tmpdir, "data", "calendar_events.jsonl")
        self.assertFalse(os.path.exists(events_path))


if __name__ == "__main__":
    unittest.main()
