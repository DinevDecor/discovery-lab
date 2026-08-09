"""
Constraint Archaeology Test Pack v1 — production-judge harness.

Runs the exact same 10 frozen pairs from ground-truth.json through the REAL
production judge (ca_agents.mechanism_judge.ClaudeMechanismJudge), calling the
actual Anthropic API, via the same unmodified gate functions used by
run_test_pack.py (profile_anomaly, same_mechanism — both imported directly
from same_mechanism_gate.py, never copied or edited).

This script is intended to run only inside the isolated,
manual-trigger-only GitHub Actions workflow
(.github/workflows/test-pack-v1-production-judge.yml), which supplies
ANTHROPIC_API_KEY from the existing repository secret. It does not touch
constraint-archaeology-agents/data/, does not call run_daily.py, and does not
modify same_mechanism_gate.py or any frozen document.

Ground truth (expected verdict/edge) is read from ground-truth.json unchanged
— not re-derived, not adjusted after seeing output.

Usage: python3 run_test_pack_production.py [RUN_ID]
  RUN_ID defaults to "PROD-R1" (the original single production run) and
  selects the output filename: results-production-judge.json for PROD-R1
  (unchanged, so the original file is never overwritten), or
  results-production-judge-<RUN_ID>.json for any other RUN_ID — used for the
  repeated-sampling variance experiment (PROD-R2..PROD-R6). Each run_id is a
  fresh, independent set of profile()/counterfactual() calls; no run reuses
  or overwrites another run's file.
"""
from __future__ import annotations

import json
import os
import sys
import traceback
from dataclasses import asdict
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.abspath(__file__))
GATE_SRC = os.path.join(ROOT, "..", "..", "constraint-archaeology-agents", "src")
sys.path.insert(0, GATE_SRC)

from ca_agents.same_mechanism_gate import (  # noqa: E402
    GateAnomaly, profile_anomaly, same_mechanism,
)
from ca_agents.mechanism_judge import ClaudeMechanismJudge  # noqa: E402
from ca_agents import llm as ca_llm  # noqa: E402


def build_gate_anomaly(raw: dict) -> GateAnomaly:
    return GateAnomaly(
        id=raw["id"], source=raw["source"], process=raw["process"], pain=raw["pain"],
        current_carrier=raw["current_carrier"], failure_mode=raw["failure_mode"],
        evidence_count=raw.get("evidence_count", 1), confidence=raw.get("confidence", 0.0),
    )


def profile_to_dict(profile) -> dict:
    d = asdict(profile)
    d["failure_class"] = profile.failure_class.value
    return d


def main():
    run_id = sys.argv[1] if len(sys.argv) > 1 else "PROD-R1"

    with open(os.path.join(ROOT, "ground-truth.json"), encoding="utf-8") as f:
        ground_truth = json.load(f)

    judge = ClaudeMechanismJudge()

    results = []
    errors = []

    for case in ground_truth["cases"]:
        tcid = case["test_case_id"]
        left = build_gate_anomaly(case["left"])
        right = build_gate_anomaly(case["right"])
        try:
            lp = profile_anomaly(left, judge)
            rp = profile_anomaly(right, judge)
            decision = same_mechanism(left, right, lp, rp, judge)
            d = decision.to_dict()

            expected_verdict = case["expected_verdict"]
            expected_edge = case["expected_edge"]
            passed = (d["verdict"] == expected_verdict) and (d["edge"] == expected_edge)

            results.append({
                "test_case_id": tcid,
                "category": case["category"],
                "cross_domain": case["cross_domain"],
                "domains": case["domains"],
                "left_observation": case["left"],
                "right_observation": case["right"],
                "expected_verdict": expected_verdict,
                "expected_edge": expected_edge,
                "actual_verdict": d["verdict"],
                "actual_edge": d["edge"],
                "pass": passed,
                "short_circuited": d["short_circuited"],
                "reasons": d["reasons"],
                "counterfactuals": d["counterfactuals"],
                "left_mechanism_profile": profile_to_dict(lp),
                "right_mechanism_profile": profile_to_dict(rp),
                "left_profile_confidence": lp.confidence,
                "right_profile_confidence": rp.confidence,
                "error": None,
            })
        except Exception as e:  # noqa: BLE001 - record and continue, do not abort the run
            tb = traceback.format_exc()
            errors.append({"test_case_id": tcid, "error": str(e), "traceback": tb})
            results.append({
                "test_case_id": tcid,
                "category": case["category"],
                "cross_domain": case["cross_domain"],
                "domains": case["domains"],
                "left_observation": case["left"],
                "right_observation": case["right"],
                "expected_verdict": case["expected_verdict"],
                "expected_edge": case["expected_edge"],
                "actual_verdict": None,
                "actual_edge": None,
                "pass": False,
                "error": str(e),
            })

    output = {
        "run_metadata": {
            "run_id": run_id,
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "gate_module": "constraint-archaeology-agents/src/ca_agents/same_mechanism_gate.py",
            "gate_unmodified": True,
            "judge": "ca_agents.mechanism_judge.ClaudeMechanismJudge (production, real Anthropic API)",
            "provider": "Anthropic",
            "anthropic_api_url": ca_llm.ANTHROPIC_URL,
            "anthropic_api_version_header": "2023-06-01",
            "model": ca_llm.DEFAULT_MODEL,
            "model_env_override_present": "ANTHROPIC_MODEL" in os.environ,
            "errors": errors,
        },
        "results": results,
    }

    filename = "results-production-judge.json" if run_id == "PROD-R1" else f"results-production-judge-{run_id}.json"
    out_path = os.path.join(ROOT, filename)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    total = len(results)
    passed = sum(1 for r in results if r["pass"])
    print(f"run_id: {run_id}")
    print(f"model: {ca_llm.DEFAULT_MODEL}")
    print(f"{passed}/{total} passed")
    for r in results:
        mark = "PASS" if r["pass"] else ("ERROR" if r.get("error") else "FAIL")
        exp = r["expected_edge"]
        act = r.get("actual_edge") or "N/A"
        print(f"  {mark:5s} {r['test_case_id']:8s} expected={exp:15s} actual={act}")
    if errors:
        print(f"\n{len(errors)} case(s) errored — see run_metadata.errors in {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
