"""Dynamic proof that neither the X bearer token nor raw post text ever
reaches any file this package writes - the concrete guarantee behind
CONTRACT.md's data-minimization rule and the §5 storage-design change
(no post text/quote persisted anywhere, transient in-memory only)."""

import _pathsetup  # noqa: F401
import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path

from x_signal_probe import probe

FAKE_TOKEN = "FAKE-SECRET-TOKEN-abc123"
DISTINCTIVE_MARKER = "UNIQUE_MARKER_do_not_persist_this_exact_string"


def _run(tmp: Path, bearer_token: str, post_text: str):
    queries_path = tmp / "queries.json"
    queries_path.write_text(
        json.dumps({"queries": [{"query_id": "q1", "family": "f1", "query": "test"}]}),
        encoding="utf-8",
    )

    def fake_transport(url, headers):
        assert headers.get("Authorization") == f"Bearer {bearer_token}"
        return {
            "data": [{"id": "100", "text": post_text, "created_at": "2026-08-10T00:00:00Z"}],
            "meta": {},
        }

    data_dir = tmp / "data"
    reports_dir = tmp / "reports"
    probe.run_probe(
        queries_path=str(queries_path),
        bearer_token=bearer_token,
        data_dir=str(data_dir),
        reports_dir=str(reports_dir),
        existing_source_paths=[],
        transport=fake_transport,
        sleep_fn=lambda s: None,
        now=dt.datetime(2026, 8, 18, tzinfo=dt.timezone.utc),
    )
    return data_dir, reports_dir


def _assert_string_absent_from_tree(test: unittest.TestCase, *roots: Path, needle: str):
    checked_any = False
    for root in roots:
        for path in root.rglob("*"):
            if path.is_file():
                checked_any = True
                content = path.read_text(encoding="utf-8")
                test.assertNotIn(needle, content, f"{needle!r} leaked into {path}")
    test.assertTrue(checked_any, "expected at least one output file to check")


class SecretNeverPersistedTests(unittest.TestCase):
    def test_bearer_token_never_written_to_any_output_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            data_dir, reports_dir = _run(
                tmp, FAKE_TOKEN, f"our bill exploded, token {FAKE_TOKEN} appears in the post text itself"
            )
            _assert_string_absent_from_tree(self, data_dir, reports_dir, needle=FAKE_TOKEN)


class PostTextNeverPersistedTests(unittest.TestCase):
    def test_raw_post_text_never_written_to_any_output_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            distinctive_text = f"{DISTINCTIVE_MARKER} our bill exploded and nobody predicted it"
            data_dir, reports_dir = _run(tmp, "tok", distinctive_text)
            _assert_string_absent_from_tree(self, data_dir, reports_dir, needle=DISTINCTIVE_MARKER)

    def test_no_author_identifier_field_present_in_persisted_observation(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            data_dir, _ = _run(tmp, "tok", "our bill exploded")
            obs_path = data_dir / "probe-observations.jsonl"
            rows = [json.loads(line) for line in obs_path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(rows), 1)
            self.assertNotIn("author_id", rows[0])
            self.assertNotIn("text", rows[0])
            self.assertNotIn("quote", rows[0])
            self.assertNotIn("evidence_quote", rows[0])


if __name__ == "__main__":
    unittest.main()
