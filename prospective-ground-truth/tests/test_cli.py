"""CLI-level tests for run_prospective_ground_truth.py's register/resolve/
report subcommands. Task Sec 14: 'Resolution references existing
prospective case' is enforced here, at the CLI layer, since
CaseLedger/ResolutionLedger are deliberately independent at the storage
layer (see test_ledger.py)."""

import _pathsetup  # noqa: F401
import json
import os
import sys
import tempfile
import unittest

_PKG_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PKG_ROOT not in sys.path:
    sys.path.insert(0, _PKG_ROOT)

import argparse  # noqa: E402

import run_prospective_ground_truth as cli  # noqa: E402


def _case_input(**overrides):
    base = {
        "domain": "permits",
        "proposition": "Will regulator X approve permit Y by 2026-09-15?",
        "decision_relevance": "Gates construction start.",
        "t0_cutoff": "2026-08-15",
        "t0_evidence": [{
            "artifact_id": "EV-1", "citation": "Official filing portal",
            "source_url": "https://example.gov/case/1", "captured_at": "2026-08-10",
            "quote_or_summary": "Application submitted, docket #1234.",
        }],
        "resolution_question": "Will regulator X approve permit Y?",
        "expected_resolution_window": {"earliest": "2026-09-01", "latest": "2026-09-30"},
        "resolution_sources_expected": ["regulator X official register"],
        "positive_condition": "Regulator publishes approval on or before 2026-09-30.",
        "negative_condition": "Regulator publishes refusal, or deadline passes with no approval.",
        "ambiguous_condition": "Deadline passes with no authoritative status available.",
        "created_at": "2026-08-15T00:00:00Z",
    }
    base.update(overrides)
    return base


def _resolution_input(prospective_case_id, **overrides):
    base = {
        "prospective_case_id": prospective_case_id,
        "resolved_at": "2026-09-10",
        "outcome": "POSITIVE",
        "t1_evidence_artifact_ids": ["EV-T1-1"],
        "authoritative_source_type": "regulator official publication",
        "resolution_rationale": "Regulator X published approval notice #5678 on 2026-09-10.",
        "resolver_type": "human",
        "created_at": "2026-09-10T00:00:00Z",
    }
    base.update(overrides)
    return base


class _TmpDirTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cases_path = os.path.join(self._tmp.name, "cases.jsonl")
        self.resolutions_path = os.path.join(self._tmp.name, "resolutions.jsonl")
        self.snapshot_path = os.path.join(self._tmp.name, "cases.json")
        self.input_path = os.path.join(self._tmp.name, "input.json")

    def tearDown(self):
        self._tmp.cleanup()

    def _write_input(self, data):
        with open(self.input_path, "w", encoding="utf-8") as f:
            json.dump(data, f)


class RegisterCommandTests(_TmpDirTestCase):
    def test_register_writes_case_and_snapshot(self):
        self._write_input(_case_input())
        args = argparse.Namespace(input=self.input_path, cases_ledger=self.cases_path,
                                   resolutions_ledger=self.resolutions_path, snapshot_out=self.snapshot_path)
        cli.cmd_register(args)
        self.assertTrue(os.path.exists(self.cases_path))
        self.assertTrue(os.path.exists(self.snapshot_path))
        with open(self.snapshot_path, encoding="utf-8") as f:
            snapshot = json.load(f)
        self.assertEqual(len(snapshot["cases"]), 1)
        self.assertEqual(snapshot["cases"][0]["status"], "OPEN")

    def test_register_is_idempotent_on_rerun(self):
        self._write_input(_case_input())
        args = argparse.Namespace(input=self.input_path, cases_ledger=self.cases_path,
                                   resolutions_ledger=self.resolutions_path, snapshot_out=self.snapshot_path)
        cli.cmd_register(args)
        cli.cmd_register(args)
        with open(self.cases_path, encoding="utf-8") as f:
            self.assertEqual(len([l for l in f if l.strip()]), 1)

    def test_register_refuses_post_t0_evidence(self):
        bad = _case_input()
        bad["t0_evidence"][0]["captured_at"] = "2026-08-20"  # after t0_cutoff 2026-08-15
        self._write_input(bad)
        args = argparse.Namespace(input=self.input_path, cases_ledger=self.cases_path,
                                   resolutions_ledger=self.resolutions_path, snapshot_out=self.snapshot_path)
        with self.assertRaises(SystemExit):
            cli.cmd_register(args)
        self.assertFalse(os.path.exists(self.cases_path))

    def test_register_refuses_blank_resolution_criteria(self):
        bad = _case_input(positive_condition="")
        self._write_input(bad)
        args = argparse.Namespace(input=self.input_path, cases_ledger=self.cases_path,
                                   resolutions_ledger=self.resolutions_path, snapshot_out=self.snapshot_path)
        with self.assertRaises(SystemExit):
            cli.cmd_register(args)


