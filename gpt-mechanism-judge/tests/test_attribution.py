import _pathsetup  # noqa: F401
import unittest
from dataclasses import dataclass, field
from typing import Any, Dict, List

from gpt_mechanism_judge.attribution import attribute_gate_decision, attribute_mechanism_profile


@dataclass(frozen=True)
class _FakeMechanismProfile:
    """Shape-compatible stand-in for ca_agents.same_mechanism_gate
    .MechanismProfile - this test module has no dependency on ca_agents."""
    anomaly_id: str
    hidden_function: str
    inputs: str
    outputs: str
    carrier: str
    failure_class: str
    failure_mechanism: str
    repair: str
    confidence: float
    evidence_count: int


@dataclass(frozen=True)
class _FakeGateDecision:
    verdict: str
    edge: str
    left_id: str
    right_id: str
    reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {"verdict": self.verdict, "edge": self.edge, "left_id": self.left_id,
                "right_id": self.right_id, "reasons": list(self.reasons)}


def _profile(anomaly_id="OBS-1"):
    return _FakeMechanismProfile(anomaly_id, "hf", "in", "out", "carrier", "absence",
                                  "mech", "repair", 0.8, 1)


class AttributeMechanismProfileTests(unittest.TestCase):
    def test_carries_required_fields(self):
        result = attribute_mechanism_profile(
            _profile(), provider="openai", model="gpt-4.1",
            source_case_ids=["case:abc"], source_artifact_ids=["OBS-1"])
        self.assertEqual(result.provider, "openai")
        self.assertEqual(result.model, "gpt-4.1")
        self.assertEqual(result.source_case_ids, ["case:abc"])
        self.assertEqual(result.source_artifact_ids, ["OBS-1"])
        self.assertTrue(result.created_at.endswith("Z"))

    def test_analysis_payload_is_the_full_profile(self):
        result = attribute_mechanism_profile(
            _profile(), provider="openai", model="gpt-4.1",
            source_case_ids=["case:abc"], source_artifact_ids=["OBS-1"])
        self.assertEqual(result.analysis["hidden_function"], "hf")
        self.assertEqual(result.analysis_kind, "mechanism_profile")

    def test_model_version_optional(self):
        result = attribute_mechanism_profile(
            _profile(), provider="openai", model="gpt-4.1", model_version="2025-04-14",
            source_case_ids=["case:abc"], source_artifact_ids=["OBS-1"])
        self.assertEqual(result.model_version, "2025-04-14")

        result_no_version = attribute_mechanism_profile(
            _profile(), provider="openai", model="gpt-4.1",
            source_case_ids=["case:abc"], source_artifact_ids=["OBS-1"])
        self.assertIsNone(result_no_version.model_version)


class SourceCaseIdsCardinalityTests(unittest.TestCase):
    """Stage 3 §0: source_case_ids is a List[str] - each real Stage-1
    case_id preserved separately, never concatenated into a synthetic
    pseudo-id string, with deterministic (sorted, deduplicated) ordering
    regardless of the order the caller passed them in."""

    def test_two_real_case_ids_preserved_separately_not_concatenated(self):
        left = "case:951963c3345d364c44c2f2ab34197651"
        right = "case:d6d245e175ca511011a102dad279f13b"
        result = attribute_mechanism_profile(
            _profile(), provider="openai", model="gpt-4.1",
            source_case_ids=[left, right], source_artifact_ids=["OBS-1", "OBS-2"])
        self.assertEqual(set(result.source_case_ids), {left, right})
        self.assertEqual(len(result.source_case_ids), 2)
        for case_id in result.source_case_ids:
            self.assertNotIn("|", case_id, "a real case_id must never contain the old pipe-joined separator")

    def test_ordering_is_deterministic_regardless_of_caller_order(self):
        left = "case:951963c3345d364c44c2f2ab34197651"
        right = "case:d6d245e175ca511011a102dad279f13b"
        forward = attribute_mechanism_profile(
            _profile(), provider="openai", model="gpt-4.1",
            source_case_ids=[left, right], source_artifact_ids=["OBS-1"])
        backward = attribute_mechanism_profile(
            _profile(), provider="openai", model="gpt-4.1",
            source_case_ids=[right, left], source_artifact_ids=["OBS-1"])
        self.assertEqual(forward.source_case_ids, backward.source_case_ids)

    def test_duplicate_case_ids_are_not_repeated(self):
        case_id = "case:951963c3345d364c44c2f2ab34197651"
        result = attribute_mechanism_profile(
            _profile(), provider="openai", model="gpt-4.1",
            source_case_ids=[case_id, case_id], source_artifact_ids=["OBS-1"])
        self.assertEqual(result.source_case_ids, [case_id])

    def test_field_type_is_a_list_never_a_string(self):
        result = attribute_mechanism_profile(
            _profile(), provider="openai", model="gpt-4.1",
            source_case_ids=["case:abc"], source_artifact_ids=["OBS-1"])
        self.assertIsInstance(result.source_case_ids, list)


