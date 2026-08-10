"""The Business Candidate Registry: an append-only event log plus a
snapshot fully rebuilt from it every run - the same split Constraint
Archaeology itself uses between findings.jsonl (append-only, this
package's precedent) and anomalies.json (rebuilt snapshot).

  data/candidate_events.jsonl   append-only, one line per event, never
                                 rewritten. A later run's decision is a
                                 NEW event, never an edit of an old one.
  data/candidates.json          fully replayed from the event log. Never
                                 hand-edited, never read-modify-written.

This is the only module (besides report.py) allowed to open a file in a
writing mode - enforced by tests/test_safety.py.
"""

from __future__ import annotations

import hashlib
import json
import os
from collections import defaultdict
from typing import Any, Dict, Iterable, List, Optional

from .models import Candidate, CandidateEvent

EVENT_KINDS = frozenset({
    "candidate_created",
    "state_changed",
    "evidence_reassessed",
    "candidates_merged",
})


def make_event_id(event_type: str, candidate_id: str, identity: Dict[str, Any]) -> str:
    """Deterministic id from the event's logical identity (never includes
    recorded_at) - a rerun over unchanged evidence that reaches the exact
    same decision produces the exact same id and is skipped by append(),
    so re-running this tool on a quiet day does not spam the log."""
    material = json.dumps({"event_type": event_type, "candidate_id": candidate_id, "identity": identity},
                           sort_keys=True, ensure_ascii=False, default=str)
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()[:24]
    return f"{event_type}:{candidate_id}:{digest}"


class CandidateRegistry:
    def __init__(self, events_path: str):
        self.events_path = events_path
        self._known_ids: set = set()
        self._events: List[Dict[str, Any]] = []
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
                    continue
                self._events.append(row)
                eid = row.get("event_id")
                if isinstance(eid, str):
                    self._known_ids.add(eid)

    def has(self, event_id: str) -> bool:
        return event_id in self._known_ids

    def all_events(self) -> List[Dict[str, Any]]:
        return list(self._events)

    def append(self, event: CandidateEvent) -> bool:
        if event.event_type not in EVENT_KINDS:
            raise ValueError(f"unknown event_type: {event.event_type!r}")
        if event.event_id in self._known_ids:
            return False
        os.makedirs(os.path.dirname(os.path.abspath(self.events_path)) or ".", exist_ok=True)
        row = event.to_dict()
        with open(self.events_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")
        self._known_ids.add(event.event_id)
        self._events.append(row)
        return True

    def append_many(self, events: Iterable[CandidateEvent]) -> int:
        return sum(1 for e in events if self.append(e))


def rebuild_snapshot(events: List[Dict[str, Any]]) -> List[Candidate]:
    """Pure function: replays the append-only log into the current-state
    view. Order of `events` must be file order (chronological, since the
    log is append-only)."""
    by_candidate: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for e in events:
        by_candidate[e["candidate_id"]].append(e)

    candidates: Dict[str, Candidate] = {}
    for cid in sorted(by_candidate):
        evs = by_candidate[cid]
        cand: Optional[Candidate] = None
        for e in evs:
            etype = e["event_type"]
            payload = e.get("payload", {})
            if etype == "candidate_created":
                cand = Candidate(
                    candidate_id=cid,
                    state=payload.get("state", "WATCH"),
                    created_at=e["recorded_at"],
                    updated_at=e["recorded_at"],
                    anomaly_ids=list(payload.get("anomaly_ids", [])),
                    observation_ids=list(payload.get("observation_ids", [])),
                    signature=payload.get("signature"),
                    dimensions=payload.get("dimensions", {}),
                )
            if cand is None:
                continue
            cand.updated_at = e["recorded_at"]
            cand.history.append({
                "event_id": e["event_id"], "event_type": etype,
                "recorded_at": e["recorded_at"], "reason": e.get("reason", ""),
                "derived_from": list(e.get("derived_from", [])),
            })
            if etype == "state_changed":
                cand.state = payload["to_state"]
                cand.dimensions = payload.get("dimensions", cand.dimensions)
                cand.anomaly_ids = sorted(set(cand.anomaly_ids) | set(payload.get("anomaly_ids", [])))
                cand.observation_ids = sorted(set(cand.observation_ids) | set(payload.get("observation_ids", [])))
                if cand.state == "REJECTED":
                    cand.rejected_reason = e.get("reason", "")
                merged_from = payload.get("merged_from")
                if merged_from:
                    items = merged_from if isinstance(merged_from, list) else [merged_from]
                    cand.merged_from = sorted(set(cand.merged_from) | set(items))
            elif etype == "evidence_reassessed":
                cand.dimensions = payload.get("dimensions", cand.dimensions)
                cand.anomaly_ids = sorted(set(cand.anomaly_ids) | set(payload.get("anomaly_ids", [])))
                cand.observation_ids = sorted(set(cand.observation_ids) | set(payload.get("observation_ids", [])))
                merged_from = payload.get("merged_from")
                if merged_from:
                    items = merged_from if isinstance(merged_from, list) else [merged_from]
                    cand.merged_from = sorted(set(cand.merged_from) | set(items))
            elif etype == "candidates_merged":
                cand.merged_into = payload.get("merged_into")
        if cand is not None:
            candidates[cid] = cand
    return [candidates[cid] for cid in sorted(candidates)]


def persist_snapshot(path: str, candidates: List[Candidate]) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump([c.to_dict() for c in candidates], f, ensure_ascii=False, indent=2, sort_keys=True)


def load_snapshot(path: str) -> List[Dict[str, Any]]:
    """Read-only load of this package's OWN previously written snapshot -
    used only to diff against the current run for the strengthened/
    weakened report sections. Never reads any Constraint Archaeology
    file."""
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else []
