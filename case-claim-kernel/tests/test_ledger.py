import _pathsetup  # noqa: F401
import json
import os
import tempfile
import unittest

from case_claim_kernel.envelope import build_case_envelope
from case_claim_kernel.ledger import ArtifactLedger
from case_claim_kernel.models import Case


def _case(source_record_id="ANOM-0001") -> Case:
    from case_claim_kernel.identity import make_case_id
    return Case(
        case_id=make_case_id("constraint_archaeology_agents", "anomaly", source_record_id),
        source_system="constraint_archaeology_agents",
        source_record_type="anomaly",
        source_record_id=source_record_id,
        source_status="WATCH",
        derived_from=[source_record_id],
        source_evidence_ids=["OBS-1", "OBS-2"],
    )


class ArtifactLedgerTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self._tmp.name, "artifacts.jsonl")

    def tearDown(self):
        self._tmp.cleanup()

    def test_append_writes_one_line(self):
        ledger = ArtifactLedger(self.path)
        envelope = build_case_envelope(_case())
        written = ledger.append(envelope)
        self.assertTrue(written)
        with open(self.path, encoding="utf-8") as f:
            lines = [l for l in f if l.strip()]
        self.assertEqual(len(lines), 1)
        row = json.loads(lines[0])
        self.assertEqual(row["artifact_id"], envelope.artifact_id)

    def test_append_is_idempotent_for_same_artifact_id(self):
        ledger = ArtifactLedger(self.path)
        envelope = build_case_envelope(_case())
        self.assertTrue(ledger.append(envelope))
        self.assertFalse(ledger.append(envelope))
        with open(self.path, encoding="utf-8") as f:
            lines = [l for l in f if l.strip()]
        self.assertEqual(len(lines), 1, "a re-append of the same artifact_id must not add a second line")

    def test_known_ids_survive_reload_from_disk(self):
        ledger = ArtifactLedger(self.path)
        envelope = build_case_envelope(_case())
        ledger.append(envelope)

        reopened = ArtifactLedger(self.path)
        self.assertTrue(reopened.has(envelope.artifact_id))
        self.assertFalse(reopened.append(envelope))

    def test_append_only_never_rewrites_existing_lines(self):
        ledger = ArtifactLedger(self.path)
        e1 = build_case_envelope(_case("ANOM-0001"))
        e2 = build_case_envelope(_case("ANOM-0002"))
        ledger.append(e1)
        with open(self.path, encoding="utf-8") as f:
            first_line_before = f.readline()
        ledger.append(e2)
        with open(self.path, encoding="utf-8") as f:
            first_line_after = f.readline()
        self.assertEqual(first_line_before, first_line_after)

    def test_corrupt_line_is_skipped_not_repaired(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("not valid json\n")
        ledger = ArtifactLedger(self.path)
        self.assertEqual(ledger.known_count, 0)
        with open(self.path, encoding="utf-8") as f:
            self.assertEqual(f.read(), "not valid json\n", "a corrupt line must never be rewritten")


if __name__ == "__main__":
    unittest.main()
