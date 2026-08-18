import _pathsetup  # noqa: F401
import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path

from x_signal_probe import probe


def _write_queries(tmp: Path, queries: list[dict]) -> Path:
    path = tmp / "queries.json"
    path.write_text(json.dumps({"queries": queries}), encoding="utf-8")
    return path


class GlobalCapTests(unittest.TestCase):
    def test_max_posts_per_run_is_enforced_across_queries(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            queries = [
                {"query_id": f"q{i}", "family": "fam", "query": f"query {i}"} for i in range(5)
            ]
            queries_path = _write_queries(tmp, queries)

            call_counter = {"n": 0}

            def fake_transport(url, headers):
                # Each query "finds" 10 distinct posts (globally unique ids).
                call_counter["n"] += 1
                base = call_counter["n"] * 100
                return {
                    "data": [
                        {"id": str(base + n), "text": f"problem report number {n}", "created_at": "2026-08-10T00:00:00Z"}
                        for n in range(10)
                    ],
                    "meta": {},
                }

            result = probe.run_probe(
                queries_path=str(queries_path),
                bearer_token="tok",
                data_dir=str(tmp / "data"),
                reports_dir=str(tmp / "reports"),
                existing_source_paths=[],
                max_results_per_query=10,
                max_pages_per_query=1,
                max_posts_per_run=12,
                transport=fake_transport,
                sleep_fn=lambda s: None,
                now=dt.datetime(2026, 8, 18, tzinfo=dt.timezone.utc),
            )
            self.assertEqual(result["metrics"].posts_fetched, 12)

    def test_api_errors_recorded_and_run_continues(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            queries = [
                {"query_id": "q_bad", "family": "fam", "query": "bad"},
                {"query_id": "q_good", "family": "fam", "query": "good"},
            ]
            queries_path = _write_queries(tmp, queries)

            def fake_transport(url, headers):
                if "bad" in url:
                    return {"errors": [{"message": "boom"}]}
                return {"data": [{"id": "1", "text": "our bill exploded", "created_at": ""}], "meta": {}}

            result = probe.run_probe(
                queries_path=str(queries_path),
                bearer_token="tok",
                data_dir=str(tmp / "data"),
                reports_dir=str(tmp / "reports"),
                existing_source_paths=[],
                transport=fake_transport,
                sleep_fn=lambda s: None,
                now=dt.datetime(2026, 8, 18, tzinfo=dt.timezone.utc),
            )
            self.assertEqual(len(result["errors"]), 1)
            self.assertIn("q_bad", result["errors"][0])
            self.assertEqual(result["metrics"].posts_fetched, 1)

    def test_observations_persisted_and_report_written(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            queries = [{"query_id": "q1", "family": "fam", "query": "test"}]
            queries_path = _write_queries(tmp, queries)

            def fake_transport(url, headers):
                return {"data": [{"id": "1", "text": "our bill exploded and nobody expected it", "created_at": "2026-08-10T00:00:00Z"}], "meta": {}}

            result = probe.run_probe(
                queries_path=str(queries_path),
                bearer_token="tok",
                data_dir=str(tmp / "data"),
                reports_dir=str(tmp / "reports"),
                existing_source_paths=[],
                transport=fake_transport,
                sleep_fn=lambda s: None,
                now=dt.datetime(2026, 8, 18, tzinfo=dt.timezone.utc),
            )
            self.assertTrue(Path(result["obs_path"]).exists())
            self.assertTrue(Path(result["report_path"]).exists())
            rows = [json.loads(line) for line in Path(result["obs_path"]).read_text().splitlines()]
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["classification"], "candidate_incremental")
            self.assertEqual(rows[0]["canonical_url"], "https://x.com/i/status/1")


if __name__ == "__main__":
    unittest.main()
