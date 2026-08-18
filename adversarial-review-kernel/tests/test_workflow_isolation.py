"""Static proof of the task's job-isolation requirements, parsing the
real workflow YAML. Mirrors
`blind-analysis-kernel/tests/test_workflow_isolation.py` exactly, adapted
to Stage 4's five jobs. PyYAML is used here as a TEST-only, offline,
static-analysis dependency - not a runtime dependency of any library
code in this repo.
"""

import _pathsetup  # noqa: F401
import unittest
from pathlib import Path

try:
    import yaml
    _HAVE_YAML = True
except ImportError:
    _HAVE_YAML = False

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "stage4-adversarial-review.yml"


@unittest.skipUnless(_HAVE_YAML, "PyYAML not installed - offline test-only dependency, skip rather than fail")
@unittest.skipUnless(WORKFLOW_PATH.exists(), f"{WORKFLOW_PATH} not present")
class WorkflowIsolationTests(unittest.TestCase):
    def setUp(self):
        with open(WORKFLOW_PATH, encoding="utf-8") as f:
            self.workflow = yaml.safe_load(f)
        self.jobs = self.workflow["jobs"]

    def _needs(self, job_name: str) -> list:
        needs = self.jobs[job_name].get("needs", [])
        return [needs] if isinstance(needs, str) else list(needs)

    def test_workflow_is_manual_dispatch_only(self):
        trigger = self.workflow.get("on") or self.workflow.get(True)
        self.assertIn("workflow_dispatch", trigger)
        self.assertNotIn("schedule", trigger, "task instructions: do NOT schedule this workflow yet")

    def test_all_five_jobs_present(self):
        self.assertEqual(
            set(self.jobs.keys()),
            {"select-disagreements", "claude-falsify", "gpt-falsify", "deterministic-judge", "persist-to-git"},
        )

    def test_run_id_input_defaults_to_the_real_persisted_run(self):
        inputs = self.workflow.get("on", self.workflow.get(True))["workflow_dispatch"]["inputs"]
        self.assertEqual(inputs["run_id"]["default"], "32142997999")

    def test_claude_falsify_does_not_depend_on_gpt_falsify(self):
        self.assertNotIn("gpt-falsify", self._needs("claude-falsify"))

    def test_gpt_falsify_does_not_depend_on_claude_falsify(self):
        self.assertNotIn("claude-falsify", self._needs("gpt-falsify"))

    def test_both_falsify_jobs_depend_only_on_select_disagreements(self):
        self.assertEqual(self._needs("claude-falsify"), ["select-disagreements"])
        self.assertEqual(self._needs("gpt-falsify"), ["select-disagreements"])

    def test_judge_job_depends_on_both_falsify_jobs(self):
        needs = set(self._needs("deterministic-judge"))
        self.assertEqual(needs, {"claude-falsify", "gpt-falsify"})

    def test_judge_job_is_the_only_one_that_needs_both(self):
        for job_name in ("select-disagreements", "claude-falsify", "gpt-falsify"):
            needs = set(self._needs(job_name))
            self.assertFalse({"claude-falsify", "gpt-falsify"}.issubset(needs))

    def test_no_job_uses_actions_cache_for_model_output(self):
        for job_name, job in self.jobs.items():
            for step in job.get("steps", []):
                uses = step.get("uses", "")
                self.assertNotIn("actions/cache", uses, f"{job_name} uses actions/cache - forbidden")

    def test_falsify_jobs_upload_their_own_artifact_only(self):
        for job_name, expected_artifact in (("claude-falsify", "claude-falsification"),
                                             ("gpt-falsify", "gpt-falsification")):
            uploads = [step["with"]["name"] for step in self.jobs[job_name].get("steps", [])
                       if step.get("uses", "").startswith("actions/upload-artifact") and "with" in step]
            self.assertEqual(uploads, [expected_artifact])

    def test_falsify_jobs_never_download_each_others_artifact(self):
        for job_name, forbidden_artifact in (("claude-falsify", "gpt-falsification"),
                                              ("gpt-falsify", "claude-falsification")):
            downloads = [step.get("with", {}).get("name") for step in self.jobs[job_name].get("steps", [])
                         if step.get("uses", "").startswith("actions/download-artifact")]
            self.assertNotIn(forbidden_artifact, downloads)

    def test_judge_job_downloads_both_falsification_artifacts(self):
        downloads = [step.get("with", {}).get("name") for step in self.jobs["deterministic-judge"].get("steps", [])
                     if step.get("uses", "").startswith("actions/download-artifact")]
        self.assertEqual(set(downloads), {"disagreement-inputs", "claude-falsification", "gpt-falsification"})

    def test_claude_falsify_uses_anthropic_secret_only(self):
        env_names = self._job_run_step_env_keys("claude-falsify")
        self.assertIn("ANTHROPIC_API_KEY", env_names)
        self.assertNotIn("OPENAI_API_KEY", env_names)

    def test_gpt_falsify_uses_openai_secret_only(self):
        env_names = self._job_run_step_env_keys("gpt-falsify")
        self.assertIn("OPENAI_API_KEY", env_names)
        self.assertNotIn("ANTHROPIC_API_KEY", env_names)

    def _job_run_step_env_keys(self, job_name: str) -> set:
        keys = set()
        for step in self.jobs[job_name].get("steps", []):
            keys.update(step.get("env", {}).keys())
        return keys

    def test_missing_secret_causes_hard_failure_not_a_fallback(self):
        for job_name in ("claude-falsify", "gpt-falsify"):
            run_texts = [step.get("run", "") for step in self.jobs[job_name].get("steps", [])]
            combined = "\n".join(run_texts)
            self.assertIn("exit 1", combined)

    def test_no_step_prints_a_secret_value_directly(self):
        for job_name, job in self.jobs.items():
            for step in job.get("steps", []):
                run_text = step.get("run", "")
                self.assertNotIn("echo $ANTHROPIC_API_KEY", run_text)
                self.assertNotIn("echo $OPENAI_API_KEY", run_text)
                self.assertNotIn("echo \"${{ secrets.ANTHROPIC_API_KEY }}\"", run_text)
                self.assertNotIn("echo \"${{ secrets.OPENAI_API_KEY }}\"", run_text)

    def test_deterministic_judge_job_never_touches_a_model_secret(self):
        """Task §7: the deterministic judge itself makes no model call -
        its own job step must not even reference a provider secret."""
        env_names = self._job_run_step_env_keys("deterministic-judge")
        self.assertNotIn("ANTHROPIC_API_KEY", env_names)
        self.assertNotIn("OPENAI_API_KEY", env_names)
        run_text = "\n".join(step.get("run", "") for step in self.jobs["deterministic-judge"].get("steps", []))
        self.assertNotIn("ANTHROPIC_API_KEY", run_text)
        self.assertNotIn("OPENAI_API_KEY", run_text)


