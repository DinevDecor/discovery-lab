import _pathsetup  # noqa: F401
import unittest

from adversarial_review_kernel.models import FalsificationArtifact, FalsificationFinding, JudgmentArtifact
from adversarial_review_kernel.validator import (
    ArtifactValidationError,
    validate_falsification_artifact,
    validate_judgment_artifact,
)

_HASH = "e" * 64


def _finding(**overrides):
    base = dict(field="carrier", target_analysis_artifact_id="analysis:gpt",
                classification="SCHEMA_AMBIGUITY", reason="r",
                source_artifact_ids=["OBS-1"], material=True)
    base.update(overrides)
    return FalsificationFinding(**base)


def _falsification(**overrides):
    base = dict(artifact_id="falsification:anthropic", run_id="run-1", critic_provider="anthropic",
                critic_model="claude-sonnet-4-5", target_artifact_id="analysis:gpt",
                source_case_ids=["case:abc"], input_packet_sha256=_HASH,
                findings=[_finding()], created_at="2026-08-18T00:00:00Z")
    base.update(overrides)
    return FalsificationArtifact(**base)


def _judgment(**overrides):
    base = dict(judgment_id="judgment:run-1", case_id="case:abc", source_run_id="run-1",
                source_analysis_artifact_ids=["analysis:claude", "analysis:gpt"],
                source_falsification_artifact_ids=["falsification:anthropic", "falsification:openai"],
                status="WATCH", reasons=["r"], material_disagreements=[], schema_ambiguities=["carrier"],
                created_at="2026-08-18T00:00:00Z")
    base.update(overrides)
    return JudgmentArtifact(**base)


class FalsificationArtifactValidatorTests(unittest.TestCase):
    def test_valid_artifact_passes(self):
        validate_falsification_artifact(_falsification())

    def test_wrong_artifact_type_rejected(self):
        with self.assertRaises(ArtifactValidationError):
            validate_falsification_artifact(_falsification(artifact_type="judgment"))

    def test_empty_findings_rejected(self):
        with self.assertRaises(ArtifactValidationError):
            validate_falsification_artifact(_falsification(findings=[]))

    def test_unknown_classification_rejected(self):
        with self.assertRaises(ArtifactValidationError):
            validate_falsification_artifact(_falsification(findings=[_finding(classification="MAYBE")]))

    def test_finding_target_mismatch_rejected(self):
        with self.assertRaises(ArtifactValidationError):
            validate_falsification_artifact(
                _falsification(findings=[_finding(target_analysis_artifact_id="analysis:wrong")]))

    def test_created_at_must_end_in_z(self):
        with self.assertRaises(ArtifactValidationError):
            validate_falsification_artifact(_falsification(created_at="2026-08-18T00:00:00"))

    def test_blank_artifact_id_rejected(self):
        with self.assertRaises(ArtifactValidationError):
            validate_falsification_artifact(_falsification(artifact_id=""))


class JudgmentArtifactValidatorTests(unittest.TestCase):
    def test_valid_judgment_passes(self):
        validate_judgment_artifact(_judgment())

    def test_unknown_status_rejected(self):
        with self.assertRaises(ArtifactValidationError):
            validate_judgment_artifact(_judgment(status="MAYBE"))

    def test_empty_reasons_rejected(self):
        with self.assertRaises(ArtifactValidationError):
            validate_judgment_artifact(_judgment(reasons=[]))

    def test_empty_source_analysis_artifact_ids_rejected(self):
        with self.assertRaises(ArtifactValidationError):
            validate_judgment_artifact(_judgment(source_analysis_artifact_ids=[]))

    def test_empty_source_falsification_artifact_ids_rejected(self):
        with self.assertRaises(ArtifactValidationError):
            validate_judgment_artifact(_judgment(source_falsification_artifact_ids=[]))

    def test_created_at_must_end_in_z(self):
        with self.assertRaises(ArtifactValidationError):
            validate_judgment_artifact(_judgment(created_at="2026-08-18T00:00:00"))


if __name__ == "__main__":
    unittest.main()
