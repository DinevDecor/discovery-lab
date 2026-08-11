"""Regression tests for the non-idempotent-regrouping defect: a candidate
that has accumulated many anomaly_ids over past merges can fragment, on a
fresh run, into several disjoint groups under _build_groups's anchor-based
comparison (see its own docstring for why that comparison is intentionally
non-transitive). Processing each fragment independently reassessed the
candidate from a PARTIAL evidence slice, repeatedly, sometimes with
contradictory conclusions in the same run, and was not a true fixed point:
re-running against unchanged evidence kept re-fragmenting and re-emitting
events for several runs before stabilizing (see chat writeup - this was
directly observed on the real corpus: BC-0005's 12 accumulated anomaly_ids
fragmented into 5 disjoint groups, producing 4 contradictory
evidence_reassessed events in one run).

tests/fixtures/ca_fragmentation/ is built so its 10 anomalies form exactly
2 disjoint fresh groups (verified directly against _build_groups): 5 share
one specific vocabulary (billing/quota/token/credit), the other 5 share a
different one (balance/meter/allocation) - same buyer_bucket and
function_class, but 0 shared keywords and 0.0 Jaccard on both fields
between the two anchors, so they never merge with each other under
signature.py's gate, exactly the anchor-fragmentation shape from the real
corpus.
"""

import _pathsetup  # noqa: F401
import os
import shutil
import tempfile
import unittest

from business_candidate_analyst.analyst import run_analysis
from business_candidate_analyst.models import CandidateEvent, NEW_MARKET
from business_candidate_analyst.registry import CandidateRegistry, make_event_id, rebuild_snapshot

_FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")
_ALL_ANOMALY_IDS = [f"ANOM-M{i:02d}" for i in range(1, 11)]
_ALL_OBSERVATION_IDS = [f"OBS-M{i:02d}" for i in range(1, 11)]


class IdempotentFragmentedReassessmentTests(unittest.TestCase):
    def setUp(self):
        self.data_dir = tempfile.mkdtemp()
        self._seed_preexisting_candidate()

    def tearDown(self):
        shutil.rmtree(self.data_dir, ignore_errors=True)

    def _seed_preexisting_candidate(self):
        """Seeds BC-0001 as already owning all 10 anomaly_ids - standing
        in for "accumulated via several past candidates_merged events",
        which is what actually happens on the real corpus over time; the
        end state (one candidate, many anomaly_ids, fresh grouping
        fragments them) is what matters for this test, not how many
        historical runs it took to get there."""
        events_path = os.path.join(self.data_dir, "candidate_events.jsonl")
        registry = CandidateRegistry(events_path)
        seed = CandidateEvent(
            event_id=make_event_id("candidate_created", "BC-0001", {"anomaly_ids": _ALL_ANOMALY_IDS}),
            event_type="candidate_created", candidate_id="BC-0001", recorded_at="2026-08-01T00:00:00Z",
            reason="seeded for test: candidate already owns all 10 anomaly_ids",
            derived_from=sorted(_ALL_ANOMALY_IDS + _ALL_OBSERVATION_IDS),
            payload={
                "state": "WATCH", "candidate_type": NEW_MARKET,
                "anomaly_ids": _ALL_ANOMALY_IDS, "observation_ids": _ALL_OBSERVATION_IDS,
                "signature": {"buyer_bucket": "api_consumer", "function_class": "resource_visibility"},
                "dimensions": {}, "merge_reasons": [],
            },
            analyst_version="0.1.0",
        )
        registry.append(seed)

    def test_fresh_grouping_fragments_into_at_least_two_subgroups(self):
        """Sanity check on the fixture itself, independent of analyst.py:
        confirms the precondition (>=2 disjoint fresh groups) actually
        holds before testing that analyst.py handles it correctly."""
        from business_candidate_analyst.analyst import _build_groups
        from business_candidate_analyst.config import load_thresholds
        from business_candidate_analyst.evidence_reader import load_ca_evidence

        th = load_thresholds()
        evidence = load_ca_evidence(os.path.join(_FIXTURES, "ca_fragmentation"))
        obs_by_id = evidence.observations_by_id()
        groups = _build_groups(evidence.anomalies, obs_by_id, th)
        self.assertGreaterEqual(len(groups), 2)
        covered = set()
        for g in groups:
            covered |= g["anomaly_ids"]
        self.assertEqual(covered, set(_ALL_ANOMALY_IDS))

    def test_candidate_reassessed_exactly_once_from_full_unioned_evidence(self):
        result = run_analysis(os.path.join(_FIXTURES, "ca_fragmentation"), self.data_dir,
                               now="2026-08-11T00:00:00Z")

        touched = [g for g in result["group_reports"] if g.get("candidate_id") == "BC-0001"]
        self.assertEqual(len(touched), 1,
                          f"BC-0001 must be reassessed exactly once per run, not once per fragment; "
                          f"got {len(touched)} group_reports: {touched}")

        candidate = next(c for c in result["candidates"] if c.candidate_id == "BC-0001")
        self.assertEqual(sorted(candidate.anomaly_ids), _ALL_ANOMALY_IDS)
        self.assertEqual(sorted(candidate.observation_ids), _ALL_OBSERVATION_IDS)

        # Full evidence set used: evidence_diversity must reflect all 10
        # observations, not whichever 5-observation fragment ran last.
        self.assertEqual(candidate.dimensions["evidence_diversity"]["value"]["distinct_sources"],
                          len({"hacker_news"}))
        self.assertEqual(candidate.dimensions["independent_observation_count"]["value"]["observation_count"], 10)

    def test_no_contradictory_events_in_one_run(self):
        events_path = os.path.join(self.data_dir, "candidate_events.jsonl")
        with open(events_path, encoding="utf-8") as f:
            before = len([l for l in f if l.strip()])

        run_analysis(os.path.join(_FIXTURES, "ca_fragmentation"), self.data_dir, now="2026-08-11T00:00:00Z")

        with open(events_path, encoding="utf-8") as f:
            all_lines = [l for l in f if l.strip()]
        new_lines = all_lines[before:]
        bc0001_events = [l for l in new_lines if '"candidate_id": "BC-0001"' in l]
        self.assertLessEqual(len(bc0001_events), 1,
                              "at most one event for BC-0001 this run - never multiple, and never "
                              "contradictory ones (e.g. 'meets the WATCH bar' and 'does not meet' in "
                              "the same run, as happened on the real corpus)")

    def test_second_and_third_identical_runs_append_zero_events(self):
        run_analysis(os.path.join(_FIXTURES, "ca_fragmentation"), self.data_dir, now="2026-08-11T00:00:00Z")

        events_path = os.path.join(self.data_dir, "candidate_events.jsonl")
        with open(events_path, encoding="utf-8") as f:
            after_run_1 = len([l for l in f if l.strip()])

        result_2 = run_analysis(os.path.join(_FIXTURES, "ca_fragmentation"), self.data_dir,
                                 now="2026-08-11T01:00:00Z")
        self.assertEqual(result_2["events_appended"], 0, "second identical run must append zero events")
        with open(events_path, encoding="utf-8") as f:
            after_run_2 = len([l for l in f if l.strip()])
        self.assertEqual(after_run_2, after_run_1)

        result_3 = run_analysis(os.path.join(_FIXTURES, "ca_fragmentation"), self.data_dir,
                                 now="2026-08-11T02:00:00Z")
        self.assertEqual(result_3["events_appended"], 0, "third identical run must also append zero events")


if __name__ == "__main__":
    unittest.main()
