import _pathsetup  # noqa: F401
import json
import unittest
from dataclasses import fields

from blind_analysis_kernel.packet import EvidencePacket, packet_sha256


def _packet(**overrides) -> EvidencePacket:
    base = dict(
        run_id="run-1",
        protocol_version="0.1.0",
        source_case_ids=["case:abc"],
        source_artifact_ids=["OBS-1"],
        anomaly={"id": "OBS-1", "source": "hn", "process": "p", "pain": "pain",
                 "current_carrier": "cc", "failure_mode": "fm", "evidence_count": 1, "confidence": 0.5},
        profile_prompt_template="template text",
        system_prompt_note="note",
        created_at="2026-08-18T00:00:00Z",
    )
    base.update(overrides)
    return EvidencePacket(**base)


class PacketHashTests(unittest.TestCase):
    def test_identical_packets_hash_identically(self):
        self.assertEqual(packet_sha256(_packet()), packet_sha256(_packet()))

    def test_different_anomaly_content_changes_hash(self):
        h1 = packet_sha256(_packet())
        h2 = packet_sha256(_packet(anomaly={"id": "OBS-2", "source": "hn", "process": "different",
                                             "pain": "pain", "current_carrier": "cc", "failure_mode": "fm",
                                             "evidence_count": 1, "confidence": 0.5}))
        self.assertNotEqual(h1, h2)

    def test_hash_is_a_full_sha256_hex_digest(self):
        h = packet_sha256(_packet())
        self.assertEqual(len(h), 64)
        int(h, 16)  # raises if not valid hex

    def test_hash_survives_a_json_round_trip(self):
        """Simulates the real workflow: prepare-input serializes the
        packet to a file, an actions/upload-artifact + download-artifact
        round trip happens, and the claude/gpt jobs each deserialize a
        fresh copy - the hash must still match."""
        original = _packet()
        roundtripped = EvidencePacket.from_dict(json.loads(json.dumps(original.to_dict())))
        self.assertEqual(packet_sha256(original), packet_sha256(roundtripped))


class PacketContainsNothingFromAnalysisTests(unittest.TestCase):
    """Task §1's 'MUST NOT contain' list, enforced by field-set
    inspection - see packet.py's own docstring for why this is checked
    structurally rather than by convention alone."""

    _FORBIDDEN_FIELD_NAME_FRAGMENTS = (
        "verdict", "confidence_score", "mechanism_profile", "gate_decision",
        "provider", "model", "analysis",
    )

    def test_no_field_name_shaped_like_an_analysis_output(self):
        field_names = {f.name for f in fields(EvidencePacket)}
        for name in field_names:
            for forbidden in self._FORBIDDEN_FIELD_NAME_FRAGMENTS:
                self.assertNotIn(forbidden, name,
                                  f"EvidencePacket field {name!r} looks analysis-shaped - "
                                  "the packet must be built before either provider runs")

    def test_field_set_is_exactly_what_task_section_1_allows(self):
        field_names = {f.name for f in fields(EvidencePacket)}
        self.assertEqual(field_names, {
            "run_id", "protocol_version", "source_case_ids", "source_artifact_ids",
            "anomaly", "profile_prompt_template", "system_prompt_note", "created_at",
        })


if __name__ == "__main__":
    unittest.main()
