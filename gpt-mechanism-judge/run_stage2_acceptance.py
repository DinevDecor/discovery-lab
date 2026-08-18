"""Stage 2 acceptance script.

The only place in this package that imports `ca_agents.same_mechanism_gate`
- that import is the boundary Stage 2 exists to test (`gate_pair`,
`GateAnomaly`, `JudgeProtocol`), not an internal implementation detail
being bypassed, so it is deliberately confined to this script and never
appears in `src/gpt_mechanism_judge/` itself (see judge.py's docstring:
the library satisfies JudgeProtocol structurally, with zero import
dependency on ca_agents at all).

Loads two REAL anomalies already committed to this repository
(`constraint-archaeology-agents/data/anomalies.json` +
`observations.jsonl`, read-only), builds the two real `GateAnomaly`
objects `ca_agents.memory.rebuild_anomalies` would itself build for them
in production, and calls the real, unmodified `gate_pair()` with an
`OpenAIMechanismJudge`.

If OPENAI_API_KEY is not set, this script builds and prints everything it
can build offline, then reports the real-provider run as
`NOT RUN — SECRET REQUIRED` rather than fabricating a result.
"""

from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(REPO_ROOT, "constraint-archaeology-agents", "src"))
sys.path.insert(0, os.path.join(REPO_ROOT, "case-claim-kernel", "src"))

from ca_agents.same_mechanism_gate import GateAnomaly, gate_pair  # noqa: E402
from case_claim_kernel.identity import make_case_id  # noqa: E402

from gpt_mechanism_judge.attribution import attribute_gate_decision  # noqa: E402
from gpt_mechanism_judge.judge import OpenAIMechanismJudge, PROVIDER  # noqa: E402
from gpt_mechanism_judge.openai_client import DEFAULT_MODEL  # noqa: E402

CA_ANOMALIES_PATH = os.path.join(REPO_ROOT, "constraint-archaeology-agents", "data", "anomalies.json")
CA_OBSERVATIONS_PATH = os.path.join(REPO_ROOT, "constraint-archaeology-agents", "data", "observations.jsonl")

# Two real, already-committed, unrelated anomalies - chosen because each
# has exactly one representative observation, keeping the acceptance case
# legible. Nothing about this choice implies they should merge; a
# DIFFERENT_MECHANISMS or INSUFFICIENT_DATA verdict is just as valid an
# acceptance result as SAME_MECHANISM (task instructions: "The acceptance
# test is not whether GPT agrees with Claude").
LEFT_ANOMALY_ID = "ANOM-0001"
RIGHT_ANOMALY_ID = "ANOM-0002"


def _load_anomalies():
    with open(CA_ANOMALIES_PATH, encoding="utf-8") as f:
        return {a["anomaly_id"]: a for a in json.load(f)}


def _load_observations():
    by_id = {}
    with open(CA_OBSERVATIONS_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            o = json.loads(line)
            by_id[o["observation_id"]] = o
    return by_id


def _to_gate_anomaly(anomaly: dict, observations: dict) -> GateAnomaly:
    rep_id = anomaly["observation_ids"][0]
    obs = observations[rep_id]
    return GateAnomaly(
        id=obs["observation_id"],
        source=obs["source"],
        process=obs["process"],
        pain=obs["pain"],
        current_carrier=obs["current_carrier"],
        failure_mode=obs["failure_mode"],
        evidence_count=len(anomaly["observation_ids"]),
        confidence=obs["confidence"],
    )


def main() -> None:
    anomalies = _load_anomalies()
    observations = _load_observations()
    left_anomaly = anomalies[LEFT_ANOMALY_ID]
    right_anomaly = anomalies[RIGHT_ANOMALY_ID]
    left = _to_gate_anomaly(left_anomaly, observations)
    right = _to_gate_anomaly(right_anomaly, observations)

    left_case_id = make_case_id("constraint_archaeology_agents", "anomaly", LEFT_ANOMALY_ID)
    right_case_id = make_case_id("constraint_archaeology_agents", "anomaly", RIGHT_ANOMALY_ID)

    report = {
        "real_anomaly_pair": [LEFT_ANOMALY_ID, RIGHT_ANOMALY_ID],
        "left_case_id": left_case_id,
        "right_case_id": right_case_id,
        "provider": PROVIDER,
        "model": DEFAULT_MODEL,
    }

    if not os.environ.get("OPENAI_API_KEY"):
        report["real_provider_run"] = "NOT RUN — SECRET REQUIRED"
        report["gate_decision"] = None
        print(json.dumps(report, indent=2, sort_keys=True))
        return

    judge = OpenAIMechanismJudge()
    decision = gate_pair(left, right, judge)  # the real, unmodified gate function
    attributed = attribute_gate_decision(
        decision,
        provider=PROVIDER,
        model=DEFAULT_MODEL,
        source_case_id=f"{left_case_id}|{right_case_id}",
        source_artifact_ids=[left.id, right.id],
    )
    report["real_provider_run"] = "SUCCESS"
    report["gate_decision"] = decision.to_dict()
    report["attributed_analysis"] = attributed.to_dict()
    print(json.dumps(report, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
