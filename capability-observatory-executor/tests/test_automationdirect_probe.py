import _pathsetup  # noqa: F401
import unittest

from capability_observatory_executor import automationdirect
from capability_observatory_executor.transport import FakeTransport, HttpResult

PINNED_ITEM = {
    "panel_item_id": "C3-001", "provider": "provider_a_automationdirect",
    "source_url": "https://www.automationdirect.com/adc/shopping/catalog/example-plc-cpu",
    "source_url_pinned": True,
}
UNPINNED_ITEM = {
    "panel_item_id": "C3-002", "provider": "provider_a_automationdirect",
    "source_url": "https://www.automationdirect.com/", "source_url_pinned": False,
}

ROBOTS_ALLOW_ALL = "User-agent: *\nDisallow:\n"
ROBOTS_DISALLOW_ALL = "User-agent: *\nDisallow: /\n"
ROBOTS_DISALLOW_SHOP = "User-agent: *\nDisallow: /shopping/\n"


class RobotsParsingTests(unittest.TestCase):
    def test_allows_root_when_nothing_disallowed(self):
        self.assertTrue(automationdirect.path_is_allowed(ROBOTS_ALLOW_ALL, "/"))

    def test_disallows_root_when_everything_blocked(self):
        self.assertFalse(automationdirect.path_is_allowed(ROBOTS_DISALLOW_ALL, "/"))

    def test_only_applies_rules_from_the_star_block(self):
        text = "User-agent: SomeOtherBot\nDisallow: /\nUser-agent: *\nDisallow:\n"
        self.assertTrue(automationdirect.path_is_allowed(text, "/"))

    def test_no_star_block_means_nothing_is_disallowed(self):
        text = "User-agent: SomeOtherBot\nDisallow: /\n"
        self.assertTrue(automationdirect.path_is_allowed(text, "/"))


class ProbeClassificationTests(unittest.TestCase):
    def test_reachable_and_allowed_classifies_automated_ok(self):
        transport = FakeTransport([
            HttpResult(ok=True, status=200, body=ROBOTS_ALLOW_ALL, final_url=automationdirect.ROBOTS_URL),
            HttpResult(ok=True, status=200, body="<html>homepage</html>", final_url=automationdirect.BASE_URL),
        ])
        result = automationdirect.probe(transport)
        self.assertEqual(result.classification, "AUTOMATED_OK")

    def test_robots_disallow_classifies_provider_blocked_without_fetching_homepage(self):
        transport = FakeTransport([
            HttpResult(ok=True, status=200, body=ROBOTS_DISALLOW_ALL, final_url=automationdirect.ROBOTS_URL),
        ])
        result = automationdirect.probe(transport)
        self.assertEqual(result.classification, "PROVIDER_BLOCKED")
        self.assertEqual(len(transport.calls), 1)  # never even tried the homepage

    def test_homepage_403_classifies_provider_blocked(self):
        transport = FakeTransport([
            HttpResult(ok=True, status=200, body=ROBOTS_ALLOW_ALL, final_url=automationdirect.ROBOTS_URL),
            HttpResult(ok=False, status=403, body="blocked", final_url=automationdirect.BASE_URL),
        ])
        result = automationdirect.probe(transport)
        self.assertEqual(result.classification, "PROVIDER_BLOCKED")

    def test_network_failure_classifies_executor_failure_never_provider_blocked(self):
        transport = FakeTransport([
            HttpResult(ok=False, status=None, body="", final_url=automationdirect.ROBOTS_URL, error_kind="network"),
        ])
        result = automationdirect.probe(transport)
        self.assertEqual(result.classification, "EXECUTOR_FAILURE")

    def test_timeout_classifies_executor_failure(self):
        transport = FakeTransport([
            HttpResult(ok=True, status=200, body=ROBOTS_ALLOW_ALL, final_url=automationdirect.ROBOTS_URL),
            HttpResult(ok=False, status=None, body="", final_url=automationdirect.BASE_URL, error_kind="timeout"),
        ])
        result = automationdirect.probe(transport)
        self.assertEqual(result.classification, "EXECUTOR_FAILURE")


class RunTests(unittest.TestCase):
    def test_executor_failure_probe_short_circuits_to_executor_network_blocked(self):
        probe_result = automationdirect.ProbeResult("EXECUTOR_FAILURE", False, False, None, "network failure")
        submission = automationdirect.run(UNPINNED_ITEM, probe_result, FakeTransport([]), "2026-08-16T07:30:00Z")
        self.assertEqual(submission.outcome, "executor_network_blocked")

    def test_provider_blocked_probe_short_circuits_to_provider_access_blocked(self):
        probe_result = automationdirect.ProbeResult("PROVIDER_BLOCKED", True, True, False, "robots.txt disallow")
        submission = automationdirect.run(UNPINNED_ITEM, probe_result, FakeTransport([]), "2026-08-16T07:30:00Z")
        self.assertEqual(submission.outcome, "provider_access_blocked")

    def test_unpinned_item_never_fabricates_a_product_url_or_price(self):
        probe_result = automationdirect.ProbeResult("AUTOMATED_OK", True, True, True, "homepage reachable")
        submission = automationdirect.run(UNPINNED_ITEM, probe_result, FakeTransport([]), "2026-08-16T07:30:00Z")
        self.assertEqual(submission.outcome, "parse_error")
        self.assertEqual(submission.error_category, "panel_item_not_pinned_to_product_page")
        self.assertIsNone(submission.observation)
        self.assertEqual(submission.requested_url, UNPINNED_ITEM["source_url"])  # never invented

    def test_pinned_item_with_successful_probe_fetches_the_real_pinned_url(self):
        probe_result = automationdirect.ProbeResult("AUTOMATED_OK", True, True, True, "homepage reachable")
        transport = FakeTransport([
            HttpResult(ok=True, status=200, body="<html>Example PLC CPU</html>", final_url=PINNED_ITEM["source_url"]),
        ])
        submission = automationdirect.run(PINNED_ITEM, probe_result, transport, "2026-08-16T07:30:00Z")
        self.assertEqual(transport.calls[0][1], PINNED_ITEM["source_url"])
        # No page-specific parser exists yet -- honestly reported, not fabricated.
        self.assertEqual(submission.outcome, "parse_error")
        self.assertEqual(submission.error_category, "no_parser_implemented_for_this_product_page")


if __name__ == "__main__":
    unittest.main()
