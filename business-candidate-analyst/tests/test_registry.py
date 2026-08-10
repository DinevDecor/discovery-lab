import _pathsetup  # noqa: F401
import json
import os
import shutil
import tempfile
import unittest

from business_candidate_analyst.models import CandidateEvent
from business_candidate_analyst.registry import CandidateRegistry, make_event_id, rebuild_snapshot, persist_snapshot, load_snapshot


class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.events_path = os.path.join(self.tmp, "candidate_events.jsonl")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _event(self, event_type, candidate_id, identity, recorded_at="2026-08-08T00:00:00Z", **payload):
        return CandidateEvent(
            event_id=make_event_id(event_type, candidate_id, identity), event_type=event_type,
            candidate_id=candidate_id, recorded_at=recorded_at, reason="test", derived_from=["ANOM-1"],
            payload=payload, analyst_version="0.1.0",
        )

    def test_append_is_idempotent_on_identical_identity(self):
        reg = CandidateRegistry(self.events_path)
        ev1 = self._event("candidate_created", "BC-0001", {"anomaly_ids": ["A1"]}, state="WATCH",
                           anomaly_ids=["A1"], observation_ids=["O1"], dimensions={})
        self.assertTrue(reg.append(ev1))
        # Re-append the SAME logical event (same identity/recorded_at differs) - must be skipped.
        ev2 = self._event("candidate_created", "BC-0001", {"anomaly_ids": ["A1"]},
                           recorded_at="2026-08-09T00:00:00Z", state="WATCH",
                           anomaly_ids=["A1"], observation_ids=["O1"], dimensions={})
        self.assertEqual(ev1.event_id, ev2.event_id, "identity excludes recorded_at by design")
        self.assertFalse(reg.append(ev2))
        self.assertEqual(len(reg.all_events()), 1)

    def test_events_persist_across_reload(self):
        reg = CandidateRegistry(self.events_path)
        reg.append(self._event("candidate_created", "BC-0001", {"anomaly_ids": ["A1"]}, state="WATCH",
                                anomaly_ids=["A1"], observation_ids=["O1"], dimensions={}))
        reg2 = CandidateRegistry(self.events_path)
        self.assertEqual(len(reg2.all_events()), 1)

    def test_file_is_append_only_never_rewritten(self):
        reg = CandidateRegistry(self.events_path)
        reg.append(self._event("candidate_created", "BC-0001", {"anomaly_ids": ["A1"]}, state="WATCH",
                                anomaly_ids=["A1"], observation_ids=["O1"], dimensions={}))
        with open(self.events_path) as f:
            line_count_before = sum(1 for _ in f)
        reg.append(self._event("state_changed", "BC-0001", {"to_state": "VALIDATING"},
                                from_state="WATCH", to_state="VALIDATING", anomaly_ids=["A1"],
                                observation_ids=["O1"], dimensions={}))
        with open(self.events_path) as f:
            lines = f.readlines()
        self.assertEqual(len(lines), line_count_before + 1)
        # First line unchanged (never rewritten).
        first = json.loads(lines[0])
        self.assertEqual(first["event_type"], "candidate_created")

    def test_rebuild_snapshot_preserves_history_across_state_changes(self):
        events = [
            self._event("candidate_created", "BC-0001", {"anomaly_ids": ["A1"]}, state="WATCH",
                         anomaly_ids=["A1"], observation_ids=["O1"], dimensions={"d": 1}).to_dict(),
            self._event("state_changed", "BC-0001", {"to": "VALIDATING"}, from_state="WATCH",
                         to_state="VALIDATING", anomaly_ids=["A1"], observation_ids=["O1", "O2"],
                         dimensions={"d": 2}).to_dict(),
        ]
        candidates = rebuild_snapshot(events)
        self.assertEqual(len(candidates), 1)
        c = candidates[0]
        self.assertEqual(c.state, "VALIDATING")
        self.assertEqual(sorted(c.observation_ids), ["O1", "O2"])
        # Both events are still visible in history - the WATCH-era reason was never overwritten.
        self.assertEqual(len(c.history), 2)
        self.assertEqual(c.history[0]["event_type"], "candidate_created")
        self.assertEqual(c.history[1]["event_type"], "state_changed")

    def test_rebuild_snapshot_tracks_merge(self):
        events = [
            self._event("candidate_created", "BC-0001", {"a": 1}, state="WATCH",
                         anomaly_ids=["A1"], observation_ids=["O1"], dimensions={}).to_dict(),
            self._event("candidate_created", "BC-0002", {"a": 2}, state="WATCH",
                         anomaly_ids=["A2"], observation_ids=["O2"], dimensions={}).to_dict(),
            self._event("candidates_merged", "BC-0002", {"into": "BC-0001"}, merged_into="BC-0001").to_dict(),
            self._event("evidence_reassessed", "BC-0001", {"m": 1}, anomaly_ids=["A1", "A2"],
                        observation_ids=["O1", "O2"], dimensions={}, merged_from=["BC-0002"]).to_dict(),
        ]
        candidates = {c.candidate_id: c for c in rebuild_snapshot(events)}
        self.assertEqual(candidates["BC-0002"].merged_into, "BC-0001")
        self.assertEqual(candidates["BC-0001"].merged_from, ["BC-0002"])
        self.assertEqual(sorted(candidates["BC-0001"].anomaly_ids), ["A1", "A2"])

    def test_persist_and_load_snapshot_roundtrip(self):
        reg = CandidateRegistry(self.events_path)
        reg.append(self._event("candidate_created", "BC-0001", {"anomaly_ids": ["A1"]}, state="WATCH",
                                anomaly_ids=["A1"], observation_ids=["O1"], dimensions={}))
        candidates = rebuild_snapshot(reg.all_events())
        snap_path = os.path.join(self.tmp, "candidates.json")
        persist_snapshot(snap_path, candidates)
        loaded = load_snapshot(snap_path)
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0]["candidate_id"], "BC-0001")

    def test_unknown_event_type_rejected(self):
        reg = CandidateRegistry(self.events_path)
        bad = CandidateEvent(event_id="x", event_type="not_a_real_kind", candidate_id="BC-0001",
                              recorded_at="2026-08-08T00:00:00Z", reason="r", derived_from=[], payload={},
                              analyst_version="0.1.0")
        with self.assertRaises(ValueError):
            reg.append(bad)


if __name__ == "__main__":
    unittest.main()
