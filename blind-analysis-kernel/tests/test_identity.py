import _pathsetup  # noqa: F401
import unittest

from blind_analysis_kernel.identity import default_run_id, make_analysis_artifact_id


class MakeAnalysisArtifactIdTests(unittest.TestCase):
    def test_deterministic_for_same_run_id_and_provider(self):
        a = make_analysis_artifact_id("run-1", "anthropic")
        b = make_analysis_artifact_id("run-1", "anthropic")
        self.assertEqual(a, b)

    def test_different_providers_same_run_id_produce_different_ids(self):
        """The core blindness-adjacent guarantee: two providers analyzing
        the same run never collide into one artifact."""
        claude_id = make_analysis_artifact_id("run-1", "anthropic")
        gpt_id = make_analysis_artifact_id("run-1", "openai")
        self.assertNotEqual(claude_id, gpt_id)

    def test_different_run_ids_same_provider_produce_different_ids(self):
        """A rerun (task §9) always gets a new artifact_id, never
        silently overwriting the prior run's artifact for that provider."""
        run1 = make_analysis_artifact_id("run-1", "anthropic")
        run2 = make_analysis_artifact_id("run-2", "anthropic")
        self.assertNotEqual(run1, run2)

    def test_artifact_id_has_stable_prefix(self):
        self.assertTrue(make_analysis_artifact_id("run-1", "anthropic").startswith("analysis:"))

    def test_case_ids_are_not_part_of_the_hash_material(self):
        """No source_case_ids parameter exists - identity here must not
        depend on which case was analyzed, only on (run_id, provider)."""
        import inspect
        params = list(inspect.signature(make_analysis_artifact_id).parameters)
        self.assertEqual(params, ["run_id", "provider"])


class DefaultRunIdTests(unittest.TestCase):
    def test_two_calls_produce_different_ids(self):
        self.assertNotEqual(default_run_id(), default_run_id())

    def test_returns_a_nonempty_string(self):
        run_id = default_run_id()
        self.assertIsInstance(run_id, str)
        self.assertTrue(run_id)


if __name__ == "__main__":
    unittest.main()
