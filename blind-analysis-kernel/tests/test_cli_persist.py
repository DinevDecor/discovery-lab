"""CLI-level tests for `run_stage3_job.py`'s `merge` and `persist`
subcommands - specifically the structural-integrity gate (task §9's
"reveal succeeds" / §6's "if Git persistence fails, the workflow must
FAIL" requirements) and `persist`'s idempotent, append-only, no-git-call
behavior.
"""

import _pathsetup  # noqa: F401
import argparse
import json
import os
import sys
import tempfile
import unittest

_PKG_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PKG_ROOT not in sys.path:
    sys.path.insert(0, _PKG_ROOT)

import run_stage3_job as cli  # noqa: E402
from blind_analysis_kernel.ledger import AnalysisLedger  # noqa: E402
from blind_analysis_kernel.manifest import RunManifestLedger  # noqa: E402
from blind_analysis_kernel.models import IndependentAnalysisArtifact  # noqa: E402

_HASH = "d" * 64


def _artifact(**overrides) -> IndependentAnalysisArtifact:
    base = dict(
        artifact_id="analysis:anthropic",
        run_id="run-1",
        source_case_ids=["case:abc"],
        source_artifact_ids=["OBS-1"],
        provider="anthropic",
        model="claude-sonnet-4-5",
        created_at="2026-08-18T00:00:00Z",
        input_packet_sha256=_HASH,
        analysis={"x": 1},
    )
    base.update(overrides)
    return IndependentAnalysisArtifact(**base)


class _TmpDirTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.claude_path = os.path.join(self._tmp.name, "claude.json")
        self.gpt_path = os.path.join(self._tmp.name, "gpt.json")
        self.ledger_path = os.path.join(self._tmp.name, "analyses.jsonl")
        self.manifest_path = os.path.join(self._tmp.name, "runs.jsonl")

    def tearDown(self):
        self._tmp.cleanup()

    def _write(self, path, artifact):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(artifact.to_dict(), f)


class StructuralIntegrityGateTests(_TmpDirTestCase):
    def test_merge_refuses_mismatched_packet_hash(self):
        claude = _artifact(provider="anthropic", input_packet_sha256=_HASH)
        gpt = _artifact(artifact_id="analysis:openai", provider="openai", input_packet_sha256="e" * 64)
        self._write(self.claude_path, claude)
        self._write(self.gpt_path, gpt)
        args = argparse.Namespace(claude_artifact=self.claude_path, gpt_artifact=self.gpt_path,
                                   ledger_out=self.ledger_path)
        with self.assertRaises(SystemExit):
            cli.cmd_merge(args)
        self.assertFalse(os.path.exists(self.ledger_path), "a mismatched pair must never reach the ledger")

    def test_persist_refuses_mismatched_case_ids(self):
        claude = _artifact(provider="anthropic", source_case_ids=["case:a"])
        gpt = _artifact(artifact_id="analysis:openai", provider="openai", source_case_ids=["case:b"])
        self._write(self.claude_path, claude)
        self._write(self.gpt_path, gpt)
        args = argparse.Namespace(claude_artifact=self.claude_path, gpt_artifact=self.gpt_path,
                                   ledger_out=self.ledger_path, manifest_out=self.manifest_path,
                                   workflow_run_id="123", head_sha="abc")
        with self.assertRaises(SystemExit):
            cli.cmd_persist(args)
        self.assertFalse(os.path.exists(self.ledger_path), "a mismatched pair must never be persisted")
        self.assertFalse(os.path.exists(self.manifest_path))

    def test_persist_refuses_colliding_artifact_ids(self):
        claude = _artifact(artifact_id="analysis:same", provider="anthropic")
        gpt = _artifact(artifact_id="analysis:same", provider="openai")
        self._write(self.claude_path, claude)
        self._write(self.gpt_path, gpt)
        args = argparse.Namespace(claude_artifact=self.claude_path, gpt_artifact=self.gpt_path,
                                   ledger_out=self.ledger_path, manifest_out=self.manifest_path,
                                   workflow_run_id="123", head_sha="abc")
        with self.assertRaises(SystemExit):
            cli.cmd_persist(args)

    def test_merge_succeeds_on_a_valid_matching_pair(self):
        claude = _artifact(artifact_id="analysis:anthropic", provider="anthropic")
        gpt = _artifact(artifact_id="analysis:openai", provider="openai")
        self._write(self.claude_path, claude)
        self._write(self.gpt_path, gpt)
        args = argparse.Namespace(claude_artifact=self.claude_path, gpt_artifact=self.gpt_path,
                                   ledger_out=self.ledger_path)
        cli.cmd_merge(args)  # must not raise
        self.assertTrue(os.path.exists(self.ledger_path))


