"""Append-only writer for `case-claim-kernel/data/artifacts.jsonl`.

Mirrors `ca_agents.findings_ledger.FindingsLedger` and
`calendar_arbitrage_watch.ledger.CalendarLedger` exactly: known ids loaded
once at construction, `append()` is a no-op for an id already present
(idempotent), the only write path opens the file in `"a"` mode, and there
is no code anywhere in this module that reads the file and writes it back.
A logically newer wrap of the same source record produces the SAME
`artifact_id` (identity.py) and is therefore a no-op re-append, not a
second, near-duplicate line - re-running identity assignment is safe to
run every day.

This is the ONLY module in this package allowed to open a file in a
writing mode, and the only path it ever writes to is its own
`case-claim-kernel/data/`. Enforced here by convention and by
tests/test_safety.py, the same split every other package in this repo
already uses for its own ledger module.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Iterable, List

from .models import ArtifactEnvelope


class ArtifactLedger:
    def __init__(self, path: str):
        self.path = path
        self._known: set = set()
        self._entries: List[Dict[str, Any]] = []
        self._load_known()

    def _load_known(self) -> None:
        if not os.path.exists(self.path):
            return
        with open(self.path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    # A corrupt line is history too - skip it for the id
                    # set, never rewrite the file to "fix" it.
                    continue
                self._entries.append(row)
                aid = row.get("artifact_id")
                if isinstance(aid, str):
                    self._known.add(aid)

    def has(self, artifact_id: str) -> bool:
        return artifact_id in self._known

    @property
    def known_count(self) -> int:
        return len(self._known)

    def all_entries(self) -> List[Dict[str, Any]]:
        return list(self._entries)

    def append(self, envelope: ArtifactEnvelope) -> bool:
        """Append one envelope. Returns True if written, False if this
        artifact_id was already present (idempotent re-append)."""
        if envelope.artifact_id in self._known:
            return False
        os.makedirs(os.path.dirname(os.path.abspath(self.path)) or ".", exist_ok=True)
        line = json.dumps(envelope.to_dict(), sort_keys=True, ensure_ascii=False, default=str)
        with open(self.path, "a", encoding="utf-8") as fh:  # append mode only
            fh.write(line + "\n")
        self._known.add(envelope.artifact_id)
        self._entries.append(envelope.to_dict())
        return True

    def append_many(self, envelopes: Iterable[ArtifactEnvelope]) -> int:
        return sum(1 for e in envelopes if self.append(e))
