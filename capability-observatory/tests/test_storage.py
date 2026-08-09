import _pathsetup  # noqa: F401
import json
import os
import tempfile
import unittest

from capability_observatory.storage import AppendOnlyStore


class StorageTests(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self._tmpdir.name, "records.jsonl")

    def tearDown(self):
        self._tmpdir.cleanup()

    def test_append_writes_a_line(self):
        store = AppendOnlyStore(self.path, id_field="id")
        written = store.append({"id": "a", "value": 1})
        self.assertTrue(written)
        self.assertEqual(store.known_count, 1)
        with open(self.path, encoding="utf-8") as fh:
            lines = fh.readlines()
        self.assertEqual(len(lines), 1)

    def test_append_is_idempotent_for_the_same_id(self):
        store = AppendOnlyStore(self.path, id_field="id")
        store.append({"id": "a", "value": 1})
        written_again = store.append({"id": "a", "value": 999})
        self.assertFalse(written_again)
        self.assertEqual(store.known_count, 1)
        with open(self.path, encoding="utf-8") as fh:
            lines = fh.readlines()
        self.assertEqual(len(lines), 1)
        # The original line is untouched -- a second append with the same id
        # never rewrites the first record's content.
        self.assertEqual(json.loads(lines[0])["value"], 1)

    def test_never_rewrites_or_deletes_existing_lines(self):
        store = AppendOnlyStore(self.path, id_field="id")
        store.append({"id": "a", "value": 1})
        store.append({"id": "b", "value": 2})
        with open(self.path, encoding="utf-8") as fh:
            before = fh.read()
        store.append({"id": "c", "value": 3})
        with open(self.path, encoding="utf-8") as fh:
            after = fh.read()
        self.assertTrue(after.startswith(before))
        self.assertEqual(len(after.splitlines()), 3)

    def test_a_fresh_store_reloads_known_ids_from_disk(self):
        store1 = AppendOnlyStore(self.path, id_field="id")
        store1.append({"id": "a", "value": 1})
        store2 = AppendOnlyStore(self.path, id_field="id")
        self.assertTrue(store2.has("a"))
        self.assertFalse(store2.append({"id": "a", "value": 2}))

    def test_read_all_returns_every_record(self):
        store = AppendOnlyStore(self.path, id_field="id")
        store.append({"id": "a", "value": 1})
        store.append({"id": "b", "value": 2})
        rows = store.read_all()
        self.assertEqual(len(rows), 2)
        self.assertEqual({r["id"] for r in rows}, {"a", "b"})

    def test_read_all_on_missing_file_returns_empty_list(self):
        store = AppendOnlyStore(self.path, id_field="id")
        self.assertEqual(store.read_all(), [])

    def test_append_requires_a_non_empty_id(self):
        store = AppendOnlyStore(self.path, id_field="id")
        with self.assertRaises(ValueError):
            store.append({"value": 1})

    def test_corrupt_line_is_skipped_not_repaired(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as fh:
            fh.write('{"id": "a", "value": 1}\n')
            fh.write("not valid json\n")
        store = AppendOnlyStore(self.path, id_field="id")
        self.assertEqual(store.known_count, 1)
        rows = store.read_all()
        self.assertEqual(len(rows), 1)
        with open(self.path, encoding="utf-8") as fh:
            content = fh.read()
        self.assertIn("not valid json", content)  # untouched, never "fixed"


if __name__ == "__main__":
    unittest.main()
