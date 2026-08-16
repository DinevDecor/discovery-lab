"""The Calendar Events Ledger: an append-only event history plus a
snapshot fully rebuilt from it - the same split already established by
constraint_change_observatory.ledger, business_candidate_analyst's
candidate_events.jsonl/candidates.json, and
constraint-archaeology-agents' (dormant) findings_ledger.py.

  data/calendar_events.jsonl     append-only, one entry per line, never
                                  rewritten. A revision to candidate_id X
                                  is a NEW line, never an edit of an old one.
  data/calendar_candidates.json  fully replayed from the event log. Never
                                  hand-edited, never read-modify-written.

candidate_id is a stable lineage key. Multiple ledger lines may share a
candidate_id - each is a full revision snapshot (a new T_shock forecast, a
delay recompute, an adversarial review outcome, a lifecycle transition);
the LATEST line for a given candidate_id is its current content, which is
exactly how "first_seen, status history, old and new T_shock, G_d/G_r
history, evidence used, rejected hypotheses, reviewer disagreement" (the
approved architecture review's state/history requirement) are recovered:
by reading the full ordered list of lines for one candidate_id, never by
overwriting a single record.

This is the only module (besides report.py) allowed to open a file in a
writing mode - enforced by tests/test_safety.py.
"""

from __future__ import annotations

import hashlib
import json
import os
from collections import defaultdict
from typing import Any, Dict, List, Optional

from .models import CalendarAssessment

LEDGER_VERSION = "1"


def make_entry_id(assessment: CalendarAssessment) -> str:
    """Deterministic id from candidate_id + canonical content
    (last_updated/first_seen excluded from the hash material would be
    wrong here since a pure-timestamp-only revision IS a real event worth
    a new line - e.g. 're-affirmed unchanged as of today'. Instead the
    caller controls idempotency by only calling append() when something
    actually changed; a byte-identical re-append (including timestamps)
    is still a no-op via `recorded_at` staying outside the hash, matching
    findings_ledger.make_finding_id's own reasoning)."""
    material = json.dumps(
        {"v": LEDGER_VERSION, "candidate_id": assessment.candidate_id, "content": assessment.to_dict()},
        sort_keys=True, ensure_ascii=False, default=str,
    )
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()[:32]
    return f"caw:{assessment.candidate_id}:{digest}"


class CalendarLedger:
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

    @property
    def known_count(self) -> int:
        return len(self._known_ids)

    def all_entries(self) -> List[Dict[str, Any]]:
        return list(self._entries)

    def append(self, assessment: CalendarAssessment, recorded_at: str) -> bool:
        """Append one entry. Returns True if written, False if this exact
        content for this candidate_id was already present (idempotent
        re-append)."""
        entry_id = make_entry_id(assessment)
        if entry_id in self._known_ids:
            return False
        row = {"entry_id": entry_id, "recorded_at": recorded_at, "record": assessment.to_dict()}
        os.makedirs(os.path.dirname(os.path.abspath(self.events_path)) or ".", exist_ok=True)
        with open(self.events_path, "a", encoding="utf-8") as f:  # append mode only
            f.write(json.dumps(row, sort_keys=True, ensure_ascii=False, default=str) + "\n")
        self._known_ids.add(entry_id)
        self._entries.append(row)
        return True

    def append_many(self, assessments, recorded_at: str) -> int:
        return sum(1 for a in assessments if self.append(a, recorded_at))


def rebuild_snapshot(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Pure function: replays the append-only log into the current-state
    view. `entries` must be in file order (append-only, so file order is
    chronological).

    Returns {"current": [...], "superseded": [...], "history": {candidate_id: [entry, ...]}}
    - superseded candidates are never dropped, only excluded from "current".
    """
    history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for e in entries:
        candidate_id = e["record"]["candidate_id"]
        history[candidate_id].append(e)

    latest_by_id: Dict[str, Dict[str, Any]] = {cid: lines[-1] for cid, lines in history.items()}

    superseded_ids: set = set()
    for cid, entry in latest_by_id.items():
        target = entry["record"].get("supersedes")
        if target and target in latest_by_id:
            superseded_ids.add(target)

    current = [latest_by_id[cid]["record"] for cid in sorted(latest_by_id) if cid not in superseded_ids]
    superseded = [latest_by_id[cid]["record"] for cid in sorted(latest_by_id) if cid in superseded_ids]
    return {
        "current": current,
        "superseded": superseded,
        "history": {cid: list(lines) for cid, lines in history.items()},
    }


def persist_snapshot(path: str, snapshot: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    payload = {"current": snapshot["current"], "superseded": snapshot["superseded"]}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=True)


def load_snapshot(path: str) -> Optional[Dict[str, Any]]:
    """Read-only load of this package's OWN previously written snapshot."""
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def current_assessments(entries: List[Dict[str, Any]]) -> List[CalendarAssessment]:
    snap = rebuild_snapshot(entries)
    return [CalendarAssessment.from_dict(d) for d in snap["current"]]
