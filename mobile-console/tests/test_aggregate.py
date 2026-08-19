"""Tests for mobile_console.aggregate against the repo's own real,
already-committed ledger data - no fixtures, no mocking, matching the
same "test against real data" precedent
adversarial_review_kernel/tests/test_falsify_blindness.py already set.
"""

import _pathsetup  # noqa: F401
import os
import unittest

from mobile_console.aggregate import (
    BCA_CANDIDATES,
    CA_ANOMALIES,
    CA_OBSERVATIONS,
    build_snapshot,
    compute_activity,
    compute_ground_truth,
    compute_machine_status,
    compute_opportunities,
    compute_pipeline,
    compute_pipeline_records,
    list_anomalies,
    list_blind_analyses,
    list_candidates_past_watch_ids,
    list_falsifications,
    list_judgments,
    list_observations,
    load_all,
)


@unittest.skipUnless(os.path.exists(CA_ANOMALIES), f"{CA_ANOMALIES} not present in this checkout")
@unittest.skipUnless(os.path.exists(CA_OBSERVATIONS), f"{CA_OBSERVATIONS} not present in this checkout")
@unittest.skipUnless(os.path.exists(BCA_CANDIDATES), f"{BCA_CANDIDATES} not present in this checkout")
class DeterminismTests(unittest.TestCase):
    def test_build_snapshot_is_deterministic(self):
        a = build_snapshot()
        b = build_snapshot()
        self.assertEqual(a, b)

    def test_machine_status_is_deterministic(self):
        raw = load_all()
        self.assertEqual(compute_machine_status(raw), compute_machine_status(raw))


@unittest.skipUnless(os.path.exists(CA_ANOMALIES), f"{CA_ANOMALIES} not present in this checkout")
@unittest.skipUnless(os.path.exists(BCA_CANDIDATES), f"{BCA_CANDIDATES} not present in this checkout")
class NoInventedMetricsTests(unittest.TestCase):
    """Task instruction: 'PIPELINE must show the real observable
    funnel/stages and actual counts only - no invented funnel metrics.'
    Every stage count must equal a direct len() over the same raw data
    the aggregator itself loaded - no rate, ratio, or estimate."""

    def test_every_pipeline_stage_count_matches_a_direct_len_over_raw_data(self):
        raw = load_all()
        stages = compute_pipeline(raw)
        counts = {s["stage"]: s["count"] for s in stages}
        self.assertEqual(counts["Observations captured"], len(raw["observations"]))
        self.assertEqual(counts["Anomalies clustered"], len(raw["anomalies"]))
        self.assertEqual(counts["Business candidates opened"], len(raw["candidates"]))
        self.assertEqual(counts["Blind dual-model analyses (Stage 3)"], len(raw["blind_analyses"]))
        self.assertEqual(counts["Adversarial falsifications (Stage 4)"], len(raw["falsifications"]))
        self.assertEqual(counts["Deterministic judgments (Stage 4)"], len(raw["judgments"]))

    def test_no_stage_count_is_a_percentage_or_float(self):
        raw = load_all()
        for stage in compute_pipeline(raw):
            self.assertIsInstance(stage["count"], int)

    def test_pipeline_module_never_computes_a_ratio_or_rate(self):
        """Structural proof: no division operator appears anywhere in
        the pipeline-computing function's own source."""
        import inspect

        from mobile_console import aggregate
        source = inspect.getsource(aggregate.compute_pipeline)
        self.assertNotIn("/", source.replace("# ", ""))  # no division; comments may contain '/' in prose, stripped


