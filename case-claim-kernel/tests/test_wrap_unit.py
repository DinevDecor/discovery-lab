"""Unit-level coverage for wrap.py paths the real, currently-committed
data doesn't exercise - `latest-evaluations.json` is empty today (no
anomaly has been evaluated yet), so `wrap_ca_evaluation_claims` needs a
synthetic Evaluation-shaped dict to prove the k1..k6 mapping. This is
deliberately separate from test_wrap_real_data.py, which is the
acceptance test and touches only real, already-committed data.
"""

import _pathsetup  # noqa: F401
import unittest

from case_claim_kernel.identity import make_case_id
from case_claim_kernel.wrap import find_by_id, wrap_ca_anomaly, wrap_ca_evaluation_claims

# Shape matches ca_agents.models.Evaluation.to_dict() exactly.
_SYNTHETIC_EVALUATION = {
    "anomaly_id": "ANOM-0001",
    "mechanism_verdict": "SAME_MECHANISM",
    "capture_verdict": "CAPTURED",
    "k1": "PASS",
    "k2": "PASS",
    "k3": "FAIL",
    "k4": "INSUFFICIENT_DATA",
    "k5": "PASS",
    "k6": "PASS",
    "rationale": "synthetic example for unit coverage only, not real pipeline output",
    "evidence_used": ["OBS-0001", "OBS-0002"],
    "action": "INVESTIGATE",
}


class WrapCaEvaluationClaimsTests(unittest.TestCase):
    def test_produces_one_claim_per_evaluation_field(self):
        case_id = make_case_id("constraint_archaeology_agents", "anomaly", "ANOM-0001")
        claims = wrap_ca_evaluation_claims(case_id, _SYNTHETIC_EVALUATION)
        names = {c.name for c in claims}
        self.assertEqual(names, {"mechanism_verdict", "capture_verdict", "k1", "k2", "k3", "k4", "k5", "k6"})

    def test_claim_values_copied_unchanged(self):
        case_id = make_case_id("constraint_archaeology_agents", "anomaly", "ANOM-0001")
        claims = {c.name: c for c in wrap_ca_evaluation_claims(case_id, _SYNTHETIC_EVALUATION)}
        self.assertEqual(claims["k3"].value, "FAIL")
        self.assertEqual(claims["mechanism_verdict"].value, "SAME_MECHANISM")

    def test_evidence_copied_from_evidence_used(self):
        case_id = make_case_id("constraint_archaeology_agents", "anomaly", "ANOM-0001")
        claims = wrap_ca_evaluation_claims(case_id, _SYNTHETIC_EVALUATION)
        for claim in claims:
            self.assertEqual(claim.evidence, ["OBS-0001", "OBS-0002"])

    def test_missing_optional_fields_are_skipped_not_fabricated(self):
        case_id = make_case_id("constraint_archaeology_agents", "anomaly", "ANOM-0001")
        partial = {"anomaly_id": "ANOM-0001", "k1": "PASS", "evidence_used": []}
        claims = wrap_ca_evaluation_claims(case_id, partial)
        self.assertEqual([c.name for c in claims], ["k1"])


class FindByIdTests(unittest.TestCase):
    def test_finds_matching_record(self):
        records = [{"anomaly_id": "A"}, {"anomaly_id": "B"}]
        self.assertEqual(find_by_id(records, "anomaly_id", "B"), {"anomaly_id": "B"})

    def test_returns_none_when_absent(self):
        records = [{"anomaly_id": "A"}]
        self.assertIsNone(find_by_id(records, "anomaly_id", "Z"))


class WrapCaAnomalyWithoutEvaluationTests(unittest.TestCase):
    def test_no_evaluation_means_empty_claims_not_fabricated_ones(self):
        anomaly = {
            "anomaly_id": "ANOM-9999",
            "canonical_pattern": "example pattern",
            "hidden_function_class": "unclassified",
            "observation_ids": ["OBS-1"],
            "independent_sources": ["hn"],
            "status": "WATCH",
        }
        case, claims = wrap_ca_anomaly(anomaly)
        self.assertEqual(claims, [])
        self.assertEqual(case.source_status, "WATCH")


if __name__ == "__main__":
    unittest.main()
