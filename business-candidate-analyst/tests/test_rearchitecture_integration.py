"""End-to-end Mode B test: Mode A runs first (as it would in the real CLI),
then Mode B runs against the SAME registry, proving:

  - candidate_id allocation continues Mode A's sequence rather than
    colliding with it (BC-0001 from Mode A, BC-0002+ from Mode B);
  - Mode B's URL-based grouping merges two anomalies that Constraint
    Archaeology's own mechanism gate kept separate (ANOM-BANK1/ANOM-BANK2,
    mirroring the real corpus's solar-curtailment story split across
    ANOM-0067/ANOM-0101 - see README);
  - an unrelated anomaly with no structural pattern produces no candidate;
  - a Mode B candidate can be REJECTED by a later Constraint Archaeology
    KILL evaluation even after reaching a high state.
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

_FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


class RearchitectureIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.data_dir = tempfile.mkdtemp()
        self.cfg = load_rearchitecture_thresholds()

    def tearDown(self):
        shutil.rmtree(self.data_dir, ignore_errors=True)

    def _run_day(self, fixture, now):
        a = run_mode_a(os.path.join(_FIXTURES, fixture), self.data_dir, now=now)
        b = run_mode_b(os.path.join(_FIXTURES, fixture), self.data_dir, self.cfg, now=now)
        return a, b

    def test_candidate_ids_do_not_collide_between_modes(self):
        a1, b1 = self._run_day("ca_rearch_run1", "2026-08-08T00:00:00Z")
        mode_a_ids = {c.candidate_id for c in a1["candidates"]}
        mode_b_ids = {c.candidate_id for c in b1["candidates"]}
        self.assertEqual(mode_a_ids & mode_b_ids, set(), "Mode A and Mode B must never reuse a candidate_id")
        for c in a1["candidates"]:
            self.assertEqual(c.candidate_type, NEW_MARKET)
        for c in b1["candidates"]:
            self.assertEqual(c.candidate_type, OLD_BUSINESS_REARCHITECTURE)

    def test_url_split_anomalies_merge_into_one_candidate(self):
        _, b1 = self._run_day("ca_rearch_run1", "2026-08-08T00:00:00Z")
        by_anomaly = {frozenset(c.anomaly_ids): c for c in b1["candidates"]}
        bank = by_anomaly[frozenset({"ANOM-BANK1", "ANOM-BANK2"})]
        self.assertEqual(sorted(bank.observation_ids), ["OBS-BANK1", "OBS-BANK2"])
        self.assertIn(bank.state, ("WATCH", "VALIDATING"))

    def test_no_pattern_anomaly_produces_no_candidate(self):
        _, b1 = self._run_day("ca_rearch_run1", "2026-08-08T00:00:00Z")
        for c in b1["candidates"]:
            self.assertNotIn("ANOM-UNRELATED", c.anomaly_ids)

    def test_ca_kill_rejects_even_a_high_state_candidate(self):
        self._run_day("ca_rearch_run1", "2026-08-08T00:00:00Z")
        _, b2 = run_mode_a(os.path.join(_FIXTURES, "ca_rearch_run2"), self.data_dir, now="2026-08-09T00:00:00Z"), \
            run_mode_b(os.path.join(_FIXTURES, "ca_rearch_run2"), self.data_dir, self.cfg, now="2026-08-09T00:00:00Z")
        by_anomaly = {frozenset(c.anomaly_ids): c for c in b2["candidates"]}
        killed = by_anomaly[frozenset({"ANOM-KILL"})]
        self.assertEqual(killed.state, "REJECTED")
        self.assertIn("KILLed", killed.rejected_reason)

    def test_provenance_never_references_ids_outside_the_fixture(self):
        _, b1 = self._run_day("ca_rearch_run1", "2026-08-08T00:00:00Z")
        known = {"ANOM-BANK1", "ANOM-BANK2", "ANOM-UNRELATED", "ANOM-KILL",
                 "OBS-BANK1", "OBS-BANK2", "OBS-UNRELATED", "OBS-KILL1"}
        for c in b1["candidates"]:
            for h in c.history:
                for ref in h["derived_from"]:
                    self.assertIn(ref, known, f"fabricated provenance reference: {ref}")

    def test_rerunning_same_day_is_idempotent(self):
        self._run_day("ca_rearch_run1", "2026-08-08T00:00:00Z")
        from business_candidate_analyst.rearchitecture.analyst import run_analysis
        repeat = run_analysis(os.path.join(_FIXTURES, "ca_rearch_run1"), self.data_dir, self.cfg,
                               now="2026-08-08T00:00:01Z")
        self.assertEqual(repeat["events_appended"], 0)


if __name__ == "__main__":
    unittest.main()