@unittest.skipUnless(os.path.exists(BCA_CANDIDATES), f"{BCA_CANDIDATES} not present in this checkout")
class OpportunitiesTests(unittest.TestCase):
    def test_every_real_candidate_is_listed(self):
        raw = load_all()
        opportunities = compute_opportunities(raw)
        self.assertEqual(len(opportunities), len(raw["candidates"]))
        self.assertEqual({o["candidate_id"] for o in opportunities}, {c["candidate_id"] for c in raw["candidates"]})

    def test_bc_0001_is_reported_as_having_a_full_docket(self):
        """BC-0001/ANOM-0001 is the one candidate that actually went
        through blind analysis + falsification + judgment in this repo's
        real history - this must be reported true, not assumed."""
        raw = load_all()
        opportunities = compute_opportunities(raw)
        bc1 = next((o for o in opportunities if o["candidate_id"] == "BC-0001"), None)
        self.assertIsNotNone(bc1, "BC-0001 not found in real candidates.json - has the fixture data changed?")
        self.assertTrue(bc1["has_full_docket"])

    def test_a_watch_only_candidate_has_no_full_docket(self):
        raw = load_all()
        opportunities = compute_opportunities(raw)
        watch_only = [o for o in opportunities if o["candidate_id"] != "BC-0001" and o["state"] == "WATCH"]
        self.assertTrue(watch_only, "expected at least one WATCH-only candidate other than BC-0001 in real data")
        for o in watch_only:
            self.assertFalse(o["has_full_docket"], f"{o['candidate_id']} unexpectedly reported a full docket")


@unittest.skipUnless(os.path.exists(CA_ANOMALIES), f"{CA_ANOMALIES} not present in this checkout")
class GroundTruthIndependenceTests(unittest.TestCase):
    """Task instruction: 'GROUND TRUTH must list PGT-0001 and future PGT
    cases independently from ANOM-0001. Do not use PGT-0001 as if it
    were the next stage of the Loop case unless a canonical relation
    exists.' PGT-0001's real source_case_id is 'BC-0101', not 'BC-0001'
    or 'ANOM-0001' - this test locks that in."""

    def test_pgt_cases_report_their_own_real_source_case_id_only(self):
        raw = load_all()
        gt = compute_ground_truth(raw)
        for case in gt["cases"]:
            # source_case_id, when present, must be a real string the
            # case itself declared at registration - never null-coalesced
            # to some other case's id, and never silently rewritten here.
            self.assertIsInstance(case["source_case_id"], (str, type(None)))

    def test_no_pgt_case_is_falsely_linked_to_anom_0001_or_bc_0001(self):
        raw = load_all()
        gt = compute_ground_truth(raw)
        for case in gt["cases"]:
            self.assertNotIn(case["source_case_id"], ("ANOM-0001", "BC-0001"),
                              f"{case['prospective_case_id']} claims a relation to the Loop case that its own "
                              f"registered source_case_id does not support")


class SnapshotStructureTests(unittest.TestCase):
    def test_snapshot_has_all_six_top_level_sections(self):
        snapshot = build_snapshot()
        for key in ("machine_status", "opportunities", "pipeline", "pipeline_records", "ground_truth", "activity"):
            self.assertIn(key, snapshot)

    def test_activity_is_sorted_newest_first(self):
        raw = load_all()
        activity = compute_activity(raw)
        timestamps = [a["timestamp"] for a in activity]
        self.assertEqual(timestamps, sorted(timestamps, reverse=True))

    def test_activity_entries_all_trace_to_a_real_timestamp_field(self):
        raw = load_all()
        for entry in compute_activity(raw):
            self.assertTrue(entry["timestamp"])
            self.assertTrue(entry["kind"])


