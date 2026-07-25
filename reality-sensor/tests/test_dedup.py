import _pathsetup  # noqa: F401
import unittest

from reality_sensor.dedup import cluster
from reality_sensor.models import Category, RawCapture, TrustLevel


def _capture(name, category, keywords, **overrides):
    base = dict(
        source_name=name,
        source_url=f"https://example.com/{name}",
        source_trust=TrustLevel.OFFICIAL,
        category=category,
        captured_at="2026-07-20T00:00:00Z",
        title=f"{name} title",
        raw_text=f"{name} raw text",
        affected_capability="some capability",
        capability_keywords=keywords,
    )
    base.update(overrides)
    return RawCapture(**base)


class TestDuplicateDetection(unittest.TestCase):
    def test_multiple_articles_about_one_release_become_one_cluster(self):
        # EXEC-008: "Multiple articles about one release -> One signal"
        a = _capture("TechBlogA", Category.FOUNDATION_MODEL_RELEASES, ["gpt-6", "release"])
        b = _capture("TechBlogB", Category.FOUNDATION_MODEL_RELEASES, ["gpt-6", "launch"])
        clusters = cluster([a, b])
        self.assertEqual(len(clusters), 1)
        self.assertEqual(len(clusters[0]), 2)

    def test_unrelated_captures_stay_separate(self):
        a = _capture("SourceA", Category.FOUNDATION_MODEL_RELEASES, ["gpt-6"])
        b = _capture("SourceB", Category.AGENT_INFRASTRUCTURE, ["mcp-2.0"])
        clusters = cluster([a, b])
        self.assertEqual(len(clusters), 2)

    def test_same_category_no_shared_keyword_stays_separate(self):
        a = _capture("SourceA", Category.FOUNDATION_MODEL_RELEASES, ["gpt-6"])
        b = _capture("SourceB", Category.FOUNDATION_MODEL_RELEASES, ["gemini-3"])
        clusters = cluster([a, b])
        self.assertEqual(len(clusters), 2)

    def test_transitive_clustering(self):
        a = _capture("A", Category.RESEARCH, ["reasoning", "chain-of-thought"])
        b = _capture("B", Category.RESEARCH, ["chain-of-thought", "planning"])
        c = _capture("C", Category.RESEARCH, ["planning", "agents"])
        clusters = cluster([a, b, c])
        self.assertEqual(len(clusters), 1)
        self.assertEqual(len(clusters[0]), 3)

    def test_empty_input_gives_empty_clusters(self):
        self.assertEqual(cluster([]), [])

    def test_clustering_is_order_independent(self):
        a = _capture("A", Category.RESEARCH, ["x"])
        b = _capture("B", Category.RESEARCH, ["x"])
        forward = cluster([a, b])
        backward = cluster([b, a])
        self.assertEqual(len(forward), len(backward))
        self.assertEqual(
            {c.source_name for c in forward[0]}, {c.source_name for c in backward[0]}
        )


if __name__ == "__main__":
    unittest.main()
