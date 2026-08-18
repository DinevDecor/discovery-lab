import _pathsetup  # noqa: F401
import unittest

from x_signal_probe import client


class ApiFailureTests(unittest.TestCase):
    def test_error_payload_without_data_raises_xapierror(self):
        def fake_transport(url, headers):
            return {"errors": [{"message": "bad query"}]}

        with self.assertRaises(client.XApiError):
            client.search_recent("q", "tok", transport=fake_transport, sleep_fn=lambda s: None)

    def test_error_payload_alongside_data_does_not_raise(self):
        # X's API can return partial `errors` (e.g. a dropped expansion)
        # alongside real `data` - only a pure-error payload should abort
        # the probe for that query.
        def fake_transport(url, headers):
            return {"data": [{"id": "1"}], "errors": [{"message": "minor"}], "meta": {}}

        results = client.search_recent("q", "tok", transport=fake_transport, sleep_fn=lambda s: None)
        self.assertEqual(len(results), 1)

    def test_malformed_payload_missing_data_key_yields_empty_results(self):
        def fake_transport(url, headers):
            return {"meta": {}}

        results = client.search_recent("q", "tok", transport=fake_transport, sleep_fn=lambda s: None)
        self.assertEqual(results, [])

    def test_transport_exception_wrapped_as_xapierror(self):
        def fake_transport(url, headers):
            raise ConnectionError("network is down")

        with self.assertRaises(client.XApiError):
            client.search_recent("q", "tok", transport=fake_transport, sleep_fn=lambda s: None)


if __name__ == "__main__":
    unittest.main()
