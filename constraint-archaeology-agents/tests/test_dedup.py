import os, sys, unittest
ROOT=os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0,os.path.join(ROOT,"src"))
from ca_agents.models import Capture
from ca_agents.dedup import assign_story_groups, canonical_url


class TestCanonicalUrl(unittest.TestCase):
    def test_strips_www_and_trailing_slash(self):
        self.assertEqual(canonical_url("https://www.example.com/post/"), canonical_url("http://example.com/post"))

    def test_strips_tracking_params_but_keeps_real_query(self):
        a = canonical_url("https://example.com/post?id=42&utm_source=hn&utm_campaign=x")
        b = canonical_url("https://example.com/post?id=42")
        self.assertEqual(a, b)

    def test_empty_url_is_empty(self):
        self.assertEqual(canonical_url(""), "")


class TestAssignStoryGroups(unittest.TestCase):
    def cap(self, source, url, title, text="body"):
        return Capture(source, url, title, text, "2026-08-08T00:00:00Z", "2026-08-08T00:00:01Z")

    def test_same_canonical_url_across_sources_grouped(self):
        caps = [
            self.cap("hacker_news", "https://example.com/post?utm_source=hn", "Cool tool"),
            self.cap("lobsters", "https://example.com/post", "Cool tool launch"),
        ]
        groups = assign_story_groups(caps)
        self.assertEqual(set(groups.keys()), {0, 1})
        self.assertEqual(groups[0], groups[1])

    def test_near_duplicate_titles_across_sources_grouped(self):
        caps = [
            self.cap("hacker_news", "https://a.example.com/x", "Show HN: We built Widget for syncing files"),
            self.cap("dev:startup", "https://blog.example.com/widget-launch", "Widget for syncing files launched today"),
        ]
        groups = assign_story_groups(caps, title_threshold=0.5)
        self.assertEqual(groups[0], groups[1])

    def test_unrelated_captures_not_grouped(self):
        caps = [
            self.cap("hacker_news", "https://a.example.com/1", "Unrelated topic A"),
            self.cap("lobsters", "https://b.example.com/2", "Completely different topic B"),
        ]
        self.assertEqual(assign_story_groups(caps), {})

    def test_same_source_near_duplicate_titles_not_grouped(self):
        # Two similarly-titled threads on the SAME forum are not a crosspost -
        # that's memory.py/same-mechanism clustering's concern, not this layer's.
        caps = [
            self.cap("hacker_news", "https://a.example.com/1", "Widget launch"),
            self.cap("hacker_news", "https://a.example.com/1-repost", "Widget launch"),
        ]
        self.assertEqual(assign_story_groups(caps), {})

    def test_three_way_crosspost_shares_one_group(self):
        caps = [
            self.cap("hacker_news", "https://vendor.example.com/launch", "Announcing Widget"),
            self.cap("lobsters", "https://vendor.example.com/launch?ref=lobsters", "Announcing Widget"),
            self.cap("product_hunt", "https://www.producthunt.com/posts/widget", "Widget"),
        ]
        groups = assign_story_groups(caps)
        self.assertEqual(groups[0], groups[1])
        self.assertNotIn(2, groups)  # different URL, title too short/dissimilar to match safely

    def test_group_id_deterministic_and_order_independent(self):
        caps_a = [
            self.cap("hacker_news", "https://example.com/post", "Cool tool"),
            self.cap("lobsters", "https://example.com/post", "Cool tool"),
        ]
        caps_b = list(reversed(caps_a))
        ga = assign_story_groups(caps_a)
        gb = assign_story_groups(caps_b)
        self.assertEqual(set(ga.values()), set(gb.values()))


if __name__ == "__main__":
    unittest.main()
