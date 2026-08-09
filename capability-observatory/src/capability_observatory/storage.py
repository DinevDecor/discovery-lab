"""Narrow append-only JSONL store.

Mirrors constraint-archaeology-agents/findings_ledger.py's own
FindingsLedger discipline exactly: known ids are loaded once at
construction, append() is a no-op for an id already present, and the only
write path opens the file in "a" mode. There is no read-modify-write path
anywhere in this class -- a correction is always a NEW record, never an
edit of an old one, and nothing here ever deletes a line.

Not safe against two writers appending concurrently (same tradeoff, same
reasoning as FindingsLedger: today's runs are one process at a time, and an
unused lock is a maintenance cost with no current benefit).
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List


class AppendOnlyStore:
    def __init__(self, path: str, id_field: str):
        self.path = path
        self.id_field = id_field
        self._known: set = set()
        self._load_known_ids()

    def _load_known_ids(self) -> None:
        if not os.path.exists(self.path):
            return
        with open(self.path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    # A corrupt line is history too -- skipped for the id
                    # set, never rewritten to "fix" it.
                    continue
                rid = rec.get(self.id_field)
                if isinstance(rid, str):
                    self._known.add(rid)

    def has(self, record_id: str) -> bool:
        return record_id in self._known

    @property
    def known_count(self) -> int:
        return len(self._known)

    def append(self, record: Dict[str, Any]) -> bool:
        """Append one record. Returns True if written, False if the id was
        already present (idempotent retry, not an error)."""
        record_id = record.get(self.id_field)
        if not isinstance(record_id, str) or not record_id:
            raise ValueError(f"record missing non-empty {self.id_field!r}")
        if record_id in self._known:
            return False

        os.makedirs(os.path.dirname(os.path.abspath(self.path)) or ".", exist_ok=True)
        with open(self.path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n")
            fh.flush()
        self._known.add(record_id)
        return True

    def read_all(self) -> List[Dict[str, Any]]:
        """Read side, used for computing metrics and continuity checks.
        Never used to rewrite the file."""
        if not os.path.exists(self.path):
            return []
        rows: List[Dict[str, Any]] = []
        with open(self.path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return rows
