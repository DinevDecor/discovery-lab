"""Task Sec 14: 'T0 packet hash is stable' and 'no post-T0 evidence
enters frozen packet' (the second half of that guarantee, structural
consistency, is proven in test_validator.py - this file proves the hash
function itself is a stable, deterministic function of exactly
t0_cutoff+evidence, nothing else)."""

import _pathsetup  # noqa: F401
import unittest

from prospective_ground_truth.models import T0EvidenceItem
from prospective_ground_truth.packet import compute_packet_sha256


def _item(**overrides):
    base = dict(artifact_id="EV-1", citation="Official Gazette", source_url="https://example.gov/x",
                captured_at="2026-08-01", quote_or_summary="Application filed.")
    base.update(overrides)
    return T0EvidenceItem(**base)


class PacketHashStabilityTests(unittest.TestCase):
    def test_same_inputs_produce_same_hash(self):
        a = compute_packet_sha256("2026-08-15", [_item()])
        b = compute_packet_sha256("2026-08-15", [_item()])
        self.assertEqual(a, b)

    def test_hash_is_a_sha256_hex_digest(self):
        h = compute_packet_sha256("2026-08-15", [_item()])
        self.assertEqual(len(h), 64)
        int(h, 16)  # raises ValueError if not valid hex

    def test_different_t0_cutoff_changes_hash(self):
        a = compute_packet_sha256("2026-08-15", [_item()])
        b = compute_packet_sha256("2026-08-16", [_item()])
        self.assertNotEqual(a, b)

    def test_different_quote_changes_hash(self):
        a = compute_packet_sha256("2026-08-15", [_item(quote_or_summary="Application filed.")])
        b = compute_packet_sha256("2026-08-15", [_item(quote_or_summary="Application filed and fee paid.")])
        self.assertNotEqual(a, b)

    def test_additional_evidence_item_changes_hash(self):
        a = compute_packet_sha256("2026-08-15", [_item()])
        b = compute_packet_sha256("2026-08-15", [_item(), _item(artifact_id="EV-2")])
        self.assertNotEqual(a, b)

    def test_evidence_order_changes_hash(self):
        """Deliberate: the packet is not order-independent - two
        evidence items presented in a different order are, byte for
        byte, a different frozen packet. This is the same 'evidence list
        is content, not a set' choice made throughout this repo."""
        e1, e2 = _item(artifact_id="EV-1"), _item(artifact_id="EV-2")
        a = compute_packet_sha256("2026-08-15", [e1, e2])
        b = compute_packet_sha256("2026-08-15", [e2, e1])
        self.assertNotEqual(a, b)

    def test_empty_evidence_list_still_hashes_deterministically(self):
        a = compute_packet_sha256("2026-08-15", [])
        b = compute_packet_sha256("2026-08-15", [])
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
