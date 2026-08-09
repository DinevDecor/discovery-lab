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
            captures, errors, telemetry = collector.collect_from_config(path)
        finally:
            os.unlink(path)
        self.assertEqual(captures, [])
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["error"], "unsupported source type")
        # Still gets a telemetry row (all zero) rather than vanishing -
        # a misconfigured source should be visible in the report, not silent.
        self.assertIn("mystery", telemetry)
        self.assertEqual(telemetry["mystery"].fetched, 0)

    def test_product_hunt_missing_token_recorded_as_error_not_raised(self):
        import json, tempfile
        cfg = {"sources": [{"name": "PH", "type": "product_hunt", "limit": 5}]}
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(cfg, f)
            path = f.name
        try:
            with patch.dict(os.environ, {}, clear=True):
                captures, errors, telemetry = collector.collect_from_config(path)
        finally:
            os.unlink(path)
        self.assertEqual(captures, [])
        self.assertEqual(len(errors), 1)
        self.assertIn("PRODUCT_HUNT_TOKEN", errors[0]["error"])
        # A source that errors before fetching anything still gets a
        # telemetry row (fetched=admitted=0), so it's never silently
        # missing from the daily report.
        self.assertIn("product_hunt", telemetry)
        self.assertEqual(telemetry["product_hunt"].fetched, 0)
        self.assertEqual(telemetry["product_hunt"].admitted, 0)

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
                captures, errors, telemetry = collector.collect_from_config(path)
        finally:
            os.unlink(path)

        self.assertEqual(errors, [])
        self.assertEqual(len(captures), 2)
        groups = {c.story_group for c in captures}
        self.assertEqual(len(groups), 1)
        self.assertNotEqual(list(groups)[0], "")
        self.assertEqual(telemetry["hacker_news"].duplicates, 1)
        self.assertEqual(telemetry["lobsters"].duplicates, 1)

    def test_high_volume_early_source_cannot_starve_product_hunt_or_discourse(self):
        """Regression test for the real production bug: with sources.json's
        actual ordering (HN, Lobsters, DEV x3, Reddit x5, Product Hunt,
        Discourse x5), HN+Lobsters+one DEV tag alone exceeds the default
        budget of 80, and every source after them - Product Hunt and all 5
        Discourse forums - got zero captures admitted in every real run to
        date. This reproduces that shape with mocked fetches and asserts
        Product Hunt and Discourse now get their fair share."""
        import json, tempfile
        cfg = {
            "sources": [
                {"name": "hn", "type": "hacker_news", "limit": 40},
                {"name": "lob", "type": "lobsters", "limit": 30},
                {"name": "dev-discuss", "type": "dev", "tag": "discuss", "limit": 25},
                {"name": "dev-startup", "type": "dev", "tag": "startup", "limit": 25},
                {"name": "dev-entrepreneurship", "type": "dev", "tag": "entrepreneurship", "limit": 25},
                {"name": "ph", "type": "product_hunt", "limit": 20},
                {"name": "discourse-a", "type": "discourse", "base_url": "https://a.example.test", "community": "a", "limit": 20},
                {"name": "discourse-b", "type": "discourse", "base_url": "https://b.example.test", "community": "b", "limit": 20},
            ]
        }
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(cfg, f)
            path = f.name

        def hn_hits(n):
            return {"hits": [{"url": f"https://hn.example/{i}", "title": f"HN {i}", "story_text": "text", "created_at": "t", "objectID": str(i)} for i in range(n)]}

        def lobsters_items(n):
            return [{"url": f"https://lobsters.example/{i}", "title": f"Lobsters {i}", "description": "text", "created_at": "t"} for i in range(n)]

        def dev_items(n, tag):
            return [{"url": f"https://dev.example/{tag}/{i}", "title": f"Dev {tag} {i}", "description": "text", "published_at": "t"} for i in range(n)]

        def ph_response(n):
            return {"data": {"posts": {"edges": [{"node": {"id": str(i), "name": f"Product {i}", "tagline": "does a thing", "slug": f"p{i}", "createdAt": "t"}} for i in range(n)]}}}

        def discourse_listing(n):
            return {"topic_list": {"topics": [{"id": i, "slug": f"t{i}", "title": f"Topic {i}", "created_at": "t"} for i in range(n)]}}

        discourse_detail = {"post_stream": {"posts": [{"cooked": "<p>a real problem description</p>"}]}}

        def fake_get_json(url, headers=None):
            if "hn.algolia.com" in url:
                return hn_hits(40)
            if "lobste.rs" in url:
                return lobsters_items(30)
            if "dev.to" in url:
                if "tag=discuss" in url:
                    return dev_items(25, "discuss")
                if "tag=startup" in url:
                    return dev_items(25, "startup")
                return dev_items(25, "entrepreneurship")
            if "a.example.test" in url and "latest.json" in url:
                return discourse_listing(20)
            if "b.example.test" in url and "latest.json" in url:
                return discourse_listing(20)
            if "/t/" in url:
                return discourse_detail
            raise AssertionError(f"unexpected url {url}")

        def fake_post_graphql(url, token, query, variables=None):
            return ph_response(20)

        try:
            with patch.dict(os.environ, {"PRODUCT_HUNT_TOKEN": "tok"}):
                with patch.object(collector, "_get_json", side_effect=fake_get_json), \
                     patch.object(collector, "_post_graphql", side_effect=fake_post_graphql):
                    captures, errors, telemetry = collector.collect_from_config(path, budget=80)
        finally:
            os.unlink(path)

        self.assertEqual(errors, [])
        # Total fetched across all 8 sources vastly exceeds the budget -
        # exactly the real-world shape that used to starve later sources.
        total_fetched = sum(t.fetched for t in telemetry.values())
        self.assertGreater(total_fetched, 80)

        # The actual regression: these must NOT be zero anymore.
        self.assertGreater(telemetry["product_hunt"].admitted, 0)
        self.assertGreater(telemetry["discourse:a"].admitted, 0)
        self.assertGreater(telemetry["discourse:b"].admitted, 0)

        # Fairness: no source should be admitted more than one capture
        # ahead of the least-admitted source among those with supply.
        admitted_counts = [t.admitted for t in telemetry.values() if t.fetched > 0]
        self.assertLessEqual(max(admitted_counts) - min(admitted_counts), 1)

        self.assertEqual(sum(t.admitted for t in telemetry.values()), 80)
        self.assertEqual(len(captures), 80)


if __name__ == "__main__":
    unittest.main()
