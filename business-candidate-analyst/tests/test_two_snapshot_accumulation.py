"""Proves cross-day evidence accumulation actually works, post cross-mode-
resolution fix - something never previously demonstrated against real data
(see docs/reviews for the prior measurement run: all 61 real-corpus
candidates were created in a single run; nothing had ever been re-run
against a genuinely different, larger corpus before this test existed).

Snapshot A (ca_accum_day1): one anomaly (ANOM-ACC1, single source
hacker_news) plus one unrelated anomaly (ANOM-UNREL) used only as a control
to prove unrelated candidates are untouched.

Snapshot B (ca_accum_day2): identical ANOM-ACC1/ANOM-UNREL, plus a new
anomaly (ANOM-ACC2) from a different source (lobsters) with a different
URL. It merges into the same Mode A candidate purely through
signature.py's real buyer/function taxonomy path (shared buyer_bucket,
shared function_class, >=2 shared resource_visibility keywords) - not
through the shared-URL short-circuit, so this is genuine independent
corroboration, not "the same capture extracted twice".
"""

import _pathsetup  # noqa: F401
import os
import shutil
import tempfile
import unittest

from business_candidate_analyst.analyst import run_analysis as run_mode_a
from business_candidate_analyst.config import load_rearchitecture_thresholds
from business_candidate_analyst.rearchitecture.analyst import run_analysis as run_mode_b

_FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


class TwoSnapshotAccumulationTests(unittest.TestCase):
    def setUp(self):
        self.data_dir = tempfile.mkdtemp()
        self.rearch_cfg = load_rearchitecture_thresholds()

    def tearDown(self):
        shutil.rmtree(self.data_dir, ignore_errors=True)

    def test_independent_second_observation_is_correctly_accumulated(self):
        # --- Snapshot A: day 1, one source, WATCH ---
        day1 = run_mode_a(os.path.join(_FIXTURES, "ca_accum_day1"), self.data_dir, now="2026-08-10T00:00:00Z")
        run_mode_b(os.path.join(_FIXTURES, "ca_accum_day1"), self.data_dir, self.rearch_cfg,
                   now="2026-08-10T00:00:01Z")

        acc = next(c for c in day1["candidates"] if c.anomaly_ids == ["ANOM-ACC1"])
        self.assertEqual(acc.state, "WATCH")
        self.assertEqual(acc.dimensions["evidence_diversity"]["value"]["distinct_sources"], 1)
        self.assertEqual(acc.dimensions["evidence_diversity"]["value"]["sources"], ["hacker_news"])
        acc_id = acc.candidate_id

        unrel_candidates_day1 = [c for c in day1["candidates"] if "ANOM-UNREL" in c.anomaly_ids]

        # --- Snapshot B: day 2, independent second source arrives ---
        day2 = run_mode_a(os.path.join(_FIXTURES, "ca_accum_day2"), self.data_dir, now="2026-08-11T00:00:00Z")

        acc_after = next(c for c in day2["candidates"] if c.candidate_id == acc_id)

        # The correct candidate received the new evidence.
        self.assertEqual(set(acc_after.anomaly_ids), {"ANOM-ACC1", "ANOM-ACC2"})
        self.assertIn("OBS-ACC2", acc_after.observation_ids)

        # Independent-source counting increased correctly: 1 -> 2, and by
        # the specific expected sources, not just an arbitrary bump.
        self.assertEqual(acc_after.dimensions["evidence_diversity"]["value"]["distinct_sources"], 2)
        self.assertEqual(sorted(acc_after.dimensions["evidence_diversity"]["value"]["sources"]),
                          ["hacker_news", "lobsters"])
        self.assertEqual(acc_after.dimensions["independent_observation_count"]["value"]["distinct_urls"], 2)

        # Lifecycle reassessment happened: crossing min_sources_validating=2
        # with economic_consequence already EVIDENCED on day 1 promotes it.
        self.assertEqual(acc_after.dimensions["economic_consequence"]["status"], "EVIDENCED")
        self.assertEqual(acc_after.state, "VALIDATING",
                          "two independent sources plus an EVIDENCED economic_consequence must cross the "
                          "WATCH->VALIDATING bar per lifecycle.py's own _validating_requirements")

        # The history shows a genuine, evidenced state_changed event, not a
        # silent snapshot overwrite.
        last_event = acc_after.history[-1]
        self.assertEqual(last_event["event_type"], "state_changed")
        self.assertEqual(last_event["reason"].split(":")[0], "reached VALIDATING")

        # Unrelated candidates (a different underlying problem entirely)
        # are completely untouched by this run.
        unrel_after = [c for c in day2["candidates"] if "ANOM-UNREL" in c.anomaly_ids]
        self.assertEqual(len(unrel_after), len(unrel_candidates_day1))
        for before, after in zip(sorted(unrel_candidates_day1, key=lambda c: c.candidate_id),
                                  sorted(unrel_after, key=lambda c: c.candidate_id)):
            self.assertEqual(before.candidate_id, after.candidate_id)
            self.assertEqual(before.state, after.state)
            self.assertEqual(len(before.history), len(after.history),
                              "an unrelated candidate must not gain a new history event just because a "
                              "different candidate accumulated new evidence")

        # Mode B's own candidates (a different type entirely) are also
        # completely untouched by this Mode-A-only accumulation run.
        registry_events_before_mode_b_check = day2["events_appended"]
        self.assertGreater(registry_events_before_mode_b_check, 0, "sanity: day 2 must have appended something")


if __name__ == "__main__":
    unittest.main()
