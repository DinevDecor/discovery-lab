import _pathsetup  # noqa: F401
import unittest

from case_claim_kernel.models import ArtifactEnvelope
from case_claim_kernel.validator import EnvelopeValidationError, validate


def _envelope(**overrides) -> ArtifactEnvelope:
    base = dict(
        artifact_id="case:abc",
        kind="case",
        recorded_at="2026-08-18T00:00:00Z",
        derived_from=["ANOM-0001"],
        analyst="case_claim_kernel",
        analyst_version="0.1.0",
        payload={"source_record_id": "ANOM-0001"},
        origin="generated",
    )
    base.update(overrides)
    return ArtifactEnvelope(**base)


class ValidatorTests(unittest.TestCase):
    def test_valid_envelope_passes(self):
        validate(_envelope())  # must not raise

    def test_unknown_kind_rejected(self):
        with self.assertRaises(EnvelopeValidationError):
            validate(_envelope(kind="decision"))

    def test_non_generated_origin_rejected(self):
        with self.assertRaises(EnvelopeValidationError):
            validate(_envelope(origin="captured"))

    def test_recorded_at_must_end_in_z(self):
        with self.assertRaises(EnvelopeValidationError):
            validate(_envelope(recorded_at="2026-08-18T00:00:00"))

    def test_empty_derived_from_rejected_without_flag(self):
        with self.assertRaises(EnvelopeValidationError):
            validate(_envelope(derived_from=[]))

    def test_empty_derived_from_allowed_with_flag_and_note(self):
        env = _envelope(derived_from=[], payload={"provenance_note": "no evidence on source record"})
        validate(env, allow_empty_provenance=True)  # must not raise

    def test_empty_derived_from_with_flag_but_no_note_rejected(self):
        env = _envelope(derived_from=[], payload={})
        with self.assertRaises(EnvelopeValidationError):
            validate(env, allow_empty_provenance=True)

    def test_blank_id_rejected(self):
        with self.assertRaises(EnvelopeValidationError):
            validate(_envelope(artifact_id=""))

    def test_non_string_in_derived_from_rejected(self):
        with self.assertRaises(EnvelopeValidationError):
            validate(_envelope(derived_from=["ok", 123]))


if __name__ == "__main__":
    unittest.main()
