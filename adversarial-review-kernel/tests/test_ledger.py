"""Task §12: 'append-only review persistence', plus idempotency and
never-deduping-two-providers-into-one, mirroring
blind_analysis_kernel.ledger's own test shape.
"""

import _pathsetup  # noqa: F401
import json
import os
import tempfile
import unittest

from adversarial_review_kernel.ledger import FalsificationLedger, JudgmentLedger
from adversarial_review_kernel.models import FalsificationArtifact, FalsificationFinding, JudgmentArtifact

_HASH = "b" * 64


def _falsification(critic_provider="anthropic", artifact_id=None, target="analysis:gpt") -> FalsificationArtifact:
    return FalsificationArtifact(
        artifact_id=artifact_id or f"falsification:{critic_provider}",
        run_id="run-1", critic_provider=critic_provider, critic_model="m",
        target_artifact_id=target, source_case_ids=["case:abc"], input_packet_sha256=_HASH,
        findings=[FalsificationFinding(field="carrier", target_analysis_artifact_id=target,
                                        classification="SCHEMA_AMBIGUITY", reason="r",
                                        source_artifact_ids=["OBS-1"], material=True)],
        created_at="2026-08-18T00:00:00Z",
    )


def _judgment(judgment_id="judgment:run-1") -> JudgmentArtifact:
    return JudgmentArtifact(
        judgment_id=judgment_id, case_id="case:abc", source_run_id="run-1",
        source_analysis_artifact_ids=["analysis:claude", "analysis:gpt"],
        source_falsification_artifact_ids=["falsification:anthropic", "falsification:openai"],
        status="WATCH", reasons=["r"], material_disagreements=[], schema_ambiguities=["carrier"],
        created_at="2026-08-18T00:00:00Z",
    )


class FalsificationLedgerTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self._tmp.name, "falsifications.jsonl")

    def tearDown(self):
        self._tmp.cleanup()

    def test_append_writes_one_line(self):
        ledger = FalsificationLedger(self.path)
        self.assertTrue(ledger.append(_falsification()))
        with open(self.path, encoding="utf-8") as f:
            self.assertEqual(len([l for l in f if l.strip()]), 1)

    def test_two_different_critics_both_persist_as_separate_lines(self):
        ledger = FalsificationLedger(self.path)
        ledger.append(_falsification(critic_provider="anthropic"))
        ledger.append(_falsification(critic_provider="openai"))
        with open(self.path, encoding="utf-8") as f:
            lines = [l for l in f if l.strip()]
        self.assertEqual(len(lines), 2)
        self.assertEqual({json.loads(l)["critic_provider"] for l in lines}, {"anthropic", "openai"})

    def test_append_is_idempotent(self):
        ledger = FalsificationLedger(self.path)
        artifact = _falsification()
        self.assertTrue(ledger.append(artifact))
        self.assertFalse(ledger.append(artifact))
        with open(self.path, encoding="utf-8") as f:
            self.assertEqual(len([l for l in f if l.strip()]), 1)

    def test_append_never_rewrites_prior_lines(self):
        ledger = FalsificationLedger(self.path)
        ledger.append(_falsification(critic_provider="anthropic"))
        with open(self.path, encoding="utf-8") as f:
            before = f.readline()
        ledger.append(_falsification(critic_provider="openai"))
        with open(self.path, encoding="utf-8") as f:
            after = f.readline()
        self.assertEqual(before, after)


class JudgmentLedgerTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self._tmp.name, "judgments.jsonl")

    def tearDown(self):
        self._tmp.cleanup()

    def test_append_writes_one_line(self):
        ledger = JudgmentLedger(self.path)
        self.assertTrue(ledger.append(_judgment()))
        with open(self.path, encoding="utf-8") as f:
            self.assertEqual(len([l for l in f if l.strip()]), 1)

    def test_append_is_idempotent(self):
        ledger = JudgmentLedger(self.path)
        j = _judgment()
        self.assertTrue(ledger.append(j))
        self.assertFalse(ledger.append(j))

    def test_two_different_runs_both_persist(self):
        ledger = JudgmentLedger(self.path)
        ledger.append(_judgment("judgment:run-1"))
        ledger.append(_judgment("judgment:run-2"))
        with open(self.path, encoding="utf-8") as f:
            self.assertEqual(len([l for l in f if l.strip()]), 2)

    def test_known_ids_survive_reload_from_disk(self):
        ledger = JudgmentLedger(self.path)
        j = _judgment()
        ledger.append(j)
        reopened = JudgmentLedger(self.path)
        self.assertTrue(reopened.has(j.judgment_id))
        self.assertFalse(reopened.append(j))


if __name__ == "__main__":
    unittest.main()
