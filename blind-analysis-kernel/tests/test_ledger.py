import _pathsetup  # noqa: F401
import json
import os
import tempfile
import unittest

from blind_analysis_kernel.ledger import AnalysisLedger
from blind_analysis_kernel.models import IndependentAnalysisArtifact

_VALID_HASH = "b" * 64


def _artifact(provider="anthropic", run_id="run-1", artifact_id=None) -> IndependentAnalysisArtifact:
    return IndependentAnalysisArtifact(
        artifact_id=artifact_id or f"analysis:{provider}",
        run_id=run_id,
        source_case_ids=["case:abc"],
        source_artifact_ids=["OBS-1"],
        provider=provider,
        model="m",
        created_at="2026-08-18T00:00:00Z",
        input_packet_sha256=_VALID_HASH,
        analysis={"x": 1},
    )


class AnalysisLedgerTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self._tmp.name, "analyses.jsonl")

    def tearDown(self):
        self._tmp.cleanup()

    def test_append_writes_one_line(self):
        ledger = AnalysisLedger(self.path)
        self.assertTrue(ledger.append(_artifact()))
        with open(self.path, encoding="utf-8") as f:
            lines = [l for l in f if l.strip()]
        self.assertEqual(len(lines), 1)

    def test_two_different_providers_same_run_both_persist_as_separate_lines(self):
        """Task §9: never dedupe two different provider analyses into one
        artifact - this is the literal proof."""
        ledger = AnalysisLedger(self.path)
        ledger.append(_artifact(provider="anthropic"))
        ledger.append(_artifact(provider="openai"))
        with open(self.path, encoding="utf-8") as f:
            lines = [l for l in f if l.strip()]
        self.assertEqual(len(lines), 2)
        providers = {json.loads(l)["provider"] for l in lines}
        self.assertEqual(providers, {"anthropic", "openai"})

    def test_rerun_with_new_run_id_adds_new_lines_not_overwrite(self):
        ledger = AnalysisLedger(self.path)
        ledger.append(_artifact(provider="anthropic", run_id="run-1", artifact_id="analysis:run1-claude"))
        ledger.append(_artifact(provider="anthropic", run_id="run-2", artifact_id="analysis:run2-claude"))
        with open(self.path, encoding="utf-8") as f:
            lines = [l for l in f if l.strip()]
        self.assertEqual(len(lines), 2)

    def test_append_is_idempotent_for_same_artifact_id(self):
        ledger = AnalysisLedger(self.path)
        artifact = _artifact()
        self.assertTrue(ledger.append(artifact))
        self.assertFalse(ledger.append(artifact))
        with open(self.path, encoding="utf-8") as f:
            lines = [l for l in f if l.strip()]
        self.assertEqual(len(lines), 1)

    def test_append_validates_before_writing(self):
        from blind_analysis_kernel.validator import ArtifactValidationError
        ledger = AnalysisLedger(self.path)
        invalid = _artifact()
        invalid = IndependentAnalysisArtifact(**{**invalid.to_dict(), "source_case_ids": []})
        with self.assertRaises(ArtifactValidationError):
            ledger.append(invalid)
        self.assertFalse(os.path.exists(self.path), "an invalid artifact must never reach the file")


if __name__ == "__main__":
    unittest.main()
