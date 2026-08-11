"""Regression tests for the cross-mode candidate-resolution bug: Mode A's
analyst.py built anomaly_to_candidate from ALL prior candidates regardless
of candidate_type, so any anomaly_id shared between a NEW_MARKET candidate
and an OLD_BUSINESS_REARCHITECTURE candidate resolved (last-write-wins,
since rebuild_snapshot returns candidates sorted by candidate_id and Mode B
always gets the higher id) to the Mode B candidate - silently starving the
real NEW_MARKET candidate of reassessment and burning incorrect events into
the append-only log of the Mode B candidate it wrongly grabbed.

`tests/fixtures/ca_rearch_run1` already contains exactly the shared-anomaly
shape needed: OBS-BANK1 and OBS-BANK2 share one source URL, so both Mode
A's signature gate (its own shared-URL short-circuit in
signature.same_opportunity) and Mode B's URL-union-find group ANOM-BANK1 +
ANOM-BANK2 into one group each - the same anomaly pair legitimately seeds
one NEW_MARKET candidate and one OLD_BUSINESS_REARCHITECTURE candidate,
exactly the "same evidence, two lenses" case the docstrings describe as
intentional.
"""

import _pathsetup  # noqa: F401
import json
import os
import shutil
import tempfile
import unittest

from business_candidate_analyst.analyst import run_analysis as run_mode_a
from business_candidate_analyst.config import load_rearchitecture_thresholds, load_thresholds
from business_candidate_analyst.models import NEW_MARKET, OLD_BUSINESS_REARCHITECTURE
from business_candidate_analyst.rearchitecture.analyst import run_analysis as run_mode_b
from business_candidate_analyst.registry import CandidateRegistry, rebuild_snapshot

_FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")
_BANK_GROUP = frozenset({"ANOM-BANK1", "ANOM-BANK2"})


