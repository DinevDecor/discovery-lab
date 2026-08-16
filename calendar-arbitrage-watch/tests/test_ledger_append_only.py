"""Append-only + idempotency + supersedes-lineage guarantees, mirroring
constraint_change_observatory/tests/test_ledger.py's own coverage.
"""

import _pathsetup  # noqa: F401
import json
import os
import tempfile
import unittest

from calendar_arbitrage_watch import ledger
from calendar_arbitrage_watch.models import CalendarAssessment, WATCH


def _assessment(candidate_id="c1", supersedes=None, lifecycle_state=WATCH, title="t") -> CalendarAssessment:
    return CalendarAssessment(candidate_id=candidate_id, supersedes=supersedes,
                               lifecycle_state=lifecycle_state, title=title)


class LedgerAppendOnlyTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.events_path = os.path.join(self.tmpdir, "calendar_events.jsonl")

    def test_append_writes_one_line(self):
        led = ledger.CalendarLedger(self.events_path)
        written = led.append(_assessment(), "2026-08-15T00:00:00Z")
        self.assertTrue(written)
        with open(self.events_path) as f:
            lines = f.readlines()
        self.assertEqual(len(lines), 1)

    def test_identical_reappend_is_idempotent(self):
        led = ledger.CalendarLedger(self.events_path)
        led.append(_assessment(), "2026-08-15T00:00:00Z")
        written_again = led.append(_assessment(), "2026-08-15T00:00:00Z")
        self.assertFalse(written_again)
        with open(self.events_path) as f:
            lines = f.readlines()
        self.assertEqual(len(lines), 1)

    def test_a_content_change_is_a_new_line_never_an_edit(self):
        led = ledger.CalendarLedger(self.events_path)
        led.append(_assessment(lifecycle_state=WATCH), "2026-08-15T00:00:00Z")
        led.append(_assessment(lifecycle_state="CHEAP_TEST"), "2026-08-16T00:00:00Z")
        with open(self.events_path) as f:
            lines = [json.loads(l) for l in f]
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0]["record"]["lifecycle_state"], WATCH)
        self.assertEqual(lines[1]["record"]["lifecycle_state"], "CHEAP_TEST")

    def test_rebuild_snapshot_takes_latest_line_per_candidate(self):
        led = ledger.CalendarLedger(self.events_path)
        led.append(_assessment(lifecycle_state=WATCH), "2026-08-15T00:00:00Z")
        led.append(_assessment(lifecycle_state="CHEAP_TEST"), "2026-08-16T00:00:00Z")
        snapshot = ledger.rebuild_snapshot(led.all_entries())
        self.assertEqual(len(snapshot["current"]), 1)
        self.assertEqual(snapshot["current"][0]["lifecycle_state"], "CHEAP_TEST")
        self.assertEqual(len(snapshot["history"]["c1"]), 2)

    def test_supersedes_excludes_the_old_lineage_from_current(self):
        led = ledger.CalendarLedger(self.events_path)
        led.append(_assessment(candidate_id="old-1"), "2026-08-15T00:00:00Z")
        led.append(_assessment(candidate_id="new-1", supersedes="old-1"), "2026-08-16T00:00:00Z")
        snapshot = ledger.rebuild_snapshot(led.all_entries())
        current_ids = {r["candidate_id"] for r in snapshot["current"]}
        superseded_ids = {r["candidate_id"] for r in snapshot["superseded"]}
        self.assertEqual(current_ids, {"new-1"})
        self.assertEqual(superseded_ids, {"old-1"})

    def test_superseded_record_is_retained_not_dropped(self):
        led = ledger.CalendarLedger(self.events_path)
        led.append(_assessment(candidate_id="old-1"), "2026-08-15T00:00:00Z")
        led.append(_assessment(candidate_id="new-1", supersedes="old-1"), "2026-08-16T00:00:00Z")
        snapshot = ledger.rebuild_snapshot(led.all_entries())
        self.assertEqual(len(snapshot["superseded"]), 1)

    def test_persist_and_load_snapshot_round_trip(self):
        led = ledger.CalendarLedger(self.events_path)
        led.append(_assessment(), "2026-08-15T00:00:00Z")
        snapshot = ledger.rebuild_snapshot(led.all_entries())
        snapshot_path = os.path.join(self.tmpdir, "calendar_candidates.json")
        ledger.persist_snapshot(snapshot_path, snapshot)
        loaded = ledger.load_snapshot(snapshot_path)
        self.assertEqual(loaded["current"], snapshot["current"])

    def test_a_reloaded_ledger_knows_previously_written_ids(self):
        led1 = ledger.CalendarLedger(self.events_path)
        led1.append(_assessment(), "2026-08-15T00:00:00Z")
        led2 = ledger.CalendarLedger(self.events_path)  # fresh instance, same file
        self.assertEqual(led2.known_count, 1)
        self.assertFalse(led2.append(_assessment(), "2026-08-15T00:00:00Z"))  # idempotent across instances too

    def test_corrupt_line_is_skipped_not_fatal(self):
        os.makedirs(self.tmpdir, exist_ok=True)
        with open(self.events_path, "w", encoding="utf-8") as f:
            f.write("not valid json\n")
        led = ledger.CalendarLedger(self.events_path)  # must not raise
        self.assertEqual(led.known_count, 0)


if __name__ == "__main__":
    unittest.main()
