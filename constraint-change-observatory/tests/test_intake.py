import _pathsetup  # noqa: F401
import json
import os
import shutil
import tempfile
import unittest

from _factories import make_record
from constraint_change_observatory.intake import ADDED, DUPLICATE, REJECTED, intake_file, validate_file
from constraint_change_observatory.ledger import ConstraintLedger, rebuild_snapshot


class IntakeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.events_path = os.path.join(self.tmp, "constraint_events.jsonl")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write_file(self, name, payload):
        path = os.path.join(self.tmp, name)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f)
        return path

    def test_valid_record_is_added(self):
        path = self._write_file("one.json", make_record().to_dict())
        ledger = ConstraintLedger(self.events_path)
        results = intake_file(path, ledger, "2026-08-10T00:00:00Z")
        self.assertEqual(results[0].outcome, ADDED)
        self.assertEqual(len(ledger.all_entries()), 1)

    def test_invalid_record_is_rejected_loudly_and_not_appended(self):
        bad = make_record(current_constraint_state="WEAKENED", current_evidence=[]).to_dict()
        path = self._write_file("bad.json", bad)
        ledger = ConstraintLedger(self.events_path)
        results = intake_file(path, ledger, "2026-08-10T00:00:00Z")
        self.assertEqual(results[0].outcome, REJECTED)
        self.assertTrue(results[0].violations)
        self.assertEqual(len(ledger.all_entries()), 0)

    def test_one_bad_record_in_a_batch_does_not_block_the_good_ones(self):
        good = make_record(record_id="ccov-good").to_dict()
        bad = make_record(record_id="ccov-bad", current_constraint_state="WEAKENED", current_evidence=[]).to_dict()
        path = self._write_file("batch.json", [good, bad])
        ledger = ConstraintLedger(self.events_path)
        results = intake_file(path, ledger, "2026-08-10T00:00:00Z")
        outcomes = {r.record_id: r.outcome for r in results}
        self.assertEqual(outcomes["ccov-good"], ADDED)
        self.assertEqual(outcomes["ccov-bad"], REJECTED)
        self.assertEqual(len(ledger.all_entries()), 1)

    def test_reappending_same_file_reports_duplicate_not_added(self):
        path = self._write_file("one.json", make_record().to_dict())
        ledger = ConstraintLedger(self.events_path)
        intake_file(path, ledger, "2026-08-10T00:00:00Z")
        results = intake_file(path, ledger, "2026-08-11T00:00:00Z")
        self.assertEqual(results[0].outcome, DUPLICATE)
        self.assertEqual(len(ledger.all_entries()), 1)

    def test_validate_file_dry_run_does_not_touch_ledger(self):
        path = self._write_file("one.json", make_record().to_dict())
        results = validate_file(path)
        self.assertEqual(results[0].outcome, ADDED)  # "would be added" - validate_file's ADDED means "valid"
        self.assertFalse(os.path.exists(self.events_path))

    def test_missing_record_id_in_file_raises_before_any_append(self):
        path = self._write_file("no_id.json", {"constraint_family": "cost"})
        ledger = ConstraintLedger(self.events_path)
        with self.assertRaises(ValueError):
            intake_file(path, ledger, "2026-08-10T00:00:00Z")

    def test_seed_probe_records_all_validate_and_load(self):
        seed_path = os.path.join(os.path.dirname(__file__), "..", "seed", "probe-records.json")
        results = validate_file(seed_path)
        self.assertEqual(len(results), 4)
        for r in results:
            self.assertEqual(r.outcome, ADDED, f"{r.record_id} failed: {r.violations}")


if __name__ == "__main__":
    unittest.main()
