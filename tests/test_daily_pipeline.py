"""Offline, deterministic tests for run_daily_pipeline.py's orchestration
logic: ordering, failure gating, and idempotency. The real Constraint
Archaeology scan makes network and model calls, so `ca_cmd` is always a
small stand-in subprocess here (matching CLAUDE.md's "no network, no
model calls in tests"); Business Candidate Analyst has no such dependency
and is invoked for real, against the small fixtures already committed
under business-candidate-analyst/tests/fixtures/, to prove the wiring
itself - not just each stage in isolation.
"""

import hashlib
import json
import os
import shutil
import sys
import tempfile
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
_BCA_SRC = os.path.join(_ROOT, "business-candidate-analyst", "src")
if _BCA_SRC not in sys.path:
    sys.path.insert(0, _BCA_SRC)

from run_daily_pipeline import run_pipeline  # noqa: E402

_BCA_FIXTURES = os.path.join(_ROOT, "business-candidate-analyst", "tests", "fixtures")
_BCA_RUNNER = os.path.join(_ROOT, "business-candidate-analyst", "run_business_candidate_analyst.py")

_CA_SUCCESS_CMD = [sys.executable, "-c", "import sys; sys.exit(0)"]
_CA_FAILURE_CMD = [sys.executable, "-c", "import sys; sys.exit(1)"]


def _bca_cmd(ca_data_dir, bca_data_dir, reports_dir, skip_mode_b=True):
    cmd = [sys.executable, _BCA_RUNNER,
           "--ca-data-dir", ca_data_dir, "--data-dir", bca_data_dir, "--reports-dir", reports_dir]
    if skip_mode_b:
        cmd.append("--skip-mode-b")
    return cmd


def _marker_bca_cmd(marker_path):
    """A stand-in BCA command whose only effect is writing a marker file -
    used only to prove whether BCA ran at all, not what it produced."""
    return [sys.executable, "-c", f"open({marker_path!r}, 'w').write('ran')"]


def _hash_dir(path):
    digest = hashlib.sha256()
    for name in sorted(os.listdir(path)):
        with open(os.path.join(path, name), "rb") as f:
            digest.update(name.encode()); digest.update(f.read())
    return digest.hexdigest()


class OrderingAndFailureGatingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_bca_runs_only_after_ca_succeeds(self):
        marker = os.path.join(self.tmp, "bca_ran.marker")
        result = run_pipeline(_CA_SUCCESS_CMD, _marker_bca_cmd(marker), self.tmp)
        self.assertEqual(result["status"], "OK")
        self.assertTrue(os.path.exists(marker), "BCA must run when CA succeeds")

    def test_failed_ca_prevents_bca_execution(self):
        marker = os.path.join(self.tmp, "bca_ran.marker")
        result = run_pipeline(_CA_FAILURE_CMD, _marker_bca_cmd(marker), self.tmp)
        self.assertEqual(result["status"], "CA_FAILED")
        self.assertIsNone(result["bca"])
        self.assertFalse(os.path.exists(marker), "BCA must never run when CA failed")

    def test_pipeline_status_artifact_is_persisted_on_both_outcomes(self):
        for ca_cmd, expected_status in [(_CA_SUCCESS_CMD, "OK"), (_CA_FAILURE_CMD, "CA_FAILED")]:
            with self.subTest(ca_cmd=ca_cmd):
                status_dir = tempfile.mkdtemp()
                try:
                    marker = os.path.join(status_dir, "marker")
                    result = run_pipeline(ca_cmd, _marker_bca_cmd(marker), status_dir)
                    self.assertTrue(os.path.exists(result["status_path"]))
                    with open(result["status_path"]) as f:
                        persisted = json.load(f)
                    self.assertEqual(persisted["status"], expected_status)
                finally:
                    shutil.rmtree(status_dir, ignore_errors=True)


class BcaFailureIsolationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.ca_dir = os.path.join(self.tmp, "ca_data")
        shutil.copytree(os.path.join(_BCA_FIXTURES, "ca_renumber_day1"), self.ca_dir)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_bca_failure_does_not_corrupt_ca_outputs(self):
        before = _hash_dir(self.ca_dir)

        # --data-dir points at a path that is a FILE, not a directory, so
        # registry.py's append() (which os.makedirs's its dirname then
        # opens the events file) fails - a genuine BCA-side crash, not a
        # simulated one.
        bogus_data_dir = os.path.join(self.tmp, "not_a_directory")
        with open(bogus_data_dir, "w") as f:
            f.write("x")
        reports_dir = os.path.join(self.tmp, "reports")

        result = run_pipeline(_CA_SUCCESS_CMD,
                               _bca_cmd(self.ca_dir, os.path.join(bogus_data_dir, "sub"), reports_dir),
                               self.tmp)
        self.assertEqual(result["status"], "BCA_FAILED")
        self.assertNotEqual(result["bca"]["returncode"], 0)

        after = _hash_dir(self.ca_dir)
        self.assertEqual(before, after, "a BCA-side crash must never modify CA's own data files")


class IdempotencyThroughOrchestratorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.ca_dir = os.path.join(self.tmp, "ca_data")
        shutil.copytree(os.path.join(_BCA_FIXTURES, "ca_renumber_day1"), self.ca_dir)
        self.bca_data_dir = os.path.join(self.tmp, "bca_data")
        self.reports_dir = os.path.join(self.tmp, "reports")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_rerunning_same_daily_corpus_creates_zero_duplicate_events(self):
        cmd = _bca_cmd(self.ca_dir, self.bca_data_dir, self.reports_dir)

        first = run_pipeline(_CA_SUCCESS_CMD, cmd, self.tmp)
        self.assertEqual(first["status"], "OK")
        first_events = first["bca"]["summary"]["mode_a"]["events_appended"]
        self.assertGreater(first_events, 0, "sanity: first run must actually create the candidate")

        second = run_pipeline(_CA_SUCCESS_CMD, cmd, self.tmp)
        self.assertEqual(second["status"], "OK")
        second_events = second["bca"]["summary"]["mode_a"]["events_appended"]
        self.assertEqual(second_events, 0, "rerunning the identical daily corpus must create 0 new events")


class MaterialEventArtifactThroughOrchestratorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.bca_data_dir = os.path.join(self.tmp, "bca_data")
        self.reports_dir = os.path.join(self.tmp, "reports")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _material_events(self, ca_data_dir):
        cmd = _bca_cmd(ca_data_dir, self.bca_data_dir, self.reports_dir)
        result = run_pipeline(_CA_SUCCESS_CMD, cmd, self.tmp)
        self.assertEqual(result["status"], "OK")
        material_path = result["bca"]["summary"]["material_events_path"]
        with open(material_path) as f:
            return json.load(f)

    def test_normal_watch_creation_produces_no_material_events(self):
        material = self._material_events(os.path.join(_BCA_FIXTURES, "ca_accum_day1"))
        self.assertEqual(material, [], "a plain WATCH-level day must produce zero material events")

    def test_watch_to_validating_produces_a_material_event(self):
        self._material_events(os.path.join(_BCA_FIXTURES, "ca_accum_day1"))
        material = self._material_events(os.path.join(_BCA_FIXTURES, "ca_accum_day2"))
        escalations = [m for m in material if m["material_type"] == "lifecycle_escalation"]
        self.assertEqual(len(escalations), 1)
        self.assertEqual(escalations[0]["from_state"], "WATCH")
        self.assertEqual(escalations[0]["to_state"], "VALIDATING")


class ThroughOrchestratorSafetyInvariantTests(unittest.TestCase):
    """Re-proves, through the actual wired orchestrator subprocess path
    (not just in-process calls to run_analysis), the two invariants the
    daily pipeline must never regress: cross-mode isolation and stable
    observation_id-based identity across a CA renumbering."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.bca_data_dir = os.path.join(self.tmp, "bca_data")
        self.reports_dir = os.path.join(self.tmp, "reports")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_no_cross_mode_contamination_through_orchestrator(self):
        ca_dir = os.path.join(_BCA_FIXTURES, "ca_rearch_run1")
        cmd = _bca_cmd(ca_dir, self.bca_data_dir, self.reports_dir, skip_mode_b=False)
        result = run_pipeline(_CA_SUCCESS_CMD, cmd, self.tmp)
        self.assertEqual(result["status"], "OK")
        summary = result["bca"]["summary"]
        self.assertIn("mode_a", summary)
        self.assertIn("mode_b", summary)
        self.assertGreater(summary["mode_a"]["candidates_total"], 0)
        self.assertGreater(summary["mode_b"]["candidates_total"], 0)

        from business_candidate_analyst.registry import CandidateRegistry, rebuild_snapshot  # noqa: E402
        events_path = os.path.join(self.bca_data_dir, "candidate_events.jsonl")
        candidates = rebuild_snapshot(CandidateRegistry(events_path).all_events())
        a_ids = {c.candidate_id for c in candidates if c.candidate_type == "NEW_MARKET"}
        b_ids = {c.candidate_id for c in candidates if c.candidate_type == "OLD_BUSINESS_REARCHITECTURE"}
        self.assertEqual(a_ids & b_ids, set())

    def test_observation_id_continuity_survives_ca_renumbering_through_orchestrator(self):
        day1 = os.path.join(_BCA_FIXTURES, "ca_renumber_day1")
        day2 = os.path.join(_BCA_FIXTURES, "ca_renumber_day2")

        r1 = run_pipeline(_CA_SUCCESS_CMD, _bca_cmd(day1, self.bca_data_dir, self.reports_dir), self.tmp)
        self.assertEqual(r1["status"], "OK")
        bc_x = None
        from business_candidate_analyst.registry import CandidateRegistry, rebuild_snapshot  # noqa: E402
        events_path = os.path.join(self.bca_data_dir, "candidate_events.jsonl")
        candidates = rebuild_snapshot(CandidateRegistry(events_path).all_events())
        self.assertEqual(len(candidates), 1)
        bc_x = candidates[0].candidate_id

        r2 = run_pipeline(_CA_SUCCESS_CMD, _bca_cmd(day2, self.bca_data_dir, self.reports_dir), self.tmp)
        self.assertEqual(r2["status"], "OK")
        candidates_after = rebuild_snapshot(CandidateRegistry(events_path).all_events())
        self.assertEqual(len(candidates_after), 1, "renumbering must not create a duplicate candidate")
        self.assertEqual(candidates_after[0].candidate_id, bc_x, "the original candidate_id must be reused")
        self.assertEqual(set(candidates_after[0].observation_ids), {"OBS-A", "OBS-B"})


if __name__ == "__main__":
    unittest.main()