class CrossModeResolutionTests(unittest.TestCase):
    def setUp(self):
        self.data_dir = tempfile.mkdtemp()
        self.rearch_cfg = load_rearchitecture_thresholds()
        self.thresholds = load_thresholds()

    def tearDown(self):
        shutil.rmtree(self.data_dir, ignore_errors=True)

    def _events(self):
        path = os.path.join(self.data_dir, "candidate_events.jsonl")
        if not os.path.exists(path):
            return []
        with open(path, encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]

    def _bank_ids(self, day1_a, day1_b):
        a_id = next(c.candidate_id for c in day1_a["candidates"] if set(c.anomaly_ids) == _BANK_GROUP)
        b_id = next(c.candidate_id for c in day1_b["candidates"] if set(c.anomaly_ids) == _BANK_GROUP)
        return a_id, b_id

    def _run_both(self, fixture, now):
        a = run_mode_a(os.path.join(_FIXTURES, fixture), self.data_dir, now=now)
        b = run_mode_b(os.path.join(_FIXTURES, fixture), self.data_dir, self.rearch_cfg, now=now)
        return a, b

    # -- 2.A -----------------------------------------------------------
    def test_mode_a_resolves_shared_anomaly_to_new_market_candidate_only(self):
        day1_a, day1_b = self._run_both("ca_rearch_run1", "2026-08-10T00:00:00Z")
        bank_a_id, bank_b_id = self._bank_ids(day1_a, day1_b)
        self.assertNotEqual(bank_a_id, bank_b_id)

        events_before = len(self._events())
        day2_a = run_mode_a(os.path.join(_FIXTURES, "ca_rearch_run1"), self.data_dir, now="2026-08-11T00:00:00Z")
        events_after = self._events()[events_before:]

        touched_ids = {e["candidate_id"] for e in events_after}
        self.assertNotIn(bank_b_id, touched_ids,
                          "Mode A must never append an event to a Mode B (OLD_BUSINESS_REARCHITECTURE) candidate")

        bank_group_report = next(g for g in day2_a["group_reports"]
                                  if set(g["anomaly_ids"]) == _BANK_GROUP)
        self.assertEqual(bank_group_report["candidate_id"], bank_a_id,
                          "Mode A must resolve the shared anomaly group back to its own NEW_MARKET candidate")

        for c in day2_a["candidates"]:
            self.assertEqual(c.candidate_type, NEW_MARKET)

    # -- 2.B -------------------------------------------------------------
    def test_mode_b_resolves_shared_anomaly_to_rearchitecture_candidate_only(self):
        day1_a, day1_b = self._run_both("ca_rearch_run1", "2026-08-10T00:00:00Z")
        bank_a_id, bank_b_id = self._bank_ids(day1_a, day1_b)

        events_before = len(self._events())
        day2_b = run_mode_b(os.path.join(_FIXTURES, "ca_rearch_run1"), self.data_dir, self.rearch_cfg,
                             now="2026-08-11T00:00:00Z")
        events_after = self._events()[events_before:]

        touched_ids = {e["candidate_id"] for e in events_after}
        self.assertNotIn(bank_a_id, touched_ids,
                          "Mode B must never append an event to a Mode A (NEW_MARKET) candidate")

        bank_group_report = next(g for g in day2_b["group_reports"]
                                  if set(g["anomaly_ids"]) == _BANK_GROUP)
        self.assertEqual(bank_group_report["candidate_id"], bank_b_id,
                          "Mode B must resolve the shared anomaly group back to its own rearchitecture candidate")

        for c in day2_b["candidates"]:
            self.assertEqual(c.candidate_type, OLD_BUSINESS_REARCHITECTURE)

    # -- 2.C ---------------------------------------------------------------
    def test_rerun_on_unchanged_corpus_is_a_true_no_op(self):
        self._run_both("ca_rearch_run1", "2026-08-10T00:00:00Z")
        snapshot_before = json.dumps(
            [c.__dict__ for c in rebuild_snapshot(CandidateRegistry(
                os.path.join(self.data_dir, "candidate_events.jsonl")).all_events())],
            sort_keys=True, default=str)
        events_before = self._events()

        day2_a, day2_b = self._run_both("ca_rearch_run1", "2026-08-11T00:00:00Z")

        self.assertEqual(day2_a["events_appended"], 0,
                          "re-running Mode A on identical evidence must append zero events")
        self.assertEqual(day2_b["events_appended"], 0,
                          "re-running Mode B on identical evidence must append zero events")
        self.assertEqual(self._events(), events_before,
                          "candidate_events.jsonl must be byte-for-byte unchanged after a true no-op re-run")

        snapshot_after = json.dumps(
            [c.__dict__ for c in rebuild_snapshot(CandidateRegistry(
                os.path.join(self.data_dir, "candidate_events.jsonl")).all_events())],
            sort_keys=True, default=str)
        self.assertEqual(snapshot_before, snapshot_after,
                          "no candidate's dimensions/state may drift on a re-run with no new evidence")

    # -- 2.D -----------------------------------------------------------
    def test_execution_order_does_not_affect_final_resolution(self):
        def _signature(candidates):
            return sorted(
                (c.candidate_type, tuple(sorted(c.anomaly_ids)), c.state)
                for c in candidates
            )

        dir_ab = tempfile.mkdtemp()
        dir_ba = tempfile.mkdtemp()
        try:
            a1 = run_mode_a(os.path.join(_FIXTURES, "ca_rearch_run1"), dir_ab, now="2026-08-10T00:00:00Z")
            b1 = run_mode_b(os.path.join(_FIXTURES, "ca_rearch_run1"), dir_ab, self.rearch_cfg,
                             now="2026-08-10T00:00:01Z")

            b2 = run_mode_b(os.path.join(_FIXTURES, "ca_rearch_run1"), dir_ba, self.rearch_cfg,
                             now="2026-08-10T00:00:00Z")
            a2 = run_mode_a(os.path.join(_FIXTURES, "ca_rearch_run1"), dir_ba, now="2026-08-10T00:00:01Z")

            registry_ab = CandidateRegistry(os.path.join(dir_ab, "candidate_events.jsonl"))
            registry_ba = CandidateRegistry(os.path.join(dir_ba, "candidate_events.jsonl"))
            candidates_ab = rebuild_snapshot(registry_ab.all_events())
            candidates_ba = rebuild_snapshot(registry_ba.all_events())

            self.assertEqual(len(candidates_ab), len(candidates_ba))
            self.assertEqual(_signature(candidates_ab), _signature(candidates_ba),
                              "the set of (type, anomaly_ids, state) triples must not depend on run order, "
                              "even though the specific BC-#### labels assigned legitimately can")
        finally:
            shutil.rmtree(dir_ab, ignore_errors=True)
            shutil.rmtree(dir_ba, ignore_errors=True)

    # -- 2.E -----------------------------------------------------------
    def test_skip_mode_b_does_not_corrupt_mode_b_candidates(self):
        day1_a, day1_b = self._run_both("ca_rearch_run1", "2026-08-10T00:00:00Z")
        _, bank_b_id = self._bank_ids(day1_a, day1_b)
        bank_b_before = next(c for c in day1_b["candidates"] if c.candidate_id == bank_b_id)

        # Mode-A-only re-run, mirroring the CLI's --skip-mode-b flag.
        run_mode_a(os.path.join(_FIXTURES, "ca_rearch_run1"), self.data_dir, now="2026-08-11T00:00:00Z")

        candidates_after = rebuild_snapshot(
            CandidateRegistry(os.path.join(self.data_dir, "candidate_events.jsonl")).all_events())
        bank_b_after = next(c for c in candidates_after if c.candidate_id == bank_b_id)

        self.assertEqual(bank_b_after.state, bank_b_before.state)
        self.assertEqual(bank_b_after.rearchitecture, bank_b_before.rearchitecture)
        self.assertEqual(len(bank_b_after.history), len(bank_b_before.history),
                          "a Mode-A-only run must never append to a Mode B candidate's history")


if __name__ == "__main__":
    unittest.main()
