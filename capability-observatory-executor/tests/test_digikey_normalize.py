import _pathsetup  # noqa: F401
import json
import os
import unittest

from capability_observatory_executor import digikey
from capability_observatory_executor.transport import FakeTransport, HttpResult

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def _load(name):
    with open(os.path.join(FIXTURES, name), "r", encoding="utf-8") as fh:
        return json.load(fh)


PANEL_ITEM = {
    "panel_item_id": "C3-010",
    "provider": "provider_d_digikey",
    "source_url": "https://www.digikey.com/",
    "label": "General-purpose 32-bit MCU",
    "identity_fields": ["manufacturer", "mpn", "package"],
}


class NormalizeFixtureTests(unittest.TestCase):
    def test_ok_fixture_normalizes_all_fields(self):
        body = _load("digikey_product_details_ok.json")
        obs = digikey.normalize_product_response(body["Products"][0], ["manufacturer", "mpn", "package"])
        self.assertEqual(obs["price"], 3.42)
        self.assertEqual(obs["currency"], "USD")
        self.assertEqual(obs["availability"], "in_stock")
        self.assertEqual(obs["lead_time_days"], 56.0)
        self.assertEqual(obs["identity_values"]["mpn"], "STM32F103C8T6")
        self.assertEqual(obs["identity_values"]["manufacturer"], "STMicroelectronics")
        self.assertEqual(obs["quote_type"], "list_price")

    def test_missing_lead_time_stays_null_never_inferred(self):
        body = _load("digikey_product_details_missing_leadtime.json")
        obs = digikey.normalize_product_response(body["Products"][0], ["manufacturer", "mpn", "package"])
        self.assertIsNone(obs["lead_time_days"])
        # everything else the fixture DID provide is still present
        self.assertEqual(obs["price"], 3.42)


class RunWithFakeTransportTests(unittest.TestCase):
    def _token_response(self):
        return HttpResult(ok=True, status=200, body=json.dumps(_load("digikey_token_ok.json")), final_url=digikey.TOKEN_URL)

    def test_missing_credentials_short_circuits_with_no_network_call(self):
        transport = FakeTransport([])  # no responses programmed -- must not be called
        result = digikey.run(PANEL_ITEM, transport, "2026-08-16T12:00:00Z", env={})
        self.assertEqual(result.outcome, "credentials_error")
        self.assertEqual(result.error_category, "missing_credentials")
        self.assertEqual(transport.calls, [])

    def test_successful_flow_produces_ok_with_observation(self):
        product_body = _load("digikey_product_details_ok.json")
        transport = FakeTransport([
            self._token_response(),
            HttpResult(ok=True, status=200, body=json.dumps(product_body), final_url=digikey.KEYWORD_SEARCH_URL),
        ])
        env = {"DIGIKEY_CLIENT_ID": "test-id", "DIGIKEY_CLIENT_SECRET": "test-secret"}
        result = digikey.run(PANEL_ITEM, transport, "2026-08-16T12:00:00Z", env=env)
        self.assertEqual(result.outcome, "ok")
        self.assertIsNotNone(result.observation)
        self.assertEqual(result.observation["price"], 3.42)

    def test_token_rejected_becomes_credentials_error(self):
        transport = FakeTransport([
            HttpResult(ok=False, status=401, body='{"error":"invalid_client"}', final_url=digikey.TOKEN_URL),
        ])
        env = {"DIGIKEY_CLIENT_ID": "bad-id", "DIGIKEY_CLIENT_SECRET": "bad-secret"}
        result = digikey.run(PANEL_ITEM, transport, "2026-08-16T12:00:00Z", env=env)
        self.assertEqual(result.outcome, "credentials_error")

    def test_quota_exceeded_becomes_api_quota_error(self):
        transport = FakeTransport([
            self._token_response(),
            HttpResult(ok=False, status=429, body='{"error":"quota exceeded"}', final_url=digikey.KEYWORD_SEARCH_URL),
        ])
        env = {"DIGIKEY_CLIENT_ID": "test-id", "DIGIKEY_CLIENT_SECRET": "test-secret"}
        result = digikey.run(PANEL_ITEM, transport, "2026-08-16T12:00:00Z", env=env)
        self.assertEqual(result.outcome, "api_quota_error")

    def test_network_failure_on_token_call_becomes_executor_network_blocked(self):
        transport = FakeTransport([
            HttpResult(ok=False, status=None, body="", final_url=digikey.TOKEN_URL, error_kind="network"),
        ])
        env = {"DIGIKEY_CLIENT_ID": "test-id", "DIGIKEY_CLIENT_SECRET": "test-secret"}
        result = digikey.run(PANEL_ITEM, transport, "2026-08-16T12:00:00Z", env=env)
        self.assertEqual(result.outcome, "executor_network_blocked")

    def test_timeout_on_token_call_becomes_timeout(self):
        transport = FakeTransport([
            HttpResult(ok=False, status=None, body="", final_url=digikey.TOKEN_URL, error_kind="timeout"),
        ])
        env = {"DIGIKEY_CLIENT_ID": "test-id", "DIGIKEY_CLIENT_SECRET": "test-secret"}
        result = digikey.run(PANEL_ITEM, transport, "2026-08-16T12:00:00Z", env=env)
        self.assertEqual(result.outcome, "timeout")

    def test_no_product_in_response_becomes_source_missing(self):
        transport = FakeTransport([
            self._token_response(),
            HttpResult(ok=True, status=200, body='{"Products": []}', final_url=digikey.KEYWORD_SEARCH_URL),
        ])
        env = {"DIGIKEY_CLIENT_ID": "test-id", "DIGIKEY_CLIENT_SECRET": "test-secret"}
        result = digikey.run(PANEL_ITEM, transport, "2026-08-16T12:00:00Z", env=env)
        self.assertEqual(result.outcome, "source_missing")


if __name__ == "__main__":
    unittest.main()
