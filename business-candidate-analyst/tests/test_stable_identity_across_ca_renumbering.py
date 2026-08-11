"""Regression tests for the anomaly_id-instability defect: Constraint
Archaeology's own anomaly_id is assigned positionally during its
non-append-only rebuild of anomalies.json
(`ANOM-{len(anomalies)+1:04d}` in ca_agents.memory.rebuild_anomalies), so
the same real observations can land under a different ANOM-#### label on
a later CA run. analyst.py (both modes) used to build its reverse
candidate lookup from each candidate's stored anomaly_ids - a lookup that
silently fails to find a candidate's own evidence once CA reshuffles that
evidence's numbering, risking a duplicate candidate for evidence this
tool has already seen and recorded.

The fix re-keys that reverse lookup on observation_id, which Constraint
Archaeology's Sensor Agent assigns once and never renumbers. These tests
simulate a CA rebuild that changes anomaly_id labels for unchanged
observation_ids/content, mirroring the real defect exactly rather than
testing the mechanism in the abstract.
"""

import _pathsetup  # noqa: F401
import os
import shutil
import tempfile
import unittest

from business_candidate_analyst.analyst import run_analysis as run_mode_a
from business_candidate_analyst.config import load_rearchitecture_thresholds
from business_candidate_analyst.models import NEW_MARKET, OLD_BUSINESS_REARCHITECTURE
from business_candidate_analyst.rearchitecture.analyst import run_analysis as run_mode_b
from business_candidate_analyst.registry import CandidateRegistry, rebuild_snapshot

_FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


