import _pathsetup  # noqa: F401
import unittest

from x_signal_probe import evaluator
from x_signal_probe.models import ProbeObservation


def _obs(classification, pid="1"):
    return ProbeObservation(
        source="x",
        post_id=pid,
        canonical_url=f"https://x.com/i/status/{pid}",
        created_at="",
        retrieved_at="",
        query_id="q1",
        query_family="f1",
        text_hash="h",
        probe_version="0.1",
        api_version="v2",
        classification=classification,
    )


class VerdictTests(unittest.TestCase):
    def test_insufficient_data_below_min_sample(self):
        obs = [_obs("candidate_incremental", str(i)) for i in range(5)]
        m = evaluator.evaluate_run(obs, posts_fetched=5, api_errors=0)
        self.assertEqual(m.automated_signal, "INSUFFICIENT_DATA")

    def test_pass_candidate_when_enough_incremental(self):
        obs = [_obs("candidate_incremental", str(i)) for i in range(5)]
        obs += [_obs("existing_source_duplicate", str(100 + i)) for i in range(25)]
        m = evaluator.evaluate_run(obs, posts_fetched=30, api_errors=0)
        self.assertEqual(m.automated_signal, "PASS_CANDIDATE")
        self.assertEqual(m.candidates_incremental, 5)

    def test_fail_candidate_when_mostly_duplicate(self):
        obs = [_obs("existing_source_duplicate", str(i)) for i in range(29)]
        obs += [_obs("candidate_incremental", "x")]
        m = evaluator.evaluate_run(obs, posts_fetched=30, api_errors=0)
        self.assertEqual(m.automated_signal, "FAIL_CANDIDATE")

    def test_verdict_is_never_a_final_pass_or_fail_label(self):
        obs = [_obs("candidate_incremental", str(i)) for i in range(10)]
        m = evaluator.evaluate_run(obs, posts_fetched=30, api_errors=0)
        self.assertIn(m.automated_signal, {"PASS_CANDIDATE", "FAIL_CANDIDATE", "INSUFFICIENT_DATA"})
        self.assertNotIn(m.automated_signal, {"PASS", "FAIL"})


class CostTests(unittest.TestCase):
    def test_cost_none_when_not_configured(self):
        obs = [_obs("candidate_incremental", "1")]
        m = evaluator.evaluate_run(obs, posts_fetched=30, api_errors=0)
        self.assertIsNone(m.estimated_cost_usd)
        self.assertIsNone(m.cost_per_usable_observation_usd)
        self.assertIsNone(m.cost_per_incremental_observation_usd)

    def test_cost_computed_when_configured(self):
        obs = [_obs("candidate_incremental", str(i)) for i in range(5)]
        m = evaluator.evaluate_run(obs, posts_fetched=30, api_errors=0, cost_per_post_usd=0.01)
        self.assertEqual(m.estimated_cost_usd, 0.30)
        self.assertIsNotNone(m.cost_per_usable_observation_usd)
        self.assertIsNotNone(m.cost_per_incremental_observation_usd)

    def test_cost_per_incremental_none_when_no_incremental_candidates(self):
        obs = [_obs("existing_source_duplicate", str(i)) for i in range(30)]
        m = evaluator.evaluate_run(obs, posts_fetched=30, api_errors=0, cost_per_post_usd=0.01)
        self.assertIsNone(m.cost_per_incremental_observation_usd)


class CountingTests(unittest.TestCase):
    def test_counts_every_classification_bucket(self):
        obs = [
            _obs("retrieval_duplicate", "1"),
            _obs("filtered_retweet", "2"),
            _obs("filtered_marketing", "3"),
            _obs("existing_source_duplicate", "4"),
            _obs("candidate_incremental", "5"),
        ]
        m = evaluator.evaluate_run(obs, posts_fetched=5, api_errors=1)
        self.assertEqual(m.retrieval_duplicates, 1)
        self.assertEqual(m.filtered_retweet, 1)
        self.assertEqual(m.filtered_marketing, 1)
        self.assertEqual(m.existing_source_duplicates, 1)
        self.assertEqual(m.candidates_incremental, 1)
        self.assertEqual(m.api_errors, 1)
        self.assertEqual(m.unique_posts, 5)


if __name__ == "__main__":
    unittest.main()