class ProviderIdentityStaysOutOfSemanticIdentityTests(unittest.TestCase):
    """Requirement 4: 'the same claim analyzed by Claude and GPT must
    remain the same claim, with two distinct analysis artifacts.'"""

    def test_same_source_case_ids_two_different_providers_two_distinct_artifacts(self):
        same_case_ids = ["case:951963c3345d364c44c2f2ab34197651"]  # real Stage 1 case_id for ANOM-0001
        claude_analysis = attribute_mechanism_profile(
            _profile(), provider="anthropic", model="claude-sonnet-4-5",
            source_case_ids=same_case_ids, source_artifact_ids=["OBS-1"])
        gpt_analysis = attribute_mechanism_profile(
            _profile(), provider="openai", model="gpt-4.1",
            source_case_ids=same_case_ids, source_artifact_ids=["OBS-1"])

        # Identity: unchanged by which provider analyzed it.
        self.assertEqual(claude_analysis.source_case_ids, gpt_analysis.source_case_ids)
        # Attribution: genuinely distinct.
        self.assertNotEqual(claude_analysis.provider, gpt_analysis.provider)
        self.assertNotEqual(claude_analysis.model, gpt_analysis.model)
        # Two distinct artifacts, not one overwritten by the other.
        self.assertIsNot(claude_analysis, gpt_analysis)
        self.assertNotEqual(claude_analysis.to_dict(), gpt_analysis.to_dict())

    def test_attribution_dataclass_has_no_field_that_could_be_mistaken_for_claim_identity(self):
        """Structural guard: AttributedAnalysis must never grow a
        `case_id`/`claim_id`-shaped field that participates in identity -
        `source_case_ids` is a list of REFERENCES to identities, never an
        identity itself (case_claim_kernel.identity remains the only place
        case_id/claim_id values are minted)."""
        from dataclasses import fields
        from gpt_mechanism_judge.attribution import AttributedAnalysis
        field_names = {f.name for f in fields(AttributedAnalysis)}
        self.assertNotIn("case_id", field_names)
        self.assertNotIn("claim_id", field_names)
        self.assertIn("source_case_ids", field_names)


class AttributeGateDecisionTests(unittest.TestCase):
    def test_carries_required_fields_and_decision_payload(self):
        decision = _FakeGateDecision("different_mechanisms", "related_distinct", "OBS-1", "OBS-2")
        result = attribute_gate_decision(
            decision, provider="openai", model="gpt-4.1",
            source_case_ids=["case:a", "case:b"], source_artifact_ids=["OBS-1", "OBS-2"])
        self.assertEqual(result.analysis_kind, "same_mechanism_decision")
        self.assertEqual(result.analysis["verdict"], "different_mechanisms")
        self.assertEqual(result.source_case_ids, ["case:a", "case:b"])
        self.assertEqual(result.source_artifact_ids, ["OBS-1", "OBS-2"])


if __name__ == "__main__":
    unittest.main()
