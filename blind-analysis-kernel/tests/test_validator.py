import _pathsetup  # noqa: F401
import unittest

from blind_analysis_kernel.models import IndependentAnalysisArtifact
from blind_analysis_kernel.validator import ArtifactValidationError, validate

_VALID_HASH = "a" * 64


def _artifact(**overrides) -> IndependentAnalysisArtifact:
    base = dict(
        artifact_id="analysis:abc",
        run_id="run-1",
        source_case_ids=["case:abc"],
        source_artifact_ids=["OBS-1"],
        provider="anthropic",
        model="claude-sonnet-4-5",
        created_at="2026-08-18T00:00:00Z",
        input_packet_sha256=_VALID_HASH,
        analysis={"hidden_function": "x"},
    )
    base.update(overrides)
    return IndependentAnalysisArtifact(**base)


class ValidatorTests(unittest.TestCase):
    def test_valid_artifact_passes(self):
        validate(_artifact())  # must not raise

    def test_wrong_artifact_type_rejected(self):
        with self.assertRaises(ArtifactValidationError):
            validate(_artifact(artifact_type="case"))

    def test_created_at_must_end_in_z(self):
        with self.assertRaises(ArtifactValidationError):
            validate(_artifact(created_at="2026-08-18T00:00:00"))

    def test_blank_artifact_id_rejected(self):
        with self.assertRaises(ArtifactValidationError):
            validate(_artifact(artifact_id=""))

    def test_empty_source_case_ids_rejected(self):
        with self.assertRaises(ArtifactValidationError):
            validate(_artifact(source_case_ids=[]))

    def test_empty_source_artifact_ids_rejected(self):
        with self.assertRaises(ArtifactValidationError):
            validate(_artifact(source_artifact_ids=[]))

    def test_short_hash_rejected(self):
        with self.assertRaises(ArtifactValidationError):
            validate(_artifact(input_packet_sha256="tooshort"))

    def test_non_dict_analysis_rejected(self):
        with self.assertRaises(ArtifactValidationError):
            validate(_artifact(analysis="not a dict"))

    def test_non_string_in_source_case_ids_rejected(self):
        with self.assertRaises(ArtifactValidationError):
            validate(_artifact(source_case_ids=["ok", 123]))


if __name__ == "__main__":
    unittest.main()
