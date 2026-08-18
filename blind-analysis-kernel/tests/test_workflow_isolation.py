"""Static proof of task §4/§7's job-isolation requirements, parsing the
real workflow YAML. PyYAML is used here as a TEST-only, offline,
static-analysis dependency (already present in this environment) - not a
runtime dependency of any library code in this repo, the same distinction
`constraint_change_observatory/tests/test_safety.py`'s own "no YAML
parser dependency" rule is actually protecting against (a parser in the
*intake* path, not in a test).
"""

import _pathsetup  # noqa: F401
import os
import unittest
from pathlib import Path

try:
    import yaml
    _HAVE_YAML = True
except ImportError:
    _HAVE_YAML = False

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "stage3-blind-dispatch.yml"


@unittest.skipUnless(_HAVE_YAML, "PyYAML not installed - offline test-only dependency, skip rather than fail")
@unittest.skipUnless(WORKFLOW_PATH.exists(), f"{WORKFLOW_PATH} not present")
class WorkflowIsolationTests(unittest.TestCase):
    def setUp(self):
        with open(WORKFLOW_PATH, encoding="utf-8") as f:
            self.workflow = yaml.safe_load(f)
        # PyYAML parses the bare key `on:` as the boolean True in YAML
        # 1.1 mode - look it up either way rather than assume which.
        self.jobs = self.workflow["jobs"]

    def _needs(self, job_name: str) -> list:
        needs = self.jobs[job_name].get("needs", [])
        return [needs] if isinstance(needs, str) else list(needs)

    def test_workflow_is_manual_dispatch_only(self):
        trigger = self.workflow.get("on") or self.workflow.get(True)
        self.assertIn("workflow_dispatch", trigger)
        self.assertNotIn("schedule", trigger, "task instructions: do NOT schedule this workflow yet")

    def test_all_four_jobs_present(self):
        self.assertEqual(set(self.jobs.keys()),
                          {"prepare-input", "claude-analysis", "gpt-analysis", "merge-reveal"})

    def test_claude_analysis_does_not_depend_on_gpt_analysis(self):
        self.assertNotIn("gpt-analysis", self._needs("claude-analysis"))

    def test_gpt_analysis_does_not_depend_on_claude_analysis(self):
        self.assertNotIn("claude-analysis", self._needs("gpt-analysis"))

    def test_both_analysis_jobs_depend_only_on_prepare_input(self):
        self.assertEqual(self._needs("claude-analysis"), ["prepare-input"])
        self.assertEqual(self._needs("gpt-analysis"), ["prepare-input"])

    def test_merge_job_depends_on_both_analysis_jobs(self):
        needs = set(self._needs("merge-reveal"))
        self.assertEqual(needs, {"claude-analysis", "gpt-analysis"})

    def test_merge_job_is_the_only_one_that_needs_both(self):
        for job_name in ("prepare-input", "claude-analysis", "gpt-analysis"):
            needs = set(self._needs(job_name))
            self.assertFalse({"claude-analysis", "gpt-analysis"}.issubset(needs) and job_name != "merge-reveal")

    def test_no_job_uses_actions_cache_for_model_output(self):
        """Task §4: 'Do not use cache for model outputs.'"""
        for job_name, job in self.jobs.items():
            for step in job.get("steps", []):
                uses = step.get("uses", "")
                self.assertNotIn("actions/cache", uses, f"{job_name} uses actions/cache - forbidden by task §4")

    def test_analysis_jobs_upload_their_own_artifact_only(self):
        """Isolated handoff via workflow artifacts, not a shared mutable
        file - each analysis job uploads exactly its own named artifact."""
        for job_name, expected_artifact in (("claude-analysis", "claude-analysis"),
                                             ("gpt-analysis", "gpt-analysis")):
            uploads = [step["with"]["name"] for step in self.jobs[job_name].get("steps", [])
                       if step.get("uses", "").startswith("actions/upload-artifact") and "with" in step]
            self.assertEqual(uploads, [expected_artifact])

    def test_analysis_jobs_never_download_each_others_artifact(self):
        for job_name, forbidden_artifact in (("claude-analysis", "gpt-analysis"),
                                              ("gpt-analysis", "claude-analysis")):
            downloads = [step.get("with", {}).get("name") for step in self.jobs[job_name].get("steps", [])
                         if step.get("uses", "").startswith("actions/download-artifact")]
            self.assertNotIn(forbidden_artifact, downloads)

    def test_merge_job_downloads_both_analysis_artifacts(self):
        downloads = [step.get("with", {}).get("name") for step in self.jobs["merge-reveal"].get("steps", [])
                     if step.get("uses", "").startswith("actions/download-artifact")]
        self.assertEqual(set(downloads), {"claude-analysis", "gpt-analysis"})

    def test_claude_job_uses_anthropic_secret_only(self):
        env_names = self._job_run_step_env_keys("claude-analysis")
        self.assertIn("ANTHROPIC_API_KEY", env_names)
        self.assertNotIn("OPENAI_API_KEY", env_names)

    def test_gpt_job_uses_openai_secret_only(self):
        env_names = self._job_run_step_env_keys("gpt-analysis")
        self.assertIn("OPENAI_API_KEY", env_names)
        self.assertNotIn("ANTHROPIC_API_KEY", env_names)

    def _job_run_step_env_keys(self, job_name: str) -> set:
        keys = set()
        for step in self.jobs[job_name].get("steps", []):
            keys.update(step.get("env", {}).keys())
        return keys

    def test_missing_secret_causes_hard_failure_not_a_fallback(self):
        """Task §5: a missing secret must fail the job loudly - checked
        here as a literal `exit 1` guard in each analysis job's run step,
        not merely documented."""
        for job_name in ("claude-analysis", "gpt-analysis"):
            run_texts = [step.get("run", "") for step in self.jobs[job_name].get("steps", [])]
            combined = "\n".join(run_texts)
            self.assertIn("exit 1", combined)

    def test_no_step_prints_a_secret_value_directly(self):
        """Best-effort static guard: no run step should ever echo the
        secret context expression itself into a log line."""
        for job_name, job in self.jobs.items():
            for step in job.get("steps", []):
                run_text = step.get("run", "")
                self.assertNotIn("echo $ANTHROPIC_API_KEY", run_text)
                self.assertNotIn("echo $OPENAI_API_KEY", run_text)
                self.assertNotIn("echo \"${{ secrets.ANTHROPIC_API_KEY }}\"", run_text)
                self.assertNotIn("echo \"${{ secrets.OPENAI_API_KEY }}\"", run_text)


if __name__ == "__main__":
    unittest.main()
