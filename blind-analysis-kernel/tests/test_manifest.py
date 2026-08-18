import _pathsetup  # noqa: F401
import os
import tempfile
import unittest

from blind_analysis_kernel.manifest import (
    ManifestValidationError,
    RunManifestLedger,
    build_run_manifest,
    make_manifest_id,
    validate_manifest,
)
from blind_analysis_kernel.models import IndependentAnalysisArtifact

_HASH = "c" * 64


def _artifact(provider="anthropic", model="claude-sonnet-4-5", run_id="run-1") -> IndependentAnalysisArtifact:
    return IndependentAnalysisArtifact(
        artifact_id=f"analysis:{provider}",
        run_id=run_id,
        source_case_ids=["case:abc"],
        source_artifact_ids=["OBS-1"],
        provider=provider,
        model=model,
        created_at="2026-08-18T00:00:00Z",
        input_packet_sha256=_HASH,
        analysis={"x": 1},
    )


class MakeManifestIdTests(unittest.TestCase):
    def test_deterministic_for_same_run_id(self):
        self.assertEqual(make_manifest_id("run-1"), make_manifest_id("run-1"))

    def test_different_run_ids_differ(self):
        self.assertNotEqual(make_manifest_id("run-1"), make_manifest_id("run-2"))

    def test_stable_prefix(self):
        self.assertTrue(make_manifest_id("run-1").startswith("manifest:"))


class BuildRunManifestTests(unittest.TestCase):
    def test_carries_both_providers_and_run_metadata(self):
        claude = _artifact(provider="anthropic", model="claude-sonnet-4-5")
        gpt = _artifact(provider="openai", model="gpt-4.1")
        manifest = build_run_manifest(claude, gpt, workflow_run_id="32140963475",
                                       head_sha="95f2170", created_at="2026-08-18T00:00:00Z")
        self.assertEqual(manifest.run_id, "run-1")
        self.assertEqual(manifest.workflow_run_id, "32140963475")
        self.assertEqual(manifest.head_sha, "95f2170")
        self.assertEqual(manifest.claude_artifact_id, claude.artifact_id)
        self.assertEqual(manifest.claude_provider, "anthropic")
        self.assertEqual(manifest.claude_model, "claude-sonnet-4-5")
        self.assertEqual(manifest.gpt_artifact_id, gpt.artifact_id)
        self.assertEqual(manifest.gpt_provider, "openai")
        self.assertEqual(manifest.gpt_model, "gpt-4.1")
        self.assertEqual(manifest.input_packet_sha256, _HASH)
        self.assertEqual(manifest.source_case_ids, ["case:abc"])

    def test_does_not_duplicate_the_analysis_payload(self):
        """Task §3: 'Do not duplicate information unnecessarily if
        analyses.jsonl already contains it' - no `analysis` field here."""
        from dataclasses import fields
        field_names = {f.name for f in fields(build_run_manifest(
            _artifact("anthropic"), _artifact("openai"),
            workflow_run_id="r", head_sha="h", created_at="2026-08-18T00:00:00Z").__class__)}
        self.assertNotIn("analysis", field_names)

    def test_manifest_id_is_scoped_to_run_id(self):
        claude = _artifact(run_id="run-42")
        gpt = _artifact(run_id="run-42")
        manifest = build_run_manifest(claude, gpt, workflow_run_id="r", head_sha="h",
                                       created_at="2026-08-18T00:00:00Z")
        self.assertEqual(manifest.manifest_id, make_manifest_id("run-42"))


class ValidateManifestTests(unittest.TestCase):
    def _manifest(self):
        return build_run_manifest(_artifact("anthropic"), _artifact("openai"),
                                   workflow_run_id="r", head_sha="h", created_at="2026-08-18T00:00:00Z")

    def test_valid_manifest_passes(self):
        validate_manifest(self._manifest())  # must not raise

    def test_blank_head_sha_rejected(self):
        from dataclasses import replace
        with self.assertRaises(ManifestValidationError):
            validate_manifest(replace(self._manifest(), head_sha=""))

    def test_created_at_must_end_in_z(self):
        from dataclasses import replace
        with self.assertRaises(ManifestValidationError):
            validate_manifest(replace(self._manifest(), created_at="2026-08-18T00:00:00"))

    def test_colliding_provider_artifact_ids_rejected(self):
        from dataclasses import replace
        with self.assertRaises(ManifestValidationError):
            validate_manifest(replace(self._manifest(), gpt_artifact_id=self._manifest().claude_artifact_id))

    def test_empty_source_case_ids_rejected(self):
        from dataclasses import replace
        with self.assertRaises(ManifestValidationError):
            validate_manifest(replace(self._manifest(), source_case_ids=[]))


class RunManifestLedgerTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self._tmp.name, "runs.jsonl")

    def tearDown(self):
        self._tmp.cleanup()

    def _manifest(self, run_id="run-1"):
        return build_run_manifest(_artifact("anthropic", run_id=run_id), _artifact("openai", run_id=run_id),
                                   workflow_run_id=run_id, head_sha="h", created_at="2026-08-18T00:00:00Z")

    def test_append_writes_one_line(self):
        ledger = RunManifestLedger(self.path)
        self.assertTrue(ledger.append(self._manifest()))
        with open(self.path, encoding="utf-8") as f:
            lines = [l for l in f if l.strip()]
        self.assertEqual(len(lines), 1)

    def test_append_is_idempotent_for_same_run(self):
        ledger = RunManifestLedger(self.path)
        m = self._manifest()
        self.assertTrue(ledger.append(m))
        self.assertFalse(ledger.append(m))
        with open(self.path, encoding="utf-8") as f:
            lines = [l for l in f if l.strip()]
        self.assertEqual(len(lines), 1)

    def test_two_different_runs_both_persist(self):
        ledger = RunManifestLedger(self.path)
        ledger.append(self._manifest("run-1"))
        ledger.append(self._manifest("run-2"))
        with open(self.path, encoding="utf-8") as f:
            lines = [l for l in f if l.strip()]
        self.assertEqual(len(lines), 2)

    def test_append_never_rewrites_prior_lines(self):
        ledger = RunManifestLedger(self.path)
        ledger.append(self._manifest("run-1"))
        with open(self.path, encoding="utf-8") as f:
            before = f.readline()
        ledger.append(self._manifest("run-2"))
        with open(self.path, encoding="utf-8") as f:
            after = f.readline()
        self.assertEqual(before, after)

    def test_known_ids_survive_reload_from_disk(self):
        ledger = RunManifestLedger(self.path)
        m = self._manifest()
        ledger.append(m)
        reopened = RunManifestLedger(self.path)
        self.assertTrue(reopened.has(m.manifest_id))
        self.assertFalse(reopened.append(m))


if __name__ == "__main__":
    unittest.main()
