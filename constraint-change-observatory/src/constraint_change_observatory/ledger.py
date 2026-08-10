"""The Constraint Change Ledger: an append-only event history plus a
snapshot fully rebuilt from it - the same split already established by
`constraint-archaeology-agents`' findings.jsonl/anomalies.json and
`business-candidate-analyst`'s candidate_events.jsonl/candidates.json.

  data/constraint_events.jsonl   append-only, one entry per line, never
                                  rewritten. A revision to record_id X is a
                                  NEW line, never an edit of an old one.
  data/constraints.json          fully replayed from the event log. Never
                                  hand-edited, never read-modify-written.

record_id is a stable lineage key (design doc §8: "stable per
constraint+activity"). Multiple ledger lines may share a record_id - each
is a full revision snapshot of that record at the time it was authored;
the LATEST line for a given record_id is its current content. A
genuinely different claim that should retire an OLDER, DIFFERENTLY-ID'd
record uses `supersedes` (see schema.py's module docstring for why this
replaces the design doc's `superseded_by`). Neither mechanism ever
mutates a historical line - "conflicting claims are preserved rather than
overwritten" is enforced structurally here, not by review discipline.

This is the only module (besides report.py) allowed to open a file in a
writing mode - enforced by tests/test_safety.py.
"""

from __future__ import annotations

import hashlib
import json
import os
from collections import defaultdict
from typing import Any, Dict, List, Optional

from .schema import ConstraintChangeRecord


def make_entry_id(record: ConstraintChangeRecord) -> str:
    """Deterministic id from record_id + canonical content (recorded_at
    excluded so a byte-identical re-append of the same content is a no-op,
    matching findings_ledger.make_finding_id's own reasoning)."""
    material = json.dumps({"record_id": record.record_id, "content": record.to_dict()},
                           sort_keys=True, ensure_ascii=False, default=str)
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()[:32]
    return f"ccr:{record.record_id}:{digest}"


class ConstraintLedger:
    def __init__(self, events_path: str):
        self.events_path = events_path
        self._known_ids: set = set()
        self._entries: List[Dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        if not os.path.exists(self.events_path):
            return
        with open(self.events_path, encoding="utf-8") as f:
            for line in f:
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
                eid = row.get("entry_id")
                if isinstance(eid, str):
                    self._known_ids.add(eid)

    def has(self, entry_id: str) -> bool:
        return entry_id in self._known_ids

    def all_entries(self) -> List[Dict[str, Any]]:
        return list(self._entries)

    def append(self, record: ConstraintChangeRecord, recorded_at: str) -> bool:
        """Append one entry. Returns True if written, False if this exact
        content for this record_id was already present (idempotent
        re-append), matching FindingsLedger.append's own contract."""
        entry_id = make_entry_id(record)
        if entry_id in self._known_ids:
            return False
        row = {"entry_id": entry_id, "recorded_at": recorded_at, "record": record.to_dict()}
        os.makedirs(os.path.dirname(os.path.abspath(self.events_path)) or ".", exist_ok=True)
        with open(self.events_path, "a", encoding="utf-8") as f:  # append mode only
            f.write(json.dumps(row, sort_keys=True, ensure_ascii=False, default=str) + "\n")
        self._known_ids.add(entry_id)
        self._entries.append(row)
        return True


def rebuild_snapshot(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Pure function: replays the append-only log into the current-state
    view. `entries` must be in file order (append-only, so file order is
    chronological).

    Returns {"current": [record dict, ...], "superseded": [record dict, ...],
    "history": {record_id: [entry, ...]}} - superseded records are never
    dropped, only excluded from "current" (see module docstring)."""
    history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for e in entries:
        record_id = e["record"]["record_id"]
        history[record_id].append(e)

    # Latest line per record_id lineage is that lineage's current content.
    latest_by_id: Dict[str, Dict[str, Any]] = {rid: lines[-1] for rid, lines in history.items()}

    # A record_id is superseded if some OTHER record_id's latest entry
    # declares supersedes == this record_id.
    superseded_ids: set = set()
    for rid, entry in latest_by_id.items():
        target = entry["record"].get("supersedes")
        if target and target in latest_by_id:
            superseded_ids.add(target)

    current = [latest_by_id[rid]["record"] for rid in sorted(latest_by_id) if rid not in superseded_ids]
    superseded = [latest_by_id[rid]["record"] for rid in sorted(latest_by_id) if rid in superseded_ids]
    return {
        "current": current,
        "superseded": superseded,
        "history": {rid: [e for e in lines] for rid, lines in history.items()},
    }


def persist_snapshot(path: str, snapshot: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    payload = {
        "current": snapshot["current"],
        "superseded": snapshot["superseded"],
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=True)


def load_snapshot(path: str) -> Optional[Dict[str, Any]]:
    """Read-only load of this package's OWN previously written snapshot."""
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def current_records(entries: List[Dict[str, Any]]) -> List[ConstraintChangeRecord]:
    snap = rebuild_snapshot(entries)
    return [ConstraintChangeRecord.from_dict(d) for d in snap["current"]]
