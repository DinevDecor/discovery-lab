"""
Constraint Archaeology Test Pack v1 — harness.

Runs the REAL, unmodified same-mechanism gate
(constraint-archaeology-agents/src/ca_agents/same_mechanism_gate.py) against the
10 pre-labeled pairs in ground-truth.json.

No network / no ANTHROPIC_API_KEY is available in this evaluation environment,
so the JudgeProtocol (profile/counterfactual) is served by CachedJudge below,
which replays verbatim responses collected from genuinely independent, blind
Claude subagent calls (judge_cache.json) — one isolated call per prompt, each
subagent seeing only the single prompt text the production gate would have
sent, with no visibility into the other case in the pair, the ground truth,
or any other subagent's answer. See README.md for the full rationale.

This script does not alter same_mechanism_gate.py, does not touch any frozen
document, and writes nothing to constraint-archaeology-agents/data/. Output
goes only to results.json in this directory.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.abspath(__file__))
GATE_SRC = os.path.join(ROOT, "..", "..", "constraint-archaeology-agents", "src")
sys.path.insert(0, GATE_SRC)

from ca_agents.same_mechanism_gate import (  # noqa: E402
    GateAnomaly, gate_pair, PROFILE_PROMPT, COUNTERFACTUAL_PROMPT,
)


class MissingCachedResponse(RuntimeError):
    pass


class CachedJudge:
    """JudgeProtocol implementation backed by pre-collected independent subagent
    responses. Raises loudly if the real gate asks a question this test pack
    did not anticipate and cache, rather than silently guessing an answer.
    """

    def __init__(self, profile_cache: dict, counterfactual_lookup: dict):
        self._profile_cache = profile_cache          # prompt text -> response dict
        self._cf_cache = counterfactual_lookup        # prompt text -> response dict
        self.profile_calls = []
        self.counterfactual_calls = []

    def profile(self, prompt: str):
        self.profile_calls.append(prompt)
        if prompt not in self._profile_cache:
            raise MissingCachedResponse(f"no cached profile for prompt:\n{prompt}")
        return self._profile_cache[prompt]

    def counterfactual(self, prompt: str):
        self.counterfactual_calls.append(prompt)
        if prompt not in self._cf_cache:
            raise MissingCachedResponse(f"no cached counterfactual for prompt:\n{prompt}")
        return self._cf_cache[prompt]


def build_gate_anomaly(raw: dict) -> GateAnomaly:
    return GateAnomaly(
        id=raw["id"], source=raw["source"], process=raw["process"], pain=raw["pain"],
        current_carrier=raw["current_carrier"], failure_mode=raw["failure_mode"],
        evidence_count=raw.get("evidence_count", 1), confidence=raw.get("confidence", 0.0),
    )


def load_cache():
    with open(os.path.join(ROOT, "judge_cache.json"), encoding="utf-8") as f:
        raw = json.load(f)
    return raw["profiles"], raw["counterfactuals"]


def build_profile_prompt_index(ground_truth, profiles_by_id):
    """Key: the EXACT PROFILE_PROMPT text the real gate would generate for this
    anomaly -> the cached response for that anomaly id. Built by importing and
    formatting the production PROFILE_PROMPT template, so a drift between this
    harness and the real gate's prompt format fails loudly (KeyError) instead
    of silently mismatching.
    """
    index = {}
    for case in ground_truth["cases"]:
        for side in ("left", "right"):
            raw = case[side]
            prompt = PROFILE_PROMPT.format(
                process=raw["process"], pain=raw["pain"],
                current_carrier=raw["current_carrier"], failure_mode=raw["failure_mode"],
            )
            index[prompt] = profiles_by_id[raw["id"]]
    return index


def build_counterfactual_prompt_index(ground_truth, profiles_by_id, cf_by_key):
    """Pre-compute the counterfactual prompt for every ordered (repair_from,
    applied_to) pair that could occur among same-failure-class pairs, keyed by
    the exact COUNTERFACTUAL_PROMPT text. Only pairs actually reaching the
    counterfactual stage need an entry present in judge_cache.json; gate_pair
    will raise MissingCachedResponse if it asks for anything else, which is
    itself a useful signal that a ground-truth prediction about short-circuit
    behaviour was wrong.
    """
    index = {}
    ids_by_case = {}
    for case in ground_truth["cases"]:
        l, r = case["left"], case["right"]
        ids_by_case[case["test_case_id"]] = (l, r)

    def add(repair_owner_raw, target_raw, cache_key):
        if cache_key not in cf_by_key:
            return
        repair = profiles_by_id[repair_owner_raw["id"]]["repair"]
        target_profile = profiles_by_id[target_raw["id"]]
        prompt = COUNTERFACTUAL_PROMPT.format(
            repair=repair, process=target_raw["process"], pain=target_raw["pain"],
            failure_mechanism=target_profile["failure_mechanism"],
        )
        index[prompt] = cf_by_key[cache_key]

    for tcid, (l, r) in ids_by_case.items():
        add(l, r, f"{tcid}_L_repair_applied_to_R")
        add(r, l, f"{tcid}_R_repair_applied_to_L")
    return index


def main():
    with open(os.path.join(ROOT, "ground-truth.json"), encoding="utf-8") as f:
        ground_truth = json.load(f)
    profiles_by_id, cf_by_key = load_cache()

    profile_index = build_profile_prompt_index(ground_truth, profiles_by_id)
    cf_index = build_counterfactual_prompt_index(ground_truth, profiles_by_id, cf_by_key)
    judge = CachedJudge(profile_index, cf_index)

    results = []
    for case in ground_truth["cases"]:
        left = build_gate_anomaly(case["left"])
        right = build_gate_anomaly(case["right"])
        decision = gate_pair(left, right, judge)
        d = decision.to_dict()

        expected_verdict = case["expected_verdict"]
        expected_edge = case["expected_edge"]
        passed = (d["verdict"] == expected_verdict) and (d["edge"] == expected_edge)

        results.append({
            "test_case_id": case["test_case_id"],
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
            "left_mechanism_profile": profiles_by_id[case["left"]["id"]],
            "right_mechanism_profile": profiles_by_id[case["right"]["id"]],
            "left_profile_confidence": profiles_by_id[case["left"]["id"]].get("confidence"),
            "right_profile_confidence": profiles_by_id[case["right"]["id"]].get("confidence"),
        })

    output = {
        "run_metadata": {
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "gate_module": "constraint-archaeology-agents/src/ca_agents/same_mechanism_gate.py",
            "gate_unmodified": True,
            "judge": "CachedJudge replaying independent isolated Claude subagent responses (see README.md); JudgeProtocol contract unmodified",
            "total_profile_calls_replayed": len(judge.profile_calls),
            "total_counterfactual_calls_replayed": len(judge.counterfactual_calls),
        },
        "results": results,
    }

    out_path = os.path.join(ROOT, "results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    total = len(results)
    passed = sum(1 for r in results if r["pass"])
    print(f"{passed}/{total} passed")
    for r in results:
        mark = "PASS" if r["pass"] else "FAIL"
        print(f"  {mark}  {r['test_case_id']:8s} expected={r['expected_edge']:15s} actual={r['actual_edge']:15s}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
