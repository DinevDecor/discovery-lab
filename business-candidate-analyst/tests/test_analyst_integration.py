"""End-to-end test over two synthetic days of Constraint Archaeology
evidence (tests/fixtures/ca_run1, ca_run2 - entirely fabricated, not real
corpus data). Exercises the full path: evidence_reader -> signature
grouping -> dimensions -> lifecycle -> registry, across two runs, so the
registry's persistence/idempotency and the lifecycle ladder's rise/fall
are both checked against a realistic multi-day scenario:

  ANOM-Q1 (hacker_news) + ANOM-Q2 (discourse:openai-devs), different CA
  anomalies/mechanisms, merge into one candidate on the shared
  "resource_visibility" business signature (buyer=api_consumer) - this is
  the cross-anomaly business-opportunity recognition the task requires.
  Day 2 adds ANOM-Q3 (lobsters) to the same signature, pushing the
  candidate from VALIDATING to INVESTIGATE (three independent sources).

  ANOM-HOME and ANOM-K1 share a buyer bucket (operator) but a different
  function class, and correctly never merge with anything.

  ANOM-K1 gets a Constraint Archaeology KILL evaluation on day 2 and its
  candidate is REJECTED - the only implemented rejection trigger.
"""

import _pathsetup  # noqa: F401
import os
import shutil
import tempfile
import unittest

from business_candidate_analyst.analyst import run_analysis

_FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


class AnalystIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.data_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.data_dir, ignore_errors=True)

    def _run(self, fixture_name, now):
        return run_analysis(os.path.join(_FIXTURES, fixture_name), self.data_dir, now=now)

    def test_day_one_creates_three_candidates_with_correct_states(self):
        r1 = self._run("ca_run1", "2026-08-08T00:00:00Z")
        by_anomaly = {frozenset(c.anomaly_ids): c for c in r1["candidates"]}
        self.assertEqual(len(r1["candidates"]), 3)

        quota = by_anomaly[frozenset({"ANOM-Q1", "ANOM-Q2"})]
        self.assertEqual(quota.state, "VALIDATING")
        self.assertEqual(sorted(quota.observation_ids), ["OBS-Q1", "OBS-Q2", "OBS-Q2b"])

        home = by_anomaly[frozenset({"ANOM-HOME"})]
        self.assertEqual(home.state, "WATCH")

        dispatch = by_anomaly[frozenset({"ANOM-K1"})]
        self.assertEqual(dispatch.state, "WATCH")

    def test_never_merges_across_different_function_classes_despite_shared_buyer_bucket(self):
        r1 = self._run("ca_run1", "2026-08-08T00:00:00Z")
        # HOME (workaround_labor) and K1 (capacity_timing) both bucket as "operator"
        # buyers but must stay separate candidates - similar market, different job.
        anomaly_sets = [frozenset(c.anomaly_ids) for c in r1["candidates"]]
        self.assertIn(frozenset({"ANOM-HOME"}), anomaly_sets)
        self.assertIn(frozenset({"ANOM-K1"}), anomaly_sets)

    def test_day_two_advances_quota_candidate_to_investigate_via_third_independent_source(self):
        self._run("ca_run1", "2026-08-08T00:00:00Z")
        r2 = self._run("ca_run2", "2026-08-09T00:00:00Z")
        by_anomaly = {frozenset(c.anomaly_ids): c for c in r2["candidates"]}
        quota = by_anomaly[frozenset({"ANOM-Q1", "ANOM-Q2", "ANOM-Q3"})]
        self.assertEqual(quota.state, "INVESTIGATE")
        self.assertEqual(quota.dimensions["evidence_diversity"]["value"]["distinct_sources"], 3)

        strengthened = [g for g in r2["group_reports"]
                        if g["kind"] == "state_changed" and g.get("candidate_id") == quota.candidate_id]
        self.assertEqual(len(strengthened), 1)
        self.assertEqual(strengthened[0]["from_state"], "VALIDATING")
        self.assertEqual(strengthened[0]["state"], "INVESTIGATE")

    def test_day_two_rejects_the_killed_anomaly_candidate(self):
        self._run("ca_run1", "2026-08-08T00:00:00Z")
        r2 = self._run("ca_run2", "2026-08-09T00:00:00Z")
        by_anomaly = {frozenset(c.anomaly_ids): c for c in r2["candidates"]}
        dispatch = by_anomaly[frozenset({"ANOM-K1"})]
        self.assertEqual(dispatch.state, "REJECTED")
        self.assertIn("KILLed", dispatch.rejected_reason)
        # Provenance must point at the real CA evaluation input, not be fabricated.
        rejection_event = [h for h in dispatch.history if h["event_type"] == "state_changed"][0]
        self.assertIn("ANOM-K1", rejection_event["derived_from"])

    def test_untouched_candidate_produces_no_new_event_on_day_two(self):
        self._run("ca_run1", "2026-08-08T00:00:00Z")
        r2 = self._run("ca_run2", "2026-08-09T00:00:00Z")
        home_events = [g for g in r2["group_reports"] if g.get("anomaly_ids") == ["ANOM-HOME"]]
        self.assertEqual(len(home_events), 1)
        self.assertEqual(home_events[0]["kind"], "unchanged")

    def test_provenance_never_references_ids_outside_the_fixture(self):
        r1 = self._run("ca_run1", "2026-08-08T00:00:00Z")
        known_anomaly_ids = {"ANOM-Q1", "ANOM-Q2", "ANOM-HOME", "ANOM-K1"}
        known_observation_ids = {"OBS-Q1", "OBS-Q2", "OBS-Q2b", "OBS-H1", "OBS-K1"}
        events = __import__("business_candidate_analyst.registry", fromlist=["CandidateRegistry"]) \
            .CandidateRegistry(r1["events_path"]).all_events()
        for e in events:
            for ref in e["derived_from"]:
                self.assertIn(ref, known_anomaly_ids | known_observation_ids,
                               f"fabricated provenance reference: {ref}")

    def test_rerunning_same_day_is_fully_idempotent(self):
        self._run("ca_run1", "2026-08-08T00:00:00Z")
        r_repeat = self._run("ca_run1", "2026-08-08T00:00:01Z")
        self.assertEqual(r_repeat["events_appended"], 0)


if __name__ == "__main__":
    unittest.main()
