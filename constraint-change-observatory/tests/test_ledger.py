import _pathsetup  # noqa: F401
import json
import os
import shutil
import tempfile
import unittest

from _factories import ev, make_record
from constraint_change_observatory.ledger import (
    ConstraintLedger, current_records, load_snapshot, make_entry_id, persist_snapshot, rebuild_snapshot,
)
from constraint_change_observatory.schema import OBSERVED, WEAKENED


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.events_path = os.path.join(self.tmp, "constraint_events.jsonl")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_append_and_reload(self):
        ledger = ConstraintLedger(self.events_path)
        record = make_record()
        self.assertTrue(ledger.append(record, "2026-08-10T00:00:00Z"))
        ledger2 = ConstraintLedger(self.events_path)
        self.assertEqual(len(ledger2.all_entries()), 1)

    def test_idempotent_reappend_of_identical_content(self):
        ledger = ConstraintLedger(self.events_path)
        record = make_record()
        self.assertTrue(ledger.append(record, "2026-08-10T00:00:00Z"))
        self.assertFalse(ledger.append(record, "2026-08-11T00:00:00Z"))  # same content, different recorded_at
        self.assertEqual(len(ledger.all_entries()), 1)

    def test_revision_of_same_record_id_appends_new_line_not_overwrite(self):
        ledger = ConstraintLedger(self.events_path)
        r1 = make_record(current_constraint_state="INSUFFICIENT_DATA", current_evidence=[])
        r2 = make_record(current_constraint_state=WEAKENED,
                          current_evidence=[ev("New current source", "x", "n/a", "2026")])
        ledger.append(r1, "2026-08-10T00:00:00Z")
        ledger.append(r2, "2026-08-11T00:00:00Z")
        with open(self.events_path) as f:
            self.assertEqual(sum(1 for _ in f), 2)  # both lines present, neither rewritten
        snapshot = rebuild_snapshot(ledger.all_entries())
        current = {r["record_id"]: r for r in snapshot["current"]}
        self.assertEqual(current["ccov-test-0001"]["current_constraint_state"], WEAKENED)  # latest wins
        self.assertEqual(len(snapshot["history"]["ccov-test-0001"]), 2)  # but both are still in history

    def test_file_never_rewritten_only_appended(self):
        ledger = ConstraintLedger(self.events_path)
        ledger.append(make_record(record_id="ccov-a"), "2026-08-10T00:00:00Z")
        with open(self.events_path) as f:
            first_line = f.readline()
        ledger.append(make_record(record_id="ccov-b"), "2026-08-10T00:01:00Z")
        with open(self.events_path) as f:
            lines = f.readlines()
        self.assertEqual(lines[0], first_line)

    def test_supersedes_excludes_old_record_from_current_but_keeps_it_in_history(self):
        ledger = ConstraintLedger(self.events_path)
        old = make_record(record_id="ccov-old")
        new = make_record(record_id="ccov-new", supersedes="ccov-old")
        ledger.append(old, "2026-08-10T00:00:00Z")
        ledger.append(new, "2026-08-11T00:00:00Z")
        snapshot = rebuild_snapshot(ledger.all_entries())
        current_ids = {r["record_id"] for r in snapshot["current"]}
        superseded_ids = {r["record_id"] for r in snapshot["superseded"]}
        self.assertEqual(current_ids, {"ccov-new"})
        self.assertEqual(superseded_ids, {"ccov-old"})
        self.assertIn("ccov-old", snapshot["history"])  # never dropped

    def test_persist_and_load_snapshot_roundtrip(self):
        ledger = ConstraintLedger(self.events_path)
        ledger.append(make_record(), "2026-08-10T00:00:00Z")
        snapshot = rebuild_snapshot(ledger.all_entries())
        snap_path = os.path.join(self.tmp, "constraints.json")
        persist_snapshot(snap_path, snapshot)
        loaded = load_snapshot(snap_path)
        self.assertEqual(len(loaded["current"]), 1)

    def test_current_records_returns_typed_objects(self):
        ledger = ConstraintLedger(self.events_path)
        ledger.append(make_record(), "2026-08-10T00:00:00Z")
        records = current_records(ledger.all_entries())
        self.assertEqual(records[0].record_id, "ccov-test-0001")

    def test_make_entry_id_is_deterministic(self):
        record = make_record()
        self.assertEqual(make_entry_id(record), make_entry_id(record))

    def test_corrupt_line_is_skipped_not_fatal(self):
        os.makedirs(self.tmp, exist_ok=True)
        with open(self.events_path, "w") as f:
            f.write("{not valid json\n")
            f.write(json.dumps({"entry_id": "x", "recorded_at": "2026-08-10T00:00:00Z",
                                  "record": make_record().to_dict()}) + "\n")
        ledger = ConstraintLedger(self.events_path)
        self.assertEqual(len(ledger.all_entries()), 1)


if __name__ == "__main__":
    unittest.main()
