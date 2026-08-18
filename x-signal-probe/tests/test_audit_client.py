import _pathsetup  # noqa: F401
import unittest
import urllib.error

from x_signal_probe import audit_client


class LookupBoundsTests(unittest.TestCase):
    def test_single_request_covers_all_requested_ids(self):
        calls = []

        def fake_transport(url, headers):
            calls.append(url)
            return {
                "data": [{"id": "1", "text": "t1", "created_at": "2026-08-18T00:00:00Z"}],
                "meta": {},
            }

        found, unavailable = audit_client.get_posts_by_ids(
            ["1"], "tok", transport=fake_transport, sleep_fn=lambda s: None
        )
        self.assertEqual(len(calls), 1)
        self.assertIn("1", found)
        self.assertEqual(unavailable, [])

    def test_rejects_more_than_max_ids_without_calling_transport(self):
        calls = []

        def fake_transport(url, headers):
            calls.append(url)
            return {"data": [], "meta": {}}

        too_many = [str(i) for i in range(audit_client.MAX_IDS_PER_REQUEST + 1)]
        with self.assertRaises(audit_client.TooManyIdsError):
            audit_client.get_posts_by_ids(too_many, "tok", transport=fake_transport, sleep_fn=lambda s: None)
        self.assertEqual(calls, [])

    def test_ids_missing_from_data_are_unavailable(self):
        def fake_transport(url, headers):
            return {"data": [{"id": "1", "text": "t1", "created_at": ""}], "meta": {}}

        found, unavailable = audit_client.get_posts_by_ids(
            ["1", "2", "3"], "tok", transport=fake_transport, sleep_fn=lambda s: None
        )
        self.assertEqual(set(found), {"1"})
        self.assertEqual(set(unavailable), {"2", "3"})

    def test_ids_listed_in_errors_are_unavailable_not_retried_differently(self):
        def fake_transport(url, headers):
            return {
                "data": [{"id": "1", "text": "t1", "created_at": ""}],
                "errors": [{"value": "2", "detail": "Could not find tweet with id: [2]."}],
                "meta": {},
            }

        found, unavailable = audit_client.get_posts_by_ids(
            ["1", "2"], "tok", transport=fake_transport, sleep_fn=lambda s: None
        )
        self.assertEqual(set(found), {"1"})
        self.assertEqual(unavailable, ["2"])

    def test_duplicate_ids_deduplicated_not_double_counted(self):
        def fake_transport(url, headers):
            return {"data": [{"id": "1", "text": "t1", "created_at": ""}], "meta": {}}

        found, unavailable = audit_client.get_posts_by_ids(
            ["1", "1", "1"], "tok", transport=fake_transport, sleep_fn=lambda s: None
        )
        self.assertEqual(list(found), ["1"])
        self.assertEqual(unavailable, [])


class RetryBoundsTests(unittest.TestCase):
    def test_retries_bounded_on_429_then_succeeds(self):
        attempts = {"n": 0}
        sleeps = []

        def fake_transport(url, headers):
            attempts["n"] += 1
            if attempts["n"] < 2:
                raise urllib.error.HTTPError(url, 429, "rate limited", {}, None)
            return {"data": [{"id": "1", "text": "t", "created_at": ""}], "meta": {}}

        found, _ = audit_client.get_posts_by_ids(["1"], "tok", max_retries=2, transport=fake_transport, sleep_fn=sleeps.append)
        self.assertIn("1", found)
        self.assertEqual(sleeps, [2])

    def test_retries_exhausted_raises_not_retry_forever(self):
        attempts = {"n": 0}

        def fake_transport(url, headers):
            attempts["n"] += 1
            raise urllib.error.HTTPError(url, 429, "rate limited", {}, None)

        with self.assertRaises(audit_client.AuditApiError):
            audit_client.get_posts_by_ids(["1"], "tok", max_retries=2, transport=fake_transport, sleep_fn=lambda s: None)
        self.assertEqual(attempts["n"], 3)

    def test_non_retryable_error_raises_immediately(self):
        sleeps = []

        def fake_transport(url, headers):
            raise urllib.error.HTTPError(url, 401, "unauthorized", {}, None)

        with self.assertRaises(audit_client.AuditApiError):
            audit_client.get_posts_by_ids(["1"], "tok", max_retries=3, transport=fake_transport, sleep_fn=sleeps.append)
        self.assertEqual(sleeps, [])


if __name__ == "__main__":
    unittest.main()
