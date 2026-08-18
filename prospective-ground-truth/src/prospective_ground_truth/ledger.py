"""Two append-only ledgers plus a rebuilt snapshot - same split already
established by `constraint_change_observatory.ledger`/
`adversarial_review_kernel.ledger`:

  data/cases.jsonl         append-only, one ProspectiveCase per line,
                            never rewritten. This is the ONLY place a
                            case's T0Freeze content is ever written -
                            resolving a case never touches this file.
  data/resolutions.jsonl   append-only, one Resolution per line, never
                            rewritten - a separate file, so it is
                            structurally impossible for appending a
                            Resolution to mutate a case's frozen T0
                            content (see module docstring on ProspectiveCase
                            in models.py).
  data/cases.json          fully replayed from both event logs -
                            never hand-edited, never read-modify-written.
                            Carries each case's DERIVED status (see
                            derive_status below) - status is a view, not
                            stored ledger content.

This is the only module (besides the CLI's report step) allowed to open
a file in a writing mode - enforced by tests/test_safety.py.
"""

from __future__ import annotations

import json
import os
from datetime import date
from typing import Any, Dict, List, Optional

from .models import (
    OUTCOME_EXPIRED_UNRESOLVED,
    OUTCOME_INVALIDATED,
    STATUS_AWAITING_OUTCOME,
    STATUS_EXPIRED_UNRESOLVED,
    STATUS_INVALIDATED,
    STATUS_OPEN,
    STATUS_RESOLVED,
    ProspectiveCase,
    Resolution,
)
from .validator import ValidationError, validate_prospective_case, validate_resolution


class CaseLedger:
    def __init__(self, path: str):
        self.path = path
        self._known: set = set()
        self._entries: List[Dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        if not os.path.exists(self.path):
            return
        with open(self.path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                self._entries.append(row)
                cid = row.get("prospective_case_id")
                if isinstance(cid, str):
                    self._known.add(cid)

    def has(self, prospective_case_id: str) -> bool:
        return prospective_case_id in self._known

    def all_entries(self) -> List[Dict[str, Any]]:
        return list(self._entries)

    def append(self, case: ProspectiveCase) -> bool:
        """Validates, then appends. Returns False (no-op) if this exact
        case_id is already known - idempotent re-registration, never a
        silent overwrite of a case's frozen T0 content."""
        violations = validate_prospective_case(case)
        if violations:
            raise ValidationError(case.prospective_case_id, violations)
        if case.prospective_case_id in self._known:
            return False
        os.makedirs(os.path.dirname(os.path.abspath(self.path)) or ".", exist_ok=True)
        line = json.dumps(case.to_dict(), sort_keys=True, ensure_ascii=False, default=str)
        with open(self.path, "a", encoding="utf-8") as f:  # append mode only
            f.write(line + "\n")
        self._known.add(case.prospective_case_id)
        self._entries.append(case.to_dict())
        return True


class ResolutionLedger:
    def __init__(self, path: str):
        self.path = path
        self._known: set = set()
        self._entries: List[Dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        if not os.path.exists(self.path):
            return
        with open(self.path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                self._entries.append(row)
                rid = row.get("resolution_id")
                if isinstance(rid, str):
                    self._known.add(rid)

    def has(self, resolution_id: str) -> bool:
        return resolution_id in self._known

    def all_entries(self) -> List[Dict[str, Any]]:
        return list(self._entries)

    def for_case(self, prospective_case_id: str) -> List[Dict[str, Any]]:
        return [e for e in self._entries if e.get("prospective_case_id") == prospective_case_id]

    def append(self, resolution: Resolution) -> bool:
        violations = validate_resolution(resolution)
        if violations:
            raise ValidationError(resolution.resolution_id, violations)
        if resolution.resolution_id in self._known:
            return False
        os.makedirs(os.path.dirname(os.path.abspath(self.path)) or ".", exist_ok=True)
        line = json.dumps(resolution.to_dict(), sort_keys=True, ensure_ascii=False, default=str)
        with open(self.path, "a", encoding="utf-8") as f:  # append mode only
            f.write(line + "\n")
        self._known.add(resolution.resolution_id)
        self._entries.append(resolution.to_dict())
        return True


def derive_status(case: Dict[str, Any], resolutions_for_case: List[Dict[str, Any]],
                   as_of_date: Optional[str] = None) -> str:
    """Pure function: a case's status is always computed from ledger
    content, never stored as mutable data on the case itself (see module
    docstring). The latest resolution for a case (by resolved_at) decides
    RESOLVED/EXPIRED_UNRESOLVED/INVALIDATED; absent any resolution, the
    case is OPEN until the expected window opens, then AWAITING_OUTCOME."""
    if resolutions_for_case:
        latest = max(resolutions_for_case, key=lambda r: r.get("resolved_at", ""))
        outcome = latest.get("outcome")
        if outcome == OUTCOME_EXPIRED_UNRESOLVED:
            return STATUS_EXPIRED_UNRESOLVED
        if outcome == OUTCOME_INVALIDATED:
            return STATUS_INVALIDATED
        return STATUS_RESOLVED  # POSITIVE | NEGATIVE | AMBIGUOUS

    today = as_of_date or date.today().isoformat()
    earliest = case.get("expected_resolution", {}).get("expected_resolution_window", {}).get("earliest")
    if earliest and today >= earliest:
        return STATUS_AWAITING_OUTCOME
    return STATUS_OPEN


def rebuild_snapshot(case_entries: List[Dict[str, Any]], resolution_entries: List[Dict[str, Any]],
                      as_of_date: Optional[str] = None) -> Dict[str, Any]:
    """Replays both append-only logs into a current-state view. Never
    written back into either .jsonl file - only ever persisted to
    data/cases.json, which is itself always fully rebuilt, never
    read-modify-written."""
    by_case: Dict[str, List[Dict[str, Any]]] = {}
    for r in resolution_entries:
        by_case.setdefault(r["prospective_case_id"], []).append(r)

    cases = []
    for c in case_entries:
        status = derive_status(c, by_case.get(c["prospective_case_id"], []), as_of_date)
        cases.append({**c, "status": status})
    return {"cases": cases, "resolutions": list(resolution_entries)}


def persist_snapshot(path: str, snapshot: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2, sort_keys=True)
