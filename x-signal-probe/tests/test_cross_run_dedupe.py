"""Cross-run identity: the durable ledger (probe-observations.jsonl)
holds at most one row per real X post_id, ever, across every run that
has found it - not just within a single run's own fetch (that's
dedupe.py's job). Exact post_id string match only - never fuzzy, never
based on text/title similarity."""

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


class CrossRunDedupeTests(unittest.TestCase):
    def test_same_post_id_second_run_is_suppressed_not_duplicated(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            queries_path = _write_queries(tmp, [{"query_id": "q1", "family": "f1", "query": "test"}])
            data_dir = tmp / "data"
            reports_dir = tmp / "reports"

            def fake_transport(url, headers):
                return {
                    "data": [{"id": "100", "text": "our bill exploded and nobody predicted it", "created_at": "2026-08-18T00:00:00Z"}],
                    "meta": {},
                }

            common_kwargs = dict(
                queries_path=str(queries_path),
                bearer_token="tok",
                data_dir=str(data_dir),
                reports_dir=str(reports_dir),
                existing_source_paths=[],
                transport=fake_transport,
                sleep_fn=lambda s: None,
            )

            result1 = probe.run_probe(**common_kwargs, now=dt.datetime(2026, 8, 18, 9, 0, tzinfo=dt.timezone.utc))
            self.assertEqual(result1["metrics"].posts_fetched, 1)
            self.assertEqual(result1["metrics"].cross_run_duplicates, 0)
            rows_after_run1 = Path(result1["obs_path"]).read_text().splitlines()
            self.assertEqual(len(rows_after_run1), 1)

            result2 = probe.run_probe(**common_kwargs, now=dt.datetime(2026, 8, 19, 9, 0, tzinfo=dt.timezone.utc))
            self.assertEqual(result2["metrics"].posts_fetched, 1)
            self.assertEqual(result2["metrics"].cross_run_duplicates, 1)
            self.assertEqual(result2["metrics"].unique_posts, 0)

            # The ledger still has exactly one row for post_id "100" - not two.
            rows_after_run2 = Path(result1["obs_path"]).read_text().splitlines()
            self.assertEqual(len(rows_after_run2), 1)
            post_ids = [json.loads(r)["post_id"] for r in rows_after_run2]
            self.assertEqual(post_ids, ["100"])

    def test_genuinely_new_post_in_second_run_is_still_admitted(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            queries_path = _write_queries(tmp, [{"query_id": "q1", "family": "f1", "query": "test"}])
            data_dir = tmp / "data"
            reports_dir = tmp / "reports"

            call_count = {"n": 0}

            def fake_transport(url, headers):
                call_count["n"] += 1
                pid = "100" if call_count["n"] == 1 else "200"
                return {
                    "data": [{"id": pid, "text": f"problem report {pid}", "created_at": "2026-08-18T00:00:00Z"}],
                    "meta": {},
                }

            common_kwargs = dict(
                queries_path=str(queries_path),
                bearer_token="tok",
                data_dir=str(data_dir),
                reports_dir=str(reports_dir),
                existing_source_paths=[],
                transport=fake_transport,
                sleep_fn=lambda s: None,
            )

            probe.run_probe(**common_kwargs, now=dt.datetime(2026, 8, 18, 9, 0, tzinfo=dt.timezone.utc))
            result2 = probe.run_probe(**common_kwargs, now=dt.datetime(2026, 8, 19, 9, 0, tzinfo=dt.timezone.utc))

            self.assertEqual(result2["metrics"].cross_run_duplicates, 0)
            rows = [json.loads(r) for r in Path(result2["obs_path"]).read_text().splitlines()]
            self.assertEqual(sorted(r["post_id"] for r in rows), ["100", "200"])

    def test_mixed_run_suppresses_only_the_already_ledgered_post(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            queries_path = _write_queries(tmp, [{"query_id": "q1", "family": "f1", "query": "test"}])
            data_dir = tmp / "data"
            reports_dir = tmp / "reports"

            def first_run_transport(url, headers):
                return {"data": [{"id": "1", "text": "first post", "created_at": ""}], "meta": {}}

            def second_run_transport(url, headers):
                return {
                    "data": [
                        {"id": "1", "text": "first post again", "created_at": ""},
                        {"id": "2", "text": "second post, brand new", "created_at": ""},
                    ],
                    "meta": {},
                }

            base_kwargs = dict(
                queries_path=str(queries_path),
                bearer_token="tok",
                data_dir=str(data_dir),
                reports_dir=str(reports_dir),
                existing_source_paths=[],
                sleep_fn=lambda s: None,
            )

            probe.run_probe(**base_kwargs, transport=first_run_transport,
                             now=dt.datetime(2026, 8, 18, 9, 0, tzinfo=dt.timezone.utc))
            result2 = probe.run_probe(**base_kwargs, transport=second_run_transport,
                                       now=dt.datetime(2026, 8, 19, 9, 0, tzinfo=dt.timezone.utc))

            self.assertEqual(result2["metrics"].cross_run_duplicates, 1)
            self.assertEqual(result2["metrics"].unique_posts, 1)
            rows = [json.loads(r) for r in Path(result2["obs_path"]).read_text().splitlines()]
            self.assertEqual(sorted(r["post_id"] for r in rows), ["1", "2"])
            # Only one row for post_id "1" across both runs combined.
            self.assertEqual(sum(1 for r in rows if r["post_id"] == "1"), 1)


if __name__ == "__main__":
    unittest.main()