class ResolveCommandTests(_TmpDirTestCase):
    def _register(self):
        self._write_input(_case_input())
        args = argparse.Namespace(input=self.input_path, cases_ledger=self.cases_path,
                                   resolutions_ledger=self.resolutions_path, snapshot_out=self.snapshot_path)
        cli.cmd_register(args)
        with open(self.cases_path, encoding="utf-8") as f:
            return json.loads(f.readline())["prospective_case_id"]

    def test_resolve_refuses_unregistered_case(self):
        self._write_input(_resolution_input("pgt-case:doesnotexist"))
        args = argparse.Namespace(input=self.input_path, cases_ledger=self.cases_path,
                                   resolutions_ledger=self.resolutions_path, snapshot_out=self.snapshot_path)
        with self.assertRaises(SystemExit):
            cli.cmd_resolve(args)
        self.assertFalse(os.path.exists(self.resolutions_path))

    def test_resolve_succeeds_for_a_registered_case_and_updates_snapshot_status(self):
        case_id = self._register()
        self._write_input(_resolution_input(case_id))
        args = argparse.Namespace(input=self.input_path, cases_ledger=self.cases_path,
                                   resolutions_ledger=self.resolutions_path, snapshot_out=self.snapshot_path)
        cli.cmd_resolve(args)
        with open(self.snapshot_path, encoding="utf-8") as f:
            snapshot = json.load(f)
        self.assertEqual(snapshot["cases"][0]["status"], "RESOLVED")
        self.assertEqual(len(snapshot["resolutions"]), 1)

    def test_resolve_never_calls_a_model(self):
        """Task Sec 8/15: structural proof cmd_resolve contains no model
        client reference anywhere in its own source."""
        import inspect
        source = inspect.getsource(cli.cmd_resolve)
        for needle in ("anthropic", "openai", "call_claude", "call_openai", "ANTHROPIC_API_KEY", "OPENAI_API_KEY"):
            self.assertNotIn(needle, source)

    def test_case_t0_content_is_unchanged_after_resolution(self):
        case_id = self._register()
        with open(self.cases_path, encoding="utf-8") as f:
            before = f.read()
        self._write_input(_resolution_input(case_id))
        args = argparse.Namespace(input=self.input_path, cases_ledger=self.cases_path,
                                   resolutions_ledger=self.resolutions_path, snapshot_out=self.snapshot_path)
        cli.cmd_resolve(args)
        with open(self.cases_path, encoding="utf-8") as f:
            after = f.read()
        self.assertEqual(before, after)


class ReportCommandTests(_TmpDirTestCase):
    def test_report_on_empty_ledgers_returns_empty_snapshot(self):
        args = argparse.Namespace(cases_ledger=self.cases_path, resolutions_ledger=self.resolutions_path,
                                   as_of_date=None)
        cli.cmd_report(args)  # must not raise even with no ledger files on disk yet


if __name__ == "__main__":
    unittest.main()