class StableIdentityAcrossRenumberingTests(unittest.TestCase):
    def setUp(self):
        self.data_dir = tempfile.mkdtemp()
        self.rearch_cfg = load_rearchitecture_thresholds()

    def tearDown(self):
        shutil.rmtree(self.data_dir, ignore_errors=True)

    def _all_candidates(self):
        events = CandidateRegistry(os.path.join(self.data_dir, "candidate_events.jsonl")).all_events()
        return rebuild_snapshot(events)

    # -- A/B: ANOM-0007=[OBS-A,OBS-B] -> renumbered to ANOM-0042 ----------
    def test_AB_renumbered_anomaly_id_still_resolves_to_existing_candidate(self):
        day1 = run_mode_a(os.path.join(_FIXTURES, "ca_renumber_day1"), self.data_dir, now="2026-08-10T00:00:00Z")
        created = [g for g in day1["group_reports"] if g["kind"] == "created"]
        self.assertEqual(len(created), 1)
        bc_x = created[0]["candidate_id"]
        self.assertEqual(set(day1["candidates"][0].observation_ids), {"OBS-A", "OBS-B"})

        day2 = run_mode_a(os.path.join(_FIXTURES, "ca_renumber_day2"), self.data_dir, now="2026-08-11T00:00:00Z")

        all_candidates = self._all_candidates()
        mode_a_candidates = [c for c in all_candidates if c.candidate_type == NEW_MARKET]
        self.assertEqual(len(mode_a_candidates), 1,
                          "renumbering ANOM-0007 -> ANOM-0042 for the SAME observations must not create a "
                          "second candidate")
        self.assertEqual(mode_a_candidates[0].candidate_id, bc_x, "the original candidate_id must be reused")
        self.assertEqual(set(mode_a_candidates[0].observation_ids), {"OBS-A", "OBS-B"},
                          "no evidence lost across the renumbering")

        touched = [g for g in day2["group_reports"] if g.get("candidate_id") == bc_x]
        self.assertEqual(len(touched), 1, "BC-X must be found and reassessed exactly once, not duplicated")
        self.assertNotEqual(touched[0]["kind"], "created", "must not be re-created as if it were new evidence")

    # -- F: idempotency on a renumbered snapshot ---------------------------
    def test_F_second_run_on_renumbered_snapshot_appends_zero_events(self):
        run_mode_a(os.path.join(_FIXTURES, "ca_renumber_day1"), self.data_dir, now="2026-08-10T00:00:00Z")
        run_mode_a(os.path.join(_FIXTURES, "ca_renumber_day2"), self.data_dir, now="2026-08-11T00:00:00Z")

        events_before = len(CandidateRegistry(os.path.join(self.data_dir, "candidate_events.jsonl")).all_events())
        result_again = run_mode_a(os.path.join(_FIXTURES, "ca_renumber_day2"), self.data_dir,
                                   now="2026-08-11T01:00:00Z")
        self.assertEqual(result_again["events_appended"], 0,
                          "re-running the same renumbered snapshot a second time must append zero events")
        events_after = len(CandidateRegistry(os.path.join(self.data_dir, "candidate_events.jsonl")).all_events())
        self.assertEqual(events_before, events_after)

    # -- C: partial regroup - ANOM-0010=[A,B] -> ANOM-0030=[A], ANOM-0031=[B]
    def test_C_partial_regroup_both_fragments_resolve_to_same_candidate(self):
        day1 = run_mode_a(os.path.join(_FIXTURES, "ca_renumber_partial_day1"), self.data_dir,
                           now="2026-08-10T00:00:00Z")
        bc_x = next(g["candidate_id"] for g in day1["group_reports"] if g["kind"] == "created")

        day2 = run_mode_a(os.path.join(_FIXTURES, "ca_renumber_partial_day2"), self.data_dir,
                           now="2026-08-11T00:00:00Z")

        # Sanity: the fixture genuinely fragments into 2 disjoint fresh
        # groups under the gate (verified independently in session notes);
        # this is exactly the harder case - identity must not depend on
        # anomaly_id even when the fresh grouping itself is fragmented.
        touched = [g for g in day2["group_reports"] if g.get("candidate_id") == bc_x]
        self.assertEqual(len(touched), 1,
                          "both post-split anomalies must resolve back to the one existing candidate and be "
                          "reassessed together exactly once, not once per fragment")

        all_candidates = self._all_candidates()
        mode_a_candidates = [c for c in all_candidates if c.candidate_type == NEW_MARKET]
        self.assertEqual(len(mode_a_candidates), 1,
                          "splitting one anomaly into two must not produce a duplicate candidate")
        self.assertEqual(set(mode_a_candidates[0].observation_ids), {"OBS-PA", "OBS-PB"},
                          "no evidence lost when CA splits the anomaly that originally carried both")

    # -- D: opposite direction - two separate anomalies bridged into one --
    def test_D_anomaly_bridging_merges_existing_candidates_not_duplicates(self):
        day1 = run_mode_a(os.path.join(_FIXTURES, "ca_renumber_bridge_day1"), self.data_dir,
                           now="2026-08-10T00:00:00Z")
        created = [g["candidate_id"] for g in day1["group_reports"] if g["kind"] == "created"]
        self.assertEqual(len(created), 2, "sanity: day 1's two unrelated anomalies must seed two candidates")

        day2 = run_mode_a(os.path.join(_FIXTURES, "ca_renumber_bridge_day2"), self.data_dir,
                           now="2026-08-11T00:00:00Z")

        all_candidates = self._all_candidates()
        mode_a_candidates = [c for c in all_candidates if c.candidate_type == NEW_MARKET]
        self.assertEqual(len(mode_a_candidates), 2,
                          "CA reclustering OBS-Q1/OBS-Q2 into one anomaly must bridge the two EXISTING "
                          "candidates via candidates_merged, never create a third, duplicate candidate")

        merged_report = next((g for g in day2["group_reports"] if g["kind"] == "merged"), None)
        self.assertIsNotNone(merged_report, "the bridge must be recorded as an explicit candidates_merged event")
        surviving = next(c for c in mode_a_candidates if c.candidate_id != merged_report["candidate_id"])
        self.assertEqual(surviving.merged_from, [merged_report["candidate_id"]])
        merged_away = next(c for c in mode_a_candidates if c.candidate_id == merged_report["candidate_id"])
        self.assertEqual(merged_away.merged_into, surviving.candidate_id)

    # -- E: mode isolation must survive renumbering ------------------------
    def test_E_mode_isolation_survives_renumbering(self):
        day1_a = run_mode_a(os.path.join(_FIXTURES, "ca_renumber_isolation_day1"), self.data_dir,
                             now="2026-08-10T00:00:00Z")
        day1_b = run_mode_b(os.path.join(_FIXTURES, "ca_renumber_isolation_day1"), self.data_dir, self.rearch_cfg,
                             now="2026-08-10T00:00:01Z")

        bc_a = next(g["candidate_id"] for g in day1_a["group_reports"] if g["kind"] == "created")
        bc_b = next(g["candidate_id"] for g in day1_b["group_reports"] if g["kind"] == "created")
        self.assertNotEqual(bc_a, bc_b)

        events_before = len(CandidateRegistry(os.path.join(self.data_dir, "candidate_events.jsonl")).all_events())

        day2_a = run_mode_a(os.path.join(_FIXTURES, "ca_renumber_isolation_day2"), self.data_dir,
                             now="2026-08-11T00:00:00Z")
        events_after_a = CandidateRegistry(os.path.join(self.data_dir, "candidate_events.jsonl")).all_events()
        new_events_from_a = events_after_a[events_before:]

        day2_b = run_mode_b(os.path.join(_FIXTURES, "ca_renumber_isolation_day2"), self.data_dir, self.rearch_cfg,
                             now="2026-08-11T00:00:01Z")
        events_after_b = CandidateRegistry(os.path.join(self.data_dir, "candidate_events.jsonl")).all_events()
        new_events_from_b = events_after_b[len(events_after_a):]

        self.assertNotIn(bc_b, {e["candidate_id"] for e in new_events_from_a},
                          "Mode A's renumbered re-run must never touch Mode B's candidate")
        self.assertNotIn(bc_a, {e["candidate_id"] for e in new_events_from_b},
                          "Mode B's renumbered re-run must never touch Mode A's candidate")

        a_group = next(g for g in day2_a["group_reports"] if g.get("candidate_id") == bc_a)
        self.assertEqual(a_group["candidate_id"], bc_a)
        b_group = next(g for g in day2_b["group_reports"] if g.get("candidate_id") == bc_b)
        self.assertEqual(b_group["candidate_id"], bc_b)

        all_candidates = self._all_candidates()
        mode_a_candidates = [c for c in all_candidates if c.candidate_type == NEW_MARKET]
        mode_b_candidates = [c for c in all_candidates if c.candidate_type == OLD_BUSINESS_REARCHITECTURE]
        self.assertEqual(len(mode_a_candidates), 1, "renumbering must not duplicate the NEW_MARKET candidate")
        self.assertEqual(len(mode_b_candidates), 1,
                          "renumbering must not duplicate the OLD_BUSINESS_REARCHITECTURE candidate")
        self.assertEqual(mode_a_candidates[0].candidate_id, bc_a)
        self.assertEqual(mode_b_candidates[0].candidate_id, bc_b)


if __name__ == "__main__":
    unittest.main()
