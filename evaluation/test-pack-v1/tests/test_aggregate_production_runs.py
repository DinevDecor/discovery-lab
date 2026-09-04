import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from aggregate_production_runs import (  # noqa: E402
    RUN_FILES,
    build_aggregate,
    classify,
    false_merge_analysis,
    load_runs,
    per_case_summary,
    per_run_summary,
    runtime_error_locations,
)

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")


class ClassifyTests(unittest.TestCase):
    def test_error_is_runtime_error_regardless_of_pass_field(self):
        self.assertEqual(classify({"error": "boom", "pass": False}), "runtime_error")
        self.assertEqual(classify({"error": "boom", "pass": True}), "runtime_error")

    def test_no_error_and_pass_is_correct(self):
        self.assertEqual(classify({"error": None, "pass": True}), "correct")

    def test_no_error_and_not_pass_is_wrong(self):
        self.assertEqual(classify({"error": None, "pass": False}), "wrong")


class DeterminismTests(unittest.TestCase):
    def test_build_aggregate_is_byte_identical_across_calls(self):
        a = json.dumps(build_aggregate(BASE_DIR), sort_keys=True)
        b = json.dumps(build_aggregate(BASE_DIR), sort_keys=True)
        self.assertEqual(a, b)

    def test_loading_never_writes_to_a_results_file(self):
        paths = [os.path.join(BASE_DIR, fn) for fn in RUN_FILES.values()]
        before = {p: os.path.getmtime(p) for p in paths}
        build_aggregate(BASE_DIR)
        after = {p: os.path.getmtime(p) for p in paths}
        self.assertEqual(before, after)


class SixRunCoverageTests(unittest.TestCase):
    """Every one of the six real production runs must be included -
    silently dropping a run would understate the sample size."""

    def test_all_six_run_files_are_read(self):
        runs = load_runs(BASE_DIR)
        self.assertEqual(set(runs.keys()), set(RUN_FILES.keys()))
        self.assertEqual(len(runs), 6)

    def test_every_run_has_ten_cases(self):
        runs = load_runs(BASE_DIR)
        for run_id, cases in runs.items():
            self.assertEqual(len(cases), 10, f"{run_id} does not have all 10 test cases")


class PreStatedObservationTests(unittest.TestCase):
    """Recomputes, from the real committed JSON files (not from any
    narrative claim), the five specific per-case counts the task
    description asserted before this aggregator existed. Locks them in
    as regression tests against the real data, not against a claim."""

    @classmethod
    def setUpClass(cls):
        cls.by_case = {c["test_case_id"]: c for c in per_case_summary(load_runs(BASE_DIR))}

    def test_tp01_correct_merged_in_3_of_6(self):
        self.assertEqual(self.by_case["TP-01"]["correct"], 3)
        self.assertEqual(self.by_case["TP-01"]["runs_present"], 6)

    def test_tp02_correct_merged_in_1_of_6(self):
        self.assertEqual(self.by_case["TP-02"]["correct"], 1)
        self.assertEqual(self.by_case["TP-02"]["runs_present"], 6)

    def test_tp03_correct_in_all_4_completed_runs_with_2_runtime_errors(self):
        c = self.by_case["TP-03"]
        self.assertEqual(c["completed_runs"], 4)
        self.assertEqual(c["correct"], 4)
        self.assertEqual(c["wrong"], 0)
        self.assertEqual(c["runtime_error"], 2)

    def test_tp08_zero_correct_unresolved_in_6(self):
        c = self.by_case["TP-08"]
        self.assertEqual(c["correct"], 0)
        self.assertEqual(c["completed_runs"], 6)

    def test_tp09_zero_correct_unresolved_in_5_completed_with_1_runtime_error(self):
        c = self.by_case["TP-09"]
        self.assertEqual(c["correct"], 0)
        self.assertEqual(c["completed_runs"], 5)
        self.assertEqual(c["runtime_error"], 1)


class RuntimeErrorLocationTests(unittest.TestCase):
    def test_exact_three_runtime_error_locations(self):
        locations = {(loc["run"], loc["case"]) for loc in runtime_error_locations(load_runs(BASE_DIR))}
        self.assertEqual(locations, {("PROD-R3", "TP-09"), ("PROD-R5", "TP-03"), ("PROD-R6", "TP-03")})

    def test_all_three_are_the_same_underlying_error(self):
        for loc in runtime_error_locations(load_runs(BASE_DIR)):
            self.assertEqual(loc["error"], "could not convert string to float: 'high'")


class FalseMergeNuanceTests(unittest.TestCase):
    """Task instruction: never state '0 false merges' unqualified.
    Zero false merges of a RELATED_DISTINCT ground-truth case, but real,
    repeated false merges of the UNRESOLVED case TP-09."""

    def test_zero_false_merges_of_related_distinct_ground_truth(self):
        analysis = false_merge_analysis(load_runs(BASE_DIR))
        self.assertEqual(analysis["false_merge_of_related_distinct_ground_truth"], [])

    def test_tp09_was_falsely_merged_three_times(self):
        analysis = false_merge_analysis(load_runs(BASE_DIR))
        of_unresolved = analysis["false_merge_of_unresolved_ground_truth"]
        self.assertEqual(len(of_unresolved), 3)
        self.assertTrue(all(entry["case"] == "TP-09" for entry in of_unresolved))
        self.assertEqual({entry["run"] for entry in of_unresolved}, {"PROD-R4", "PROD-R5", "PROD-R6"})


class BehaviorClassificationTests(unittest.TestCase):
    """Stable-vs-sampling-sensitive is derived only from whether a
    case's own completed-run edges disagree with each other - never
    from whether the case is correct."""

    @classmethod
    def setUpClass(cls):
        cls.by_case = {c["test_case_id"]: c for c in per_case_summary(load_runs(BASE_DIR))}

    def test_tp01_and_tp02_are_sampling_sensitive(self):
        self.assertEqual(self.by_case["TP-01"]["behavior"], "sampling_sensitive")
        self.assertEqual(self.by_case["TP-02"]["behavior"], "sampling_sensitive")

    def test_tp08_is_stable_but_wrong(self):
        self.assertEqual(self.by_case["TP-08"]["behavior"], "stable_wrong")

    def test_easy_related_distinct_cases_are_stable_correct(self):
        for cid in ("TP-04", "TP-05", "TP-06", "TP-07", "TP-10"):
            self.assertEqual(self.by_case[cid]["behavior"], "stable_correct")


class OverallTotalsTests(unittest.TestCase):
    def test_sixty_total_attempts_partition_into_correct_wrong_error(self):
        aggregate = build_aggregate(BASE_DIR)
        self.assertEqual(aggregate["total_attempts"], 60)
        self.assertEqual(
            aggregate["total_correct"] + aggregate["total_wrong_semantic"] + aggregate["total_runtime_errors"],
            60,
        )
        self.assertEqual(aggregate["total_correct"], 38)
        self.assertEqual(aggregate["total_wrong_semantic"], 19)
        self.assertEqual(aggregate["total_runtime_errors"], 3)

    def test_per_run_correct_counts(self):
        summary = per_run_summary(load_runs(BASE_DIR))
        expected = {
            "PROD-R1": 6, "PROD-R2": 6, "PROD-R3": 7,
            "PROD-R4": 7, "PROD-R5": 7, "PROD-R6": 5,
        }
        for run_id, expected_correct in expected.items():
            self.assertEqual(summary[run_id]["correct"], expected_correct, run_id)


if __name__ == "__main__":
    unittest.main()
