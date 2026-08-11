"""Offline, deterministic tests for material_events.detect_material_events:
the daily pipeline must stay silent on ordinary WATCH creation and
same-state evidence accumulation, and must fire exactly on the six
material categories the operating contract defines (five of which are
BCA registry events; the sixth, pipeline failure, is handled separately
by run_daily_pipeline.py and tested in test_daily_pipeline.py)."""

import _pathsetup  # noqa: F401
import unittest

from business_candidate_analyst.material_events import detect_material_events


def _event(event_type, candidate_id, payload=None, reason="", recorded_at="2026-08-12T00:00:00Z"):
    return {
        "event_id": f"{event_type}:{candidate_id}:test",
        "event_type": event_type,
        "candidate_id": candidate_id,
        "recorded_at": recorded_at,
        "reason": reason,
        "payload": payload or {},
    }


class MaterialEventDetectionTests(unittest.TestCase):
    def test_candidate_created_is_never_material(self):
        events = [_event("candidate_created", "BC-0001", {"state": "WATCH"})]
        self.assertEqual(detect_material_events(events), [])

    def test_same_state_evidence_reassessed_is_never_material(self):
        events = [_event("evidence_reassessed", "BC-0001", {"anomaly_ids": [], "observation_ids": []})]
        self.assertEqual(detect_material_events(events), [])

    def test_watch_to_validating_is_material(self):
        events = [_event("state_changed", "BC-0001", {"from_state": "WATCH", "to_state": "VALIDATING"})]
        material = detect_material_events(events)
        self.assertEqual(len(material), 1)
        self.assertEqual(material[0]["material_type"], "lifecycle_escalation")
        self.assertEqual(material[0]["candidate_id"], "BC-0001")

    def test_validating_to_investigate_is_material(self):
        events = [_event("state_changed", "BC-0002", {"from_state": "VALIDATING", "to_state": "INVESTIGATE"})]
        material = detect_material_events(events)
        self.assertEqual(len(material), 1)
        self.assertEqual(material[0]["material_type"], "lifecycle_escalation")

    def test_investigate_to_promising_is_material(self):
        events = [_event("state_changed", "BC-0003", {"from_state": "INVESTIGATE", "to_state": "PROMISING"})]
        material = detect_material_events(events)
        self.assertEqual(len(material), 1)
        self.assertEqual(material[0]["material_type"], "lifecycle_escalation")

    def test_rejected_from_validating_or_higher_is_material(self):
        for from_state in ("VALIDATING", "INVESTIGATE", "PROMISING"):
            with self.subTest(from_state=from_state):
                events = [_event("state_changed", "BC-0004", {"from_state": from_state, "to_state": "REJECTED"})]
                material = detect_material_events(events)
                self.assertEqual(len(material), 1)
                self.assertEqual(material[0]["material_type"], "lifecycle_rejection")

    def test_rejected_from_watch_is_not_material(self):
        """REJECTED directly from WATCH never earned attention in the
        first place - silent, per the operating contract."""
        events = [_event("state_changed", "BC-0005", {"from_state": "WATCH", "to_state": "REJECTED"})]
        self.assertEqual(detect_material_events(events), [])

    def test_merge_with_no_state_change_is_not_material(self):
        """The common case: two WATCH candidates bridge and the canonical
        one stays WATCH - no state_changed event fires at all, so there
        is nothing to surface."""
        events = [_event("candidates_merged", "BC-0006", {"merged_into": "BC-0007"})]
        self.assertEqual(detect_material_events(events), [])

    def test_merge_that_changes_lifecycle_state_is_material(self):
        events = [
            _event("candidates_merged", "BC-0006", {"merged_into": "BC-0007"}),
            _event("state_changed", "BC-0007", {"from_state": "WATCH", "to_state": "VALIDATING"}),
        ]
        material = detect_material_events(events)
        # The state_changed event is itself a WATCH->VALIDATING escalation,
        # so it is labeled by the more specific category - the merge
        # context is still implicit in it being on the just-merged-into id.
        self.assertEqual(len(material), 1)
        self.assertEqual(material[0]["material_type"], "lifecycle_escalation")
        self.assertEqual(material[0]["candidate_id"], "BC-0007")

    def test_merge_target_state_change_not_itself_an_escalation_is_still_material(self):
        """A merge can change state via a non-ladder path (e.g. a
        REJECTED candidate merging into a WATCH one that then advances
        for reasons unrelated to a clean ladder step); any state_changed
        on the just-merged-into candidate this run is material."""
        events = [
            _event("candidates_merged", "BC-0008", {"merged_into": "BC-0009"}),
            _event("state_changed", "BC-0009", {"from_state": "REJECTED", "to_state": "WATCH"}),
        ]
        material = detect_material_events(events)
        self.assertEqual(len(material), 1)
        self.assertEqual(material[0]["material_type"], "merge_with_lifecycle_change")
        self.assertEqual(material[0]["candidate_id"], "BC-0009")

    def test_mixed_run_only_material_events_surface(self):
        events = [
            _event("candidate_created", "BC-0010", {"state": "WATCH"}),
            _event("evidence_reassessed", "BC-0011", {}),
            _event("state_changed", "BC-0012", {"from_state": "WATCH", "to_state": "VALIDATING"}),
            _event("state_changed", "BC-0013", {"from_state": "WATCH", "to_state": "REJECTED"}),
        ]
        material = detect_material_events(events)
        self.assertEqual([m["candidate_id"] for m in material], ["BC-0012"])


if __name__ == "__main__":
    unittest.main()
