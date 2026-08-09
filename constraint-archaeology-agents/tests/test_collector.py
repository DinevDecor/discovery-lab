import os, sys, unittest
from unittest.mock import patch
ROOT=os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0,os.path.join(ROOT,"src"))
from ca_agents import collector
from ca_agents.collector import CollectorError


class TestProductHunt(unittest.TestCase):
    def test_missing_token_raises_collector_error(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(CollectorError):
                collector.collect_product_hunt(5)

    def test_graphql_error_payload_raises_collector_error(self):
        with patch.dict(os.environ, {"PRODUCT_HUNT_TOKEN": "tok"}):
            with patch.object(collector, "_post_graphql", return_value={"errors": [{"message": "invalid token"}]}):
                with self.assertRaises(CollectorError):
                    collector.collect_product_hunt(5)

    def test_parses_posts_without_votes_and_includes_comment_context(self):
        fake_response = {
            "data": {
                "posts": {
                    "edges": [
                        {
                            "node": {
                                "id": "1",
                                "name": "Widget",
                                "tagline": "Do the thing for teams",
                                "slug": "widget",
                                "website": "https://widget.example",
                                "votesCount": 532,
                                "createdAt": "2026-08-01T00:00:00Z",
                                "comments": {
                                    "edges": [
                                        {"node": {"body": "We built this after manual reconciliation was painful"}}
                                    ]
                                },
                            }
                        }
                    ]
                }
            }
        }
        with patch.dict(os.environ, {"PRODUCT_HUNT_TOKEN": "tok"}):
            with patch.object(collector, "_post_graphql", return_value=fake_response):
                caps = collector.collect_product_hunt(5)
        self.assertEqual(len(caps), 1)
        c = caps[0]
        self.assertEqual(c.source, "product_hunt")
        self.assertEqual(c.url, "https://www.producthunt.com/posts/widget")
        self.assertNotIn("532", c.text)
        self.assertIn("manual reconciliation was painful", c.text)

    def test_skips_edges_with_no_name(self):
        fake_response = {"data": {"posts": {"edges": [{"node": {"name": "", "tagline": "x"}}]}}}
        with patch.dict(os.environ, {"PRODUCT_HUNT_TOKEN": "tok"}):
            with patch.object(collector, "_post_graphql", return_value=fake_response):
                caps = collector.collect_product_hunt(5)
        self.assertEqual(caps, [])


class TestDiscourse(unittest.TestCase):
    def test_parses_newest_topics_with_op_text_html_stripped(self):
        latest_response = {
            "topic_list": {
                "topics": [
                    {"id": 101, "slug": "sync-fails-randomly", "title": "Sync fails randomly on large libraries", "created_at": "2026-08-05T00:00:00Z"}
                ]
            }
        }
        topic_detail = {
            "post_stream": {
                "posts": [
                    {"cooked": "<p>My library sync keeps failing when I have more than 2000 items.</p>"},
                    {"cooked": "<p>Same here, had to split my library into two.</p>"},
                ]
            }
        }

        def fake_get_json(url, headers=None):
            if "latest.json" in url:
                self.assertIn("order=created", url)
                return latest_response
            return topic_detail

        with patch.object(collector, "_get_json", side_effect=fake_get_json):
            caps = collector.collect_discourse("https://example-forum.test", "example", limit=5)
        self.assertEqual(len(caps), 1)
        c = caps[0]
        self.assertEqual(c.source, "discourse:example")
        self.assertEqual(c.url, "https://example-forum.test/t/sync-fails-randomly/101")
        self.assertIn("more than 2000 items", c.text)
        self.assertIn("split my library into two", c.text)
        self.assertNotIn("<p>", c.text)

    def test_each_forum_keeps_distinct_source_label(self):
        listing = {"topic_list": {"topics": [{"id": 1, "slug": "a", "title": "Topic A", "created_at": "t"}]}}
        detail = {"post_stream": {"posts": [{"cooked": "body"}]}}

        def fake_get_json(url, headers=None):
            return listing if "latest.json" in url else detail

        with patch.object(collector, "_get_json", side_effect=fake_get_json):
            a = collector.collect_discourse("https://forum-a.test", "forum-a", limit=5)
            b = collector.collect_discourse("https://forum-b.test", "forum-b", limit=5)
        self.assertEqual(a[0].source, "discourse:forum-a")
        self.assertEqual(b[0].source, "discourse:forum-b")

    def test_topic_with_no_posts_skipped(self):
        listing = {"topic_list": {"topics": [{"id": 1, "slug": "a", "title": "Empty topic", "created_at": "t"}]}}
        detail = {"post_stream": {"posts": []}}

        def fake_get_json(url, headers=None):
            return listing if "latest.json" in url else detail

        with patch.object(collector, "_get_json", side_effect=fake_get_json):
            caps = collector.collect_discourse("https://example-forum.test", "example", limit=5)
        self.assertEqual(caps, [])


class TestCollectFromConfigDispatch(unittest.TestCase):
    def test_unknown_source_type_recorded_as_error_not_raised(self):
        import json, tempfile
        cfg = {"sources": [{"name": "mystery", "type": "carrier_pigeon"}]}
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(cfg, f)
            path = f.name
        try:
            captures, errors = collector.collect_from_config(path)
        finally:
            os.unlink(path)
        self.assertEqual(captures, [])
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["error"], "unsupported source type")

    def test_product_hunt_missing_token_recorded_as_error_not_raised(self):
        import json, tempfile
        cfg = {"sources": [{"name": "PH", "type": "product_hunt", "limit": 5}]}
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(cfg, f)
            path = f.name
        try:
            with patch.dict(os.environ, {}, clear=True):
                captures, errors = collector.collect_from_config(path)
        finally:
            os.unlink(path)
        self.assertEqual(captures, [])
        self.assertEqual(len(errors), 1)
        self.assertIn("PRODUCT_HUNT_TOKEN", errors[0]["error"])

    def test_crosspost_across_sources_gets_shared_story_group(self):
        import json, tempfile
        cfg = {
            "sources": [
                {"name": "hn", "type": "hacker_news", "limit": 1},
                {"name": "lob", "type": "lobsters", "limit": 1},
            ]
        }
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(cfg, f)
            path = f.name

        hn_payload = {"hits": [{"url": "https://vendor.example.com/launch", "title": "Announcing Widget", "story_text": "", "comment_text": "", "created_at": "t", "objectID": "1"}]}
        lobsters_payload = [{"url": "https://vendor.example.com/launch?ref=lobsters", "title": "Announcing Widget", "description": "", "created_at": "t", "comments_url": ""}]

        def fake_get_json(url, headers=None):
            if "hn.algolia.com" in url:
                return hn_payload
            if "lobste.rs" in url:
                return lobsters_payload
            raise AssertionError(f"unexpected url {url}")

        try:
            with patch.object(collector, "_get_json", side_effect=fake_get_json):
                captures, errors = collector.collect_from_config(path)
        finally:
            os.unlink(path)

        self.assertEqual(errors, [])
        self.assertEqual(len(captures), 2)
        groups = {c.story_group for c in captures}
        self.assertEqual(len(groups), 1)
        self.assertNotEqual(list(groups)[0], "")


if __name__ == "__main__":
    unittest.main()