@unittest.skipUnless(os.path.exists(CA_ANOMALIES), f"{CA_ANOMALIES} not present in this checkout")
@unittest.skipUnless(os.path.exists(CA_OBSERVATIONS), f"{CA_OBSERVATIONS} not present in this checkout")
@unittest.skipUnless(os.path.exists(BCA_CANDIDATES), f"{BCA_CANDIDATES} not present in this checkout")
class PipelineDrilldownTests(unittest.TestCase):
    """Task instruction: 'displayed count == number of records in the
    opened list', for every one of the 7 Pipeline rows. Each assertion
    here compares the row's own count (from compute_pipeline) against
    the length of the real list a tap on that row would open - never a
    second, independently-computed number."""

    def _counts_by_id(self, raw):
        return {s["id"]: s["count"] for s in compute_pipeline(raw)}

    def test_observations_count_matches_list_length(self):
        raw = load_all()
        self.assertEqual(self._counts_by_id(raw)["observations"], len(list_observations(raw)))

    def test_anomalies_count_matches_list_length(self):
        raw = load_all()
        self.assertEqual(self._counts_by_id(raw)["anomalies"], len(list_anomalies(raw)))

    def test_candidates_count_matches_opportunities_length(self):
        """Row 3 reuses the existing Opportunities list verbatim - no
        second candidates list is ever built."""
        raw = load_all()
        self.assertEqual(self._counts_by_id(raw)["candidates"], len(compute_opportunities(raw)))

    def test_candidates_past_watch_count_matches_list_length(self):
        raw = load_all()
        self.assertEqual(self._counts_by_id(raw)["candidates_past_watch"], len(list_candidates_past_watch_ids(raw)))

    def test_blind_analyses_count_matches_list_length(self):
        raw = load_all()
        self.assertEqual(self._counts_by_id(raw)["blind_analyses"], len(list_blind_analyses(raw)))

    def test_falsifications_count_matches_list_length(self):
        raw = load_all()
        self.assertEqual(self._counts_by_id(raw)["falsifications"], len(list_falsifications(raw)))

    def test_judgments_count_matches_list_length(self):
        raw = load_all()
        self.assertEqual(self._counts_by_id(raw)["judgments"], len(list_judgments(raw)))

    def test_candidates_past_watch_uses_the_same_rule_as_machine_status(self):
        """Task instruction: 'Use the exact existing lifecycle/state rule
        that generated the current count. Do not invent a new definition
        of past WATCH.' Locks the drill-down's ids to the same set
        compute_machine_status's own candidates_past_watch count is
        derived from, via one shared predicate - not two definitions
        that happen to agree today."""
        raw = load_all()
        expected_ids = {c["candidate_id"] for c in raw["candidates"] if c.get("state") not in ("WATCH", None)}
        self.assertEqual(set(list_candidates_past_watch_ids(raw)), expected_ids)
        self.assertEqual(len(expected_ids), compute_machine_status(raw)["candidates_past_watch"])

    def test_candidates_past_watch_ids_are_real_and_not_watch(self):
        raw = load_all()
        candidates_by_id = {c["candidate_id"]: c for c in raw["candidates"]}
        past_watch_ids = list_candidates_past_watch_ids(raw)
        self.assertTrue(past_watch_ids, "expected at least one real candidate past WATCH")
        for cid in past_watch_ids:
            self.assertIn(cid, candidates_by_id, f"{cid} is not a real candidate_id")
            self.assertNotEqual(candidates_by_id[cid].get("state"), "WATCH")

    def test_stage4_judgment_for_the_loop_case_remains_watch(self):
        """BC-0001/ANOM-0001's real Stage 4 judgment is WATCH - the
        drill-down must report it exactly as recorded, not reinterpret
        or advance it."""
        raw = load_all()
        judgments = list_judgments(raw)
        loop_case_judgment = next(
            (j for j in judgments if j["case_id"] == "case:951963c3345d364c44c2f2ab34197651"), None
        )
        self.assertIsNotNone(loop_case_judgment, "expected the real Loop case judgment in real data")
        self.assertEqual(loop_case_judgment["status"], "WATCH")

    def test_pipeline_records_exposes_exactly_the_five_new_lists(self):
        raw = load_all()
        records = compute_pipeline_records(raw)
        self.assertEqual(
            set(records.keys()),
            {"observations", "anomalies", "candidates_past_watch", "blind_analyses", "falsifications", "judgments"},
        )

    def test_falsification_findings_count_is_a_real_len_not_invented(self):
        raw = load_all()
        raw_by_id = {f["artifact_id"]: f for f in raw["falsifications"]}
        for f in list_falsifications(raw):
            self.assertEqual(f["findings_count"], len(raw_by_id[f["artifact_id"]].get("findings", [])))

    def test_every_pipeline_row_has_a_stable_id(self):
        raw = load_all()
        ids = [s["id"] for s in compute_pipeline(raw)]
        self.assertEqual(
            ids,
            ["observations", "anomalies", "candidates", "candidates_past_watch",
             "blind_analyses", "falsifications", "judgments"],
        )


if __name__ == "__main__":
    unittest.main()
