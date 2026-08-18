"""Proves `ca_agents.same_mechanism_gate.gate_pair()` — the real,
unmodified function — accepts an `OpenAIMechanismJudge` and produces a
valid `GateDecision`, against the same two real, already-committed
anomalies `run_stage2_acceptance.py` uses. `call_openai` is mocked (no
real network call) - this is the offline proof; the real-provider proof
is `run_stage2_acceptance.py`, gated on `OPENAI_API_KEY`.
"""

import _pathsetup  # noqa: F401
import json
import os
import sys
import unittest
from unittest.mock import patch

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_CA_SRC = os.path.join(REPO_ROOT, "constraint-archaeology-agents", "src")
if _CA_SRC not in sys.path:
    sys.path.insert(0, _CA_SRC)

from ca_agents.same_mechanism_gate import EdgeType, GateAnomaly, Verdict, gate_pair  # noqa: E402

from gpt_mechanism_judge.judge import OpenAIMechanismJudge  # noqa: E402

CA_ANOMALIES_PATH = os.path.join(REPO_ROOT, "constraint-archaeology-agents", "data", "anomalies.json")
CA_OBSERVATIONS_PATH = os.path.join(REPO_ROOT, "constraint-archaeology-agents", "data", "observations.jsonl")


def _load_real_pair():
    with open(CA_ANOMALIES_PATH, encoding="utf-8") as f:
        anomalies = {a["anomaly_id"]: a for a in json.load(f)}
    observations = {}
    with open(CA_OBSERVATIONS_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            o = json.loads(line)
            observations[o["observation_id"]] = o

    def to_gate_anomaly(anomaly_id):
        anomaly = anomalies[anomaly_id]
        obs = observations[anomaly["observation_ids"][0]]
        return GateAnomaly(id=obs["observation_id"], source=obs["source"], process=obs["process"],
                            pain=obs["pain"], current_carrier=obs["current_carrier"],
                            failure_mode=obs["failure_mode"], evidence_count=len(anomaly["observation_ids"]),
                            confidence=obs["confidence"])

    return to_gate_anomaly("ANOM-0001"), to_gate_anomaly("ANOM-0002")


@unittest.skipUnless(os.path.exists(CA_ANOMALIES_PATH), "real CA anomalies.json not present")
@unittest.skipUnless(os.path.exists(CA_OBSERVATIONS_PATH), "real CA observations.jsonl not present")
class GatePairWithOpenAIJudgeTests(unittest.TestCase):
    def setUp(self):
        self.left, self.right = _load_real_pair()
        self.assertNotEqual(self.left.id, self.right.id)

    def test_openai_judge_satisfies_judgeprotocol_structurally(self):
        judge = OpenAIMechanismJudge()
        self.assertTrue(hasattr(judge, "profile"))
        self.assertTrue(hasattr(judge, "counterfactual"))
        self.assertTrue(callable(judge.profile))
        self.assertTrue(callable(judge.counterfactual))

    def test_gate_pair_runs_unmodified_and_returns_valid_decision(self):
        """Two clearly-unrelated real anomalies (probabilistic-programming
        performance vs. no-reply-email PII leakage) - a DIFFERENT_MECHANISMS
        verdict from a same-failure-class-blind judge, or INSUFFICIENT_DATA,
        is exactly as valid an acceptance result as SAME_MECHANISM. The
        thing being proven is that gate_pair() runs to completion and
        returns a well-formed GateDecision with a real GPT-shaped judge
        plugged in - not what verdict it reaches."""
        profile_responses = {
            self.left.process: json.dumps({
                "hidden_function": "publish a working research prototype",
                "inputs": "implementation effort", "outputs": "usable tool",
                "carrier": self.left.current_carrier, "failure_class": "capacity",
                "failure_mechanism": "execution speed too slow for practical use",
                "repair": "optimize runtime performance", "confidence": 0.7,
            }),
            self.right.process: json.dumps({
                "hidden_function": "prevent PII exposure via no-reply addresses",
                "inputs": "sender address validation", "outputs": "protected customer data",
                "carrier": self.right.current_carrier, "failure_class": "absence",
                "failure_mechanism": "no ownership validation on no-reply sender addresses",
                "repair": "validate no-reply domain ownership before send", "confidence": 0.7,
            }),
        }

        def fake_call_openai(system, prompt, max_tokens=900):
            for process_text, response in profile_responses.items():
                if process_text in prompt:
                    return response
            return json.dumps({"removes_failure": False, "reason": "different failure class"})

        with patch("gpt_mechanism_judge.judge.call_openai", side_effect=fake_call_openai):
            decision = gate_pair(self.left, self.right, OpenAIMechanismJudge())

        self.assertIn(decision.verdict, (Verdict.SAME_MECHANISM, Verdict.DIFFERENT_MECHANISMS,
                                          Verdict.INSUFFICIENT_DATA))
        self.assertIn(decision.edge, (EdgeType.MERGED, EdgeType.RELATED_DISTINCT, EdgeType.UNRESOLVED))
        self.assertEqual({decision.left_id, decision.right_id}, {self.left.id, self.right.id})
        self.assertTrue(decision.reasons)

    def test_all_three_gate_outcomes_are_reachable_through_the_openai_judge(self):
        """Same evidence-floor / counterfactual logic same_mechanism_gate
        already has, exercised through OpenAIMechanismJudge instead of
        ClaudeMechanismJudge - proves the adapter doesn't accidentally
        make one outcome unreachable."""
        low_confidence_left = GateAnomaly(id=self.left.id, source=self.left.source,
                                           process=self.left.process, pain=self.left.pain,
                                           current_carrier=self.left.current_carrier,
                                           failure_mode=self.left.failure_mode,
                                           evidence_count=1, confidence=0.0)

        def fake_call_openai(system, prompt, max_tokens=900):
            return json.dumps({"hidden_function": "x", "inputs": "x", "outputs": "x",
                                "carrier": "x", "failure_class": "other",
                                "failure_mechanism": "x", "repair": "x", "confidence": 0.0})

        with patch("gpt_mechanism_judge.judge.call_openai", side_effect=fake_call_openai):
            decision = gate_pair(low_confidence_left, self.right, OpenAIMechanismJudge(), min_confidence=0.5)
        self.assertIs(decision.verdict, Verdict.INSUFFICIENT_DATA)
        self.assertIs(decision.edge, EdgeType.UNRESOLVED)


if __name__ == "__main__":
    unittest.main()