@unittest.skipUnless(_HAVE_YAML, "PyYAML not installed - offline test-only dependency, skip rather than fail")
@unittest.skipUnless(WORKFLOW_PATH.exists(), f"{WORKFLOW_PATH} not present")
class PersistToGitWriteBoundaryTests(unittest.TestCase):
    """Only persist-to-git may write to Git, only after
    deterministic-judge, with bounded retry, no force push, and a hard
    failure on any persistence error."""

    def setUp(self):
        with open(WORKFLOW_PATH, encoding="utf-8") as f:
            self.workflow = yaml.safe_load(f)
        self.jobs = self.workflow["jobs"]

    def _needs(self, job_name: str) -> list:
        needs = self.jobs[job_name].get("needs", [])
        return [needs] if isinstance(needs, str) else list(needs)

    def _run_text(self, job_name: str) -> str:
        return "\n".join(step.get("run", "") for step in self.jobs[job_name].get("steps", []))

    def test_persist_to_git_depends_on_deterministic_judge(self):
        self.assertEqual(self._needs("persist-to-git"), ["deterministic-judge"])

    def test_only_persist_to_git_has_contents_write(self):
        for job_name, job in self.jobs.items():
            permissions = job.get("permissions", {})
            if job_name == "persist-to-git":
                self.assertEqual(permissions.get("contents"), "write")
            else:
                self.assertEqual(permissions.get("contents"), "read",
                                  f"{job_name} must declare contents: read explicitly")

    def test_only_persist_to_git_job_contains_a_git_push(self):
        for job_name in self.jobs:
            run_text = self._run_text(job_name)
            if job_name == "persist-to-git":
                self.assertIn("git push", run_text)
            else:
                self.assertNotIn("git push", run_text,
                                  f"{job_name} must never push to git - only persist-to-git may")

    def test_model_jobs_have_no_write_permission_and_no_git_write_calls(self):
        for job_name in ("select-disagreements", "claude-falsify", "gpt-falsify", "deterministic-judge"):
            self.assertEqual(self.jobs[job_name].get("permissions", {}).get("contents"), "read")
            run_text = self._run_text(job_name)
            for forbidden in ("git push", "git commit", "git add"):
                self.assertNotIn(forbidden, run_text, f"{job_name} must never touch git")

    def test_persist_to_git_job_has_no_model_secrets(self):
        job = self.jobs["persist-to-git"]
        env_names = set()
        for step in job.get("steps", []):
            env_names.update(step.get("env", {}).keys())
        self.assertNotIn("ANTHROPIC_API_KEY", env_names)
        self.assertNotIn("OPENAI_API_KEY", env_names)

    def test_persist_to_git_has_a_concurrency_group_with_cancel_in_progress_false(self):
        concurrency = self.jobs["persist-to-git"].get("concurrency", {})
        self.assertTrue(concurrency.get("group"))
        self.assertIs(concurrency.get("cancel-in-progress"), False)

    def test_persist_to_git_never_force_pushes(self):
        run_text = self._run_text("persist-to-git")
        self.assertNotIn("--force", run_text)
        self.assertNotIn("-f ", run_text)
        self.assertNotIn("push --force", run_text)

    def test_persist_to_git_pulls_before_retrying_push(self):
        run_text = self._run_text("persist-to-git")
        self.assertIn("git pull --rebase", run_text)

    def test_persist_to_git_retry_is_bounded(self):
        run_text = self._run_text("persist-to-git")
        self.assertIn("max_attempts", run_text)

    def test_persist_to_git_fails_the_job_when_push_exhausts_retries(self):
        run_text = self._run_text("persist-to-git")
        self.assertIn("exit 1", run_text)

    def test_persist_to_git_calls_the_persist_subcommand_not_judge(self):
        run_text = self._run_text("persist-to-git")
        self.assertIn("run_stage4_job.py persist", run_text)
        self.assertNotIn("run_stage4_job.py judge", run_text)

    def test_persist_to_git_only_stages_the_designated_knowledge_paths(self):
        run_text = self._run_text("persist-to-git")
        self.assertIn("git add adversarial-review-kernel/data/falsifications.jsonl "
                       "adversarial-review-kernel/data/judgments.jsonl", run_text)


if __name__ == "__main__":
    unittest.main()
