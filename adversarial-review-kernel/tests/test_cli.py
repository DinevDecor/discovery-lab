"""CLI-level tests for `run_stage4_job.py`'s `judge` and `persist`
subcommands - the structural-integrity gate (task §9-equivalent: refuse
to judge/persist a structurally broken pair) and `persist`'s idempotent,
append-only, no-git-call behavior. Mirrors
`blind-analysis-kernel/tests/test_cli_persist.py` exactly.
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

import run_stage4_job as cli  # noqa: E402
from adversarial_review_kernel.ledger import FalsificationLedger, JudgmentLedger  # noqa: E402
from adversarial_review_kernel.models import (  # noqa: E402
    FalsificationArtifact,
    FalsificationFinding,
    SCHEMA_AMBIGUITY,
)

_HASH = "d" * 64
CLAUDE_ID = "analysis:claude"
GPT_ID = "analysis:gpt"


def _analysis(artifact_id, provider, source_case_ids=None):
    return {
        "artifact_id": artifact_id,
        "run_id": "run-1",
        "provider": provider,
        "source_case_ids": source_case_ids or ["case:abc"],
        "analysis": {"carrier": "x"},
    }


def _finding(field="carrier", classification=SCHEMA_AMBIGUITY, target=GPT_ID, material=True):
    return FalsificationFinding(field=field, target_analysis_artifact_id=target,
                                 classification=classification, reason="r",
                                 source_artifact_ids=["OBS-1"], material=material)


def _falsification(critic_provider, target_artifact_id, input_packet_sha256=_HASH, findings=None):
    return FalsificationArtifact(
        artifact_id=f"falsification:{critic_provider}", run_id="run-1",
        critic_provider=critic_provider, critic_model="m",
        target_artifact_id=target_artifact_id, source_case_ids=["case:abc"],
        input_packet_sha256=input_packet_sha256,
        findings=findings or [_finding(target=target_artifact_id)],
        created_at="2026-08-18T00:00:00Z",
    )


class _TmpDirTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.claude_path = os.path.join(self._tmp.name, "claude.json")
        self.gpt_path = os.path.join(self._tmp.name, "gpt.json")
        self.disagreements_path = os.path.join(self._tmp.name, "disagreements.json")
        self.claude_fals_path = os.path.join(self._tmp.name, "claude_fals.json")
        self.gpt_fals_path = os.path.join(self._tmp.name, "gpt_fals.json")
        self.judgment_path = os.path.join(self._tmp.name, "judgment.json")
        self.fals_ledger_path = os.path.join(self._tmp.name, "falsifications.jsonl")
        self.judgment_ledger_path = os.path.join(self._tmp.name, "judgments.jsonl")

    def tearDown(self):
        self._tmp.cleanup()

    def _write_json(self, path, obj):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(obj, f)


class JudgeStructuralIntegrityGateTests(_TmpDirTestCase):
    def _write_analyses(self, claude_case_ids=None, gpt_case_ids=None):
        self._write_json(self.claude_path, _analysis(CLAUDE_ID, "anthropic", claude_case_ids))
        self._write_json(self.gpt_path, _analysis(GPT_ID, "openai", gpt_case_ids))

    def _judge_args(self):
        return argparse.Namespace(
            claude_artifact=self.claude_path, gpt_artifact=self.gpt_path,
            disagreements=self.disagreements_path,
            claude_falsification=self.claude_fals_path, gpt_falsification=self.gpt_fals_path,
            out=self.judgment_path,
        )

    def test_judge_refuses_mismatched_input_packet_sha256(self):
        self._write_analyses()
        self._write_json(self.disagreements_path, [])
        self._write_json(self.claude_fals_path, _falsification("anthropic", GPT_ID, "a" * 64).to_dict())
        self._write_json(self.gpt_fals_path, _falsification("openai", CLAUDE_ID, "b" * 64).to_dict())
        with self.assertRaises(SystemExit):
            cli.cmd_judge(self._judge_args())
        self.assertFalse(os.path.exists(self.judgment_path), "a mismatched pair must never be judged")

    def test_judge_refuses_claude_falsification_targeting_the_wrong_artifact(self):
        self._write_analyses()
        self._write_json(self.disagreements_path, [])
        self._write_json(self.claude_fals_path, _falsification("anthropic", CLAUDE_ID).to_dict())
        self._write_json(self.gpt_fals_path, _falsification("openai", CLAUDE_ID).to_dict())
        with self.assertRaises(SystemExit):
            cli.cmd_judge(self._judge_args())

    def test_judge_refuses_gpt_falsification_targeting_the_wrong_artifact(self):
        self._write_analyses()
        self._write_json(self.disagreements_path, [])
        self._write_json(self.claude_fals_path, _falsification("anthropic", GPT_ID).to_dict())
        self._write_json(self.gpt_fals_path, _falsification("openai", GPT_ID).to_dict())
        with self.assertRaises(SystemExit):
            cli.cmd_judge(self._judge_args())

    def test_judge_refuses_mismatched_source_case_ids(self):
        self._write_analyses(claude_case_ids=["case:a"], gpt_case_ids=["case:b"])
        self._write_json(self.disagreements_path, [])
        self._write_json(self.claude_fals_path, _falsification("anthropic", GPT_ID).to_dict())
        self._write_json(self.gpt_fals_path, _falsification("openai", CLAUDE_ID).to_dict())
        with self.assertRaises(SystemExit):
            cli.cmd_judge(self._judge_args())

    def test_judge_succeeds_on_a_valid_matching_pair(self):
        self._write_analyses()
        self._write_json(self.disagreements_path, [{
            "field": "carrier", "claude_value": "a", "gpt_value": "b",
            "claude_artifact_id": CLAUDE_ID, "gpt_artifact_id": GPT_ID,
        }])
        self._write_json(self.claude_fals_path, _falsification("anthropic", GPT_ID).to_dict())
        self._write_json(self.gpt_fals_path, _falsification("openai", CLAUDE_ID).to_dict())
        cli.cmd_judge(self._judge_args())  # must not raise
        self.assertTrue(os.path.exists(self.judgment_path))
        with open(self.judgment_path, encoding="utf-8") as f:
            judgment = json.load(f)
        self.assertEqual(judgment["status"], "WATCH")  # material SCHEMA_AMBIGUITY on carrier


class PersistSubcommandTests(_TmpDirTestCase):
    def _write_valid_falsifications_and_judgment(self):
        claude_fals = _falsification("anthropic", GPT_ID)
        gpt_fals = _falsification("openai", CLAUDE_ID)
        self._write_json(self.claude_fals_path, claude_fals.to_dict())
        self._write_json(self.gpt_fals_path, gpt_fals.to_dict())
        judgment = {
            "judgment_id": "judgment:run-1", "case_id": "case:abc", "source_run_id": "run-1",
            "source_analysis_artifact_ids": sorted([CLAUDE_ID, GPT_ID]),
            "source_falsification_artifact_ids": sorted([claude_fals.artifact_id, gpt_fals.artifact_id]),
            "status": "WATCH", "reasons": ["r"], "material_disagreements": [],
            "schema_ambiguities": ["carrier"], "created_at": "2026-08-18T00:00:00Z",
            "artifact_type": "judgment", "protocol_version": "0.1.0",
        }
        self._write_json(self.judgment_path, judgment)
        return claude_fals, gpt_fals

    def _args(self):
        return argparse.Namespace(
            claude_falsification=self.claude_fals_path, gpt_falsification=self.gpt_fals_path,
            judgment=self.judgment_path,
            falsification_ledger_out=self.fals_ledger_path, judgment_ledger_out=self.judgment_ledger_path,
        )

    def test_persist_writes_both_falsifications_and_the_judgment(self):
        self._write_valid_falsifications_and_judgment()
        cli.cmd_persist(self._args())
        fals_ledger = FalsificationLedger(self.fals_ledger_path)
        self.assertEqual(fals_ledger.known_count, 2)
        judgment_ledger = JudgmentLedger(self.judgment_ledger_path)
        self.assertEqual(judgment_ledger.known_count, 1)

    def test_persist_is_idempotent_on_rerun(self):
        self._write_valid_falsifications_and_judgment()
        cli.cmd_persist(self._args())
        cli.cmd_persist(self._args())
        with open(self.fals_ledger_path, encoding="utf-8") as f:
            fals_lines = [l for l in f if l.strip()]
        with open(self.judgment_ledger_path, encoding="utf-8") as f:
            judgment_lines = [l for l in f if l.strip()]
        self.assertEqual(len(fals_lines), 2)
        self.assertEqual(len(judgment_lines), 1)

    def test_persist_never_dedupes_the_two_critics_into_one_line(self):
        self._write_valid_falsifications_and_judgment()
        cli.cmd_persist(self._args())
        with open(self.fals_ledger_path, encoding="utf-8") as f:
            rows = [json.loads(l) for l in f if l.strip()]
        providers = {r["critic_provider"] for r in rows}
        self.assertEqual(providers, {"anthropic", "openai"})

    def test_persist_never_calls_git(self):
        """persist writes local files only - the calling workflow step
        owns git add/commit/push, never this script."""
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


class SelectAndDisagreeSubcommandTests(_TmpDirTestCase):
    def test_select_raises_when_run_id_has_no_matching_pair(self):
        analyses_path = os.path.join(self._tmp.name, "analyses.jsonl")
        with open(analyses_path, "w", encoding="utf-8") as f:
            f.write(json.dumps({"run_id": "other-run", "provider": "anthropic",
                                 "artifact_id": CLAUDE_ID, "source_case_ids": ["case:abc"]}) + "\n")
        args = argparse.Namespace(run_id="run-1", analyses_ledger=analyses_path,
                                   claude_out=self.claude_path, gpt_out=self.gpt_path)
        with self.assertRaises(SystemExit):
            cli.cmd_select(args)

    def test_select_finds_both_providers_for_a_real_matching_run_id(self):
        analyses_path = os.path.join(self._tmp.name, "analyses.jsonl")
        with open(analyses_path, "w", encoding="utf-8") as f:
            f.write(json.dumps({"run_id": "run-1", "provider": "anthropic",
                                 "artifact_id": CLAUDE_ID, "source_case_ids": ["case:abc"]}) + "\n")
            f.write(json.dumps({"run_id": "run-1", "provider": "openai",
                                 "artifact_id": GPT_ID, "source_case_ids": ["case:abc"]}) + "\n")
        args = argparse.Namespace(run_id="run-1", analyses_ledger=analyses_path,
                                   claude_out=self.claude_path, gpt_out=self.gpt_path)
        cli.cmd_select(args)  # must not raise
        self.assertTrue(os.path.exists(self.claude_path))
        self.assertTrue(os.path.exists(self.gpt_path))

    def test_disagree_writes_the_deterministic_diff(self):
        self._write_json(self.claude_path, {"artifact_id": CLAUDE_ID, "analysis": {"carrier": "a"}})
        self._write_json(self.gpt_path, {"artifact_id": GPT_ID, "analysis": {"carrier": "b"}})
        args = argparse.Namespace(claude_artifact=self.claude_path, gpt_artifact=self.gpt_path,
                                   out=self.disagreements_path)
        cli.cmd_disagree(args)
        with open(self.disagreements_path, encoding="utf-8") as f:
            rows = json.load(f)
        self.assertEqual([r["field"] for r in rows], ["carrier"])


if __name__ == "__main__":
    unittest.main()
