"""End-to-end test of the `process` command: drop submission files into
incoming/, run process, verify the append-only stores and the rendered
report -- the same path the GitHub Actions workflow exercises. Entirely
offline: every submission's raw_content is a literal fixture string, never
fetched.
"""

import _pathsetup  # noqa: F401
import json
import os
import tempfile
import unittest

from capability_observatory import cli

PANEL = {
    "panel_version": "test-v1",
    "items": [
        {
            "panel_item_id": "T-001",
            "provider": "provider_a",
            "identity_fields": ["manufacturer", "mpn"],
        },
        {
            "panel_item_id": "T-002",
            "provider": "provider_b",
            "identity_fields": ["manufacturer", "mpn"],
        },
        {
            "panel_item_id": "T-003",
            "provider": "provider_a",
            "identity_fields": ["manufacturer", "mpn"],
        },
    ],
}


def _write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh)


class CliProcessTests(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.root = self._tmpdir.name
        _write_json(os.path.join(self.root, "config", "panel.json"), PANEL)
        os.makedirs(os.path.join(self.root, "incoming"), exist_ok=True)

    def tearDown(self):
        self._tmpdir.cleanup()

    def _submit(self, filename, submission):
        _write_json(os.path.join(self.root, "incoming", filename), submission)

    def test_process_records_captures_and_moves_files_to_processed(self):
        self._submit("t001.json", {
            "panel_item_id": "T-001",
            "source": "provider_a",
            "source_url": "https://example.test/t001",
            "fetched_at": "2026-08-09T00:00:00Z",
            "capture_outcome": "ok",
            "executor": "test",
            "raw_content": "content-1",
            "observation": {
                "price": 10.0,
                "availability": "in_stock",
                "identity_values": {"manufacturer": "Acme", "mpn": "M1"},
            },
        })
        self._submit("t002.json", {
            "panel_item_id": "T-002",
            "source": "provider_b",
            "source_url": "https://example.test/t002",
            "fetched_at": "2026-08-09T00:00:00Z",
            "capture_outcome": "access_blocked",
            "executor": "test",
            "raw_content": "blocked",
        })

        rc = cli.main(["--root", self.root, "process"])
        self.assertEqual(rc, 0)

        captures = os.path.join(self.root, "data", "captures.jsonl")
        observations = os.path.join(self.root, "data", "observations.jsonl")
        with open(captures, encoding="utf-8") as fh:
            capture_rows = [json.loads(l) for l in fh if l.strip()]
        with open(observations, encoding="utf-8") as fh:
            observation_rows = [json.loads(l) for l in fh if l.strip()]

        self.assertEqual(len(capture_rows), 2)
        self.assertEqual(len(observation_rows), 1)  # only the ok capture

        self.assertTrue(os.path.exists(os.path.join(self.root, "incoming", "processed", "t001.json")))
        self.assertTrue(os.path.exists(os.path.join(self.root, "incoming", "processed", "t002.json")))
        self.assertFalse(os.path.exists(os.path.join(self.root, "incoming", "t001.json")))

    def test_process_writes_a_machine_and_human_readable_report(self):
        self._submit("t003.json", {
            "panel_item_id": "T-003",
            "source": "provider_a",
            "source_url": "https://example.test/t003",
            "fetched_at": "2026-08-09T00:00:00Z",
            "capture_outcome": "ok",
            "executor": "test",
            "raw_content": "content-3",
            "observation": {
                "price": 20.0,
                "availability": "in_stock",
                "identity_values": {"manufacturer": "Acme", "mpn": "M3"},
            },
        })
        cli.main(["--root", self.root, "process"])

        summary_path = os.path.join(self.root, "reports", "latest-summary.json")
        self.assertTrue(os.path.exists(summary_path))
        with open(summary_path, encoding="utf-8") as fh:
            summary = json.load(fh)
        self.assertEqual(summary["observability"]["panel_size"], 3)
        self.assertEqual(summary["observability"]["observed_count"], 1)

        md_files = [f for f in os.listdir(os.path.join(self.root, "reports")) if f.endswith(".md")]
        self.assertEqual(len(md_files), 1)

    def test_malformed_submission_is_rejected_not_silently_dropped(self):
        self._submit("bad.json", {"panel_item_id": "T-001", "capture_outcome": "ok"})  # missing required fields
        rc = cli.main(["--root", self.root, "process"])
        self.assertEqual(rc, 0)  # process still completes for the rest of the batch
        self.assertTrue(os.path.exists(os.path.join(self.root, "incoming", "rejected", "bad.json")))
        self.assertFalse(os.path.exists(os.path.join(self.root, "incoming", "bad.json")))

    def test_running_process_twice_on_the_same_submissions_is_idempotent(self):
        submission = {
            "panel_item_id": "T-001",
            "source": "provider_a",
            "source_url": "https://example.test/t001",
            "fetched_at": "2026-08-09T00:00:00Z",
            "capture_outcome": "ok",
            "executor": "test",
            "raw_content": "content-1",
            "observation": {
                "price": 10.0,
                "availability": "in_stock",
                "identity_values": {"manufacturer": "Acme", "mpn": "M1"},
            },
        }
        self._submit("t001.json", submission)
        cli.main(["--root", self.root, "process"])

        # Re-submit the identical capture a second time, in a fresh incoming/ file.
        self._submit("t001-retry.json", submission)
        cli.main(["--root", self.root, "process"])

        with open(os.path.join(self.root, "data", "captures.jsonl"), encoding="utf-8") as fh:
            rows = [json.loads(l) for l in fh if l.strip()]
        self.assertEqual(len(rows), 1)  # same capture_id both times -- no duplicate


if __name__ == "__main__":
    unittest.main()
