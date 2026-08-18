import _pathsetup  # noqa: F401
import unittest
import urllib.error

from x_signal_probe import client


class BoundedPaginationTests(unittest.TestCase):
    def test_stops_after_max_pages_even_with_next_token_available(self):
        calls = []

        def fake_transport(url, headers):
            calls.append(url)
            return {"data": [{"id": str(len(calls))}], "meta": {"next_token": "more"}}

        results = client.search_recent(
            "q", "tok", max_pages=2, transport=fake_transport, sleep_fn=lambda s: None
        )
        self.assertEqual(len(calls), 2)
        self.assertEqual(len(results), 2)

    def test_stops_early_when_no_next_token(self):
        calls = []

        def fake_transport(url, headers):
            calls.append(url)
            return {"data": [{"id": "1"}], "meta": {}}

        results = client.search_recent(
            "q", "tok", max_pages=5, transport=fake_transport, sleep_fn=lambda s: None
        )
        self.assertEqual(len(calls), 1)
        self.assertEqual(len(results), 1)

    def test_rejects_zero_max_pages(self):
        with self.assertRaises(ValueError):
            client.search_recent("q", "tok", max_pages=0)

    def test_default_max_results_and_pages_are_conservative(self):
        self.assertEqual(client.DEFAULT_MAX_RESULTS_PER_QUERY, 10)
        self.assertEqual(client.DEFAULT_MAX_PAGES_PER_QUERY, 1)


class BoundedRetryTests(unittest.TestCase):
    def test_retries_bounded_on_429_then_succeeds(self):
        attempts = {"n": 0}
        sleeps = []

        def fake_transport(url, headers):
            attempts["n"] += 1
            if attempts["n"] < 2:
                raise urllib.error.HTTPError(url, 429, "rate limited", {}, None)
            return {"data": [{"id": "1"}], "meta": {}}

        results = client.search_recent(
            "q", "tok", max_retries=2, transport=fake_transport, sleep_fn=sleeps.append
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(sleeps, [2])  # first backoff step only, never unbounded

    def test_retries_exhausted_raises_xapierror_not_retry_forever(self):
        attempts = {"n": 0}

        def fake_transport(url, headers):
            attempts["n"] += 1
            raise urllib.error.HTTPError(url, 429, "rate limited", {}, None)

        with self.assertRaises(client.XApiError):
            client.search_recent(
                "q", "tok", max_retries=2, transport=fake_transport, sleep_fn=lambda s: None
            )
        self.assertEqual(attempts["n"], 3)  # 1 initial + 2 retries, never more

    def test_non_retryable_error_raises_immediately_without_sleeping(self):
        sleeps = []

        def fake_transport(url, headers):
            raise urllib.error.HTTPError(url, 401, "unauthorized", {}, None)

        with self.assertRaises(client.XApiError):
            client.search_recent(
                "q", "tok", max_retries=3, transport=fake_transport, sleep_fn=sleeps.append
            )
        self.assertEqual(sleeps, [])


if __name__ == "__main__":
    unittest.main()