class PersistSubcommandTests(_TmpDirTestCase):
    def _write_valid_pair(self):
        claude = _artifact(artifact_id="analysis:anthropic", provider="anthropic")
        gpt = _artifact(artifact_id="analysis:openai", provider="openai")
        self._write(self.claude_path, claude)
        self._write(self.gpt_path, gpt)
        return claude, gpt

    def _args(self):
        return argparse.Namespace(claude_artifact=self.claude_path, gpt_artifact=self.gpt_path,
                                   ledger_out=self.ledger_path, manifest_out=self.manifest_path,
                                   workflow_run_id="32140963475", head_sha="95f2170abc")

    def test_persist_writes_both_artifacts_and_a_manifest(self):
        self._write_valid_pair()
        cli.cmd_persist(self._args())
        ledger = AnalysisLedger(self.ledger_path)
        self.assertEqual(ledger.known_count, 2)
        manifest_ledger = RunManifestLedger(self.manifest_path)
        self.assertEqual(manifest_ledger.known_count, 1)

    def test_persist_is_idempotent_on_rerun(self):
        """Task §6/§9: a retry of the same run must not duplicate
        content - append-only, idempotent by artifact_id/manifest_id."""
        self._write_valid_pair()
        cli.cmd_persist(self._args())
        cli.cmd_persist(self._args())
        with open(self.ledger_path, encoding="utf-8") as f:
            ledger_lines = [l for l in f if l.strip()]
        with open(self.manifest_path, encoding="utf-8") as f:
            manifest_lines = [l for l in f if l.strip()]
        self.assertEqual(len(ledger_lines), 2)
        self.assertEqual(len(manifest_lines), 1)

    def test_persist_never_dedupes_the_two_providers_into_one_line(self):
        self._write_valid_pair()
        cli.cmd_persist(self._args())
        with open(self.ledger_path, encoding="utf-8") as f:
            rows = [json.loads(l) for l in f if l.strip()]
        providers = {r["provider"] for r in rows}
        self.assertEqual(providers, {"anthropic", "openai"})

    def test_manifest_records_workflow_run_id_and_head_sha(self):
        self._write_valid_pair()
        cli.cmd_persist(self._args())
        with open(self.manifest_path, encoding="utf-8") as f:
            row = json.loads(f.readline())
        self.assertEqual(row["workflow_run_id"], "32140963475")
        self.assertEqual(row["head_sha"], "95f2170abc")

    def test_persist_never_calls_git(self):
        """persist writes local files only - the calling workflow step
        owns git add/commit/push, never this script. Checked against the
        code body only (docstrings legitimately mention git in prose
        explaining that ownership split)."""
        import ast
        import inspect
        source = inspect.getsource(cli.cmd_persist)
        tree = ast.parse(source)
        func_node = tree.body[0]
        body_without_docstring = func_node.body[1:] if (
            func_node.body and isinstance(func_node.body[0], ast.Expr)
            and isinstance(func_node.body[0].value, ast.Constant)
        ) else func_node.body
        code_only = ast.unparse(ast.Module(body=body_without_docstring, type_ignores=[]))
        for needle in ("subprocess", "os.system", "git.", "'git", '"git'):
            self.assertNotIn(needle, code_only)


if __name__ == "__main__":
    unittest.main()
