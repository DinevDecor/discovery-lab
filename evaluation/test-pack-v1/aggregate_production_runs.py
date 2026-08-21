"""Deterministic aggregator over the six real production-judge runs
(PROD-R1..PROD-R6) already committed under evaluation/test-pack-v1/.

Read-only: never calls a model, never makes a network request, never
imports or re-runs same_mechanism_gate.py, and never writes to any
results-production-judge*.json file. Its only write is its own derived
artifact, production-judge-aggregate.json - re-running it against the
same six input files always produces byte-identical output, because it
does nothing but reduce data that already exists on disk.

A runtime/parser crash inside one attempt (result["error"] set,
actual_verdict/actual_edge both null) is classified "runtime_error" and
counted completely separately from a completed attempt that reached a
verdict and was simply wrong ("wrong"). The two are never summed into
one "failure" bucket anywhere in this module - conflating a gate crash
with a gate decision would misattribute a parser/contract problem as a
semantic one, or vice versa.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

HERE = os.path.dirname(os.path.abspath(__file__))

RUN_FILES = {
    "PROD-R1": "results-production-judge.json",
    "PROD-R2": "results-production-judge-PROD-R2.json",
    "PROD-R3": "results-production-judge-PROD-R3.json",
    "PROD-R4": "results-production-judge-PROD-R4.json",
    "PROD-R5": "results-production-judge-PROD-R5.json",
    "PROD-R6": "results-production-judge-PROD-R6.json",
}

OUTPUT_PATH = os.path.join(HERE, "production-judge-aggregate.json")


def load_runs(base_dir: str = HERE) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """Read-only load of the six real result files, keyed run_id ->
    test_case_id -> that case's raw result record for that run."""
    runs: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for run_id, filename in RUN_FILES.items():
        path = os.path.join(base_dir, filename)
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        runs[run_id] = {r["test_case_id"]: r for r in data["results"]}
    return runs


def classify(result: Dict[str, Any]) -> str:
    """'runtime_error' | 'correct' | 'wrong' - never a fourth bucket, and
    never both at once. A crash (error set) is never scored as pass/fail
    on the merits, because the gate never reached a verdict to score."""
    if result.get("error"):
        return "runtime_error"
    return "correct" if result.get("pass") else "wrong"


def per_case_summary(runs: Dict[str, Dict[str, Dict[str, Any]]]) -> List[Dict[str, Any]]:
    case_ids = sorted({cid for run in runs.values() for cid in run})
    out = []
    for cid in case_ids:
        correct = wrong = runtime_error = 0
        expected_verdict: Optional[str] = None
        expected_edge: Optional[str] = None
        edge_distribution: Dict[str, int] = {}
        per_run: Dict[str, Any] = {}
        for run_id in RUN_FILES:
            r = runs[run_id].get(cid)
            if r is None:
                continue
            expected_verdict = r["expected_verdict"]
            expected_edge = r["expected_edge"]
            cls = classify(r)
            per_run[run_id] = {
                "classification": cls,
                "actual_verdict": r.get("actual_verdict"),
                "actual_edge": r.get("actual_edge"),
                "error": r.get("error"),
            }
            if cls == "correct":
                correct += 1
            elif cls == "wrong":
                wrong += 1
            else:
                runtime_error += 1
            if cls != "runtime_error":
                edge = r["actual_edge"]
                edge_distribution[edge] = edge_distribution.get(edge, 0) + 1

        completed = correct + wrong
        distinct_completed_edges = len(edge_distribution)
        if completed == 0:
            behavior = "no_completed_runs"
        elif distinct_completed_edges <= 1:
            behavior = "stable_correct" if wrong == 0 else "stable_wrong"
        else:
            behavior = "sampling_sensitive"

        out.append({
            "test_case_id": cid,
            "expected_verdict": expected_verdict,
            "expected_edge": expected_edge,
            "runs_present": len(per_run),
            "completed_runs": completed,
            "correct": correct,
            "wrong": wrong,
            "runtime_error": runtime_error,
            "edge_distribution_completed_runs": edge_distribution,
            "behavior": behavior,
            "per_run": per_run,
        })
    return out


