import _pathsetup  # noqa: F401
import json
import os
import unittest

from capability_observatory_executor import mouser
from capability_observatory_executor.transport import FakeTransport, HttpResult

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def _load(name):
    with open(os.path.join(FIXTURES, name), "r", encoding="utf-8") as fh:
        return json.load(fh)


PANEL_ITEM = {
    "panel_item_id": "C3-011",
    "provider": "provider_e_mouser",
    "source_url": "https://www.mouser.com/",
    "label": "Same exact MCU MPN as C3-010",
    "identity_fields": ["manufacturer", "mpn", "package"],
}


class NormalizeFixtureTests(unittest.TestCase):
    def test_ok_fixture_normalizes_all_fields(self):
        body = _load("mouser_search_ok.json")
        part = body["SearchResults"]["Parts"][0]
        obs = mouser.normalize_part_response(part, ["manufacturer", "mpn", "package"])
        self.assertEqual(obs["price"], 3.42)
        self.assertEqual(obs["currency"], "USD")
        self.assertEqual(obs["availability"], "in_stock")
        self.assertEqual(obs["lead_time_days"], 56.0)  # 8 weeks * 7
        self.assertEqual(obs["identity_values"]["mpn"], "STM32F103C8T6")

    def test_missing_lead_time_and_zero_stock_stay_honest_not_inferred(self):
        body = _load("mouser_search_missing_leadtime.json")
        part = body["SearchResults"]["Parts"][0]
        obs = mouser.normalize_part_response(part, ["manufacturer", "mpn", "package"])
        self.assertIsNone(obs["lead_time_days"])
        self.assertEqual(obs["availability"], "out_of_stock")
        self.assertIsNone(obs["price"])  # empty PriceBreaks -- never fabricated

    def test_lead_time_parser_handles_weeks_and_days(self):
        self.assertEqual(mouser._parse_lead_time_days("8 Weeks"), 56.0)
        self.assertEqual(mouser._parse_lead_time_days("3 Days"), 3.0)
        self.assertIsNone(mouser._parse_lead_time_days(""))
        self.assertIsNone(mouser._parse_lead_time_days(None))

    def test_availability_parser_covers_documented_states(self):
        self.assertEqual(mouser._parse_availability("1500 In Stock"), "in_stock")
        self.assertEqual(mouser._parse_availability("On Backorder"), "backorder")
        self.assertEqual(mouser._parse_availability("Obsolete"), "discontinued")
        self.assertEqual(mouser._parse_availability("something unrecognized"), "unknown")


class RunWithFakeTransportTests(unittest.TestCase):
    def test_missing_credentials_short_circuits_with_no_network_call(self):
        transport = FakeTransport([])
        result = mouser.run(PANEL_ITEM, transport, "2026-08-16T12:00:00Z", env={})
        self.assertEqual(result.outcome, "credentials_error")
        self.assertEqual(transport.calls, [])

    def test_successful_flow_produces_ok_with_observation(self):
        body = _load("mouser_search_ok.json")
        transport = FakeTransport([
            HttpResult(ok=True, status=200, body=json.dumps(body), final_url="https://api.mouser.com/api/v1/search/keyword"),
        ])
        result = mouser.run(PANEL_ITEM, transport, "2026-08-16T12:00:00Z", env={"MOUSER_API_KEY": "test-key"})
        self.assertEqual(result.outcome, "ok")
        self.assertEqual(result.observation["price"], 3.42)

    def test_no_parts_becomes_source_missing(self):
        transport = FakeTransport([
            HttpResult(ok=True, status=200, body='{"Errors": [], "SearchResults": {"Parts": []}}',
                       final_url="https://api.mouser.com/api/v1/search/keyword"),
        ])
        result = mouser.run(PANEL_ITEM, transport, "2026-08-16T12:00:00Z", env={"MOUSER_API_KEY": "test-key"})
        self.assertEqual(result.outcome, "source_missing")

    def test_rate_limit_becomes_api_quota_error(self):
        transport = FakeTransport([
            HttpResult(ok=False, status=429, body="", final_url="https://api.mouser.com/api/v1/search/keyword"),
        ])
        result = mouser.run(PANEL_ITEM, transport, "2026-08-16T12:00:00Z", env={"MOUSER_API_KEY": "test-key"})
        self.assertEqual(result.outcome, "api_quota_error")

    def test_network_failure_becomes_executor_network_blocked(self):
        transport = FakeTransport([
            HttpResult(ok=False, status=None, body="", final_url="x", error_kind="network"),
        ])
        result = mouser.run(PANEL_ITEM, transport, "2026-08-16T12:00:00Z", env={"MOUSER_API_KEY": "test-key"})
        self.assertEqual(result.outcome, "executor_network_blocked")


if __name__ == "__main__":
    unittest.main()