def per_run_summary(runs: Dict[str, Dict[str, Dict[str, Any]]]) -> Dict[str, Any]:
    out = {}
    for run_id in RUN_FILES:
        cases = runs[run_id]
        completed = {cid: r for cid, r in cases.items() if not r.get("error")}
        errored = {cid: r for cid, r in cases.items() if r.get("error")}
        correct = [cid for cid, r in completed.items() if r["pass"]]
        edge_distribution: Dict[str, int] = {}
        for r in completed.values():
            edge_distribution[r["actual_edge"]] = edge_distribution.get(r["actual_edge"], 0) + 1
        out[run_id] = {
            "cases_present": len(cases),
            "completed": len(completed),
            "runtime_errors": sorted(errored.keys()),
            "correct": len(correct),
            "edge_distribution": edge_distribution,
        }
    return out


def false_merge_analysis(runs: Dict[str, Dict[str, Dict[str, Any]]]) -> Dict[str, Any]:
    """The nuance the headline '0 false merges' number hides if stated
    unqualified: zero false merges among RELATED_DISTINCT ground truth,
    but real, repeated false merges of an UNRESOLVED ground-truth case
    (evidence-floor bypass, not a false-split-style error)."""
    of_related_distinct = []
    of_unresolved = []
    for run_id, cases in runs.items():
        for cid, r in cases.items():
            if r.get("error") or r["actual_edge"] != "merged":
                continue
            if r["expected_edge"] == "related_distinct":
                of_related_distinct.append({"run": run_id, "case": cid})
            elif r["expected_edge"] == "unresolved":
                of_unresolved.append({"run": run_id, "case": cid})
    return {
        "false_merge_of_related_distinct_ground_truth": of_related_distinct,
        "false_merge_of_unresolved_ground_truth": of_unresolved,
    }


def runtime_error_locations(runs: Dict[str, Dict[str, Dict[str, Any]]]) -> List[Dict[str, str]]:
    out = []
    for run_id in RUN_FILES:
        for cid, r in runs[run_id].items():
            if r.get("error"):
                out.append({"run": run_id, "case": cid, "error": r["error"]})
    return out


RUNTIME_ERROR_ROOT_CAUSE = (
    "same_mechanism_gate.py's profile_anomaly() calls "
    "float(raw.get('confidence', 0.0)) on the judge's raw profile response "
    "with no type validation and no try/except. PROFILE_PROMPT's own JSON "
    "contract lists 'confidence' as a bare key with no numeric-format "
    "instruction (unlike failure_class, which is given an explicit enum) - "
    "so a production judge answer of a category word ('high') instead of a "
    "0-1 float is not a contract the judge was ever unambiguously told to "
    "honor. Observed literal error text in every occurrence: "
    "\"could not convert string to float: 'high'\"."
)


def build_aggregate(base_dir: str = HERE) -> Dict[str, Any]:
    runs = load_runs(base_dir)
    per_case = per_case_summary(runs)
    total_correct = sum(c["correct"] for c in per_case)
    total_wrong = sum(c["wrong"] for c in per_case)
    total_runtime_error = sum(c["runtime_error"] for c in per_case)
    return {
        "run_ids": list(RUN_FILES.keys()),
        "total_attempts": total_correct + total_wrong + total_runtime_error,
        "total_correct": total_correct,
        "total_wrong_semantic": total_wrong,
        "total_runtime_errors": total_runtime_error,
        "per_run": per_run_summary(runs),
        "per_case": per_case,
        "false_merge_analysis": false_merge_analysis(runs),
        "runtime_error_locations": runtime_error_locations(runs),
        "runtime_error_root_cause": RUNTIME_ERROR_ROOT_CAUSE,
    }


def main() -> None:
    aggregate = build_aggregate()
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(aggregate, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(json.dumps({
        "total_attempts": aggregate["total_attempts"],
        "total_correct": aggregate["total_correct"],
        "total_wrong_semantic": aggregate["total_wrong_semantic"],
        "total_runtime_errors": aggregate["total_runtime_errors"],
        "output": OUTPUT_PATH,
    }, indent=2))


if __name__ == "__main__":
    main()
