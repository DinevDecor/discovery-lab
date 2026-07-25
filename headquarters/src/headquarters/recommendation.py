"""Recommendation Traceability + Evaluation (EXEC-004 §7, §8).

Persistent `HQ-000N` identifiers, stored in this tool's own
`reports/recommendation-log.json` (never anywhere in an observed
repository). A candidate that recurs across runs keeps its ID rather
than minting a new one every time, so a human can watch one
recommendation's status over time instead of a fresh list each run.

Status changes (`accepted` / `rejected` / `obsolete` / `implemented`)
are never made by this tool — they only ever come from a human editing
`reports/recommendation-decisions.json` by hand. If that file is empty
or missing, Recommendation Evaluation honestly reports that no
evaluation is possible yet, rather than inventing one.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path

from .prioritizer import Candidate


@dataclass
class RecommendationRecord:
    hq_id: str
    key: str
    title: str
    first_proposed: str
    last_proposed: str
    status: str = "proposed"
    times_proposed: int = 1


def load_log(path: Path) -> list[RecommendationRecord]:
    if not path.is_file():
        return []
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    return [RecommendationRecord(**r) for r in raw]


def save_log(path: Path, records: list[RecommendationRecord]) -> None:
    path.write_text(
        json.dumps([asdict(r) for r in records], indent=2, sort_keys=False),
        encoding="utf-8",
    )


def _next_hq_id(records: list[RecommendationRecord]) -> str:
    max_n = 0
    for r in records:
        if r.hq_id.startswith("HQ-"):
            try:
                max_n = max(max_n, int(r.hq_id.split("-")[1]))
            except (IndexError, ValueError):
                continue
    return f"HQ-{max_n + 1:04d}"


def assign_id(candidate: Candidate, records: list[RecommendationRecord], today: date) -> tuple[str, list[RecommendationRecord]]:
    """Return (hq_id, updated_records). Reuses an existing ID for the
    same candidate.key; otherwise mints the next sequential HQ-000N."""
    today_str = today.isoformat()
    for r in records:
        if r.key == candidate.key:
            r.last_proposed = today_str
            r.times_proposed += 1
            return r.hq_id, records

    hq_id = _next_hq_id(records)
    records.append(
        RecommendationRecord(
            hq_id=hq_id,
            key=candidate.key,
            title=candidate.title,
            first_proposed=today_str,
            last_proposed=today_str,
            status="proposed",
            times_proposed=1,
        )
    )
    return hq_id, records


def load_decisions(path: Path) -> dict[str, dict]:
    """Human-maintained: {"HQ-0001": {"accepted": true, "implemented":
    false, "useful": true, "obsolete": false, "incorrect": false,
    "note": "..."}}. Never written by this tool."""
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def evaluate(records: list[RecommendationRecord], decisions: dict[str, dict]) -> dict:
    if not decisions:
        return {
            "status": "INSUFFICIENT_EVIDENCE (no recommendation-decisions.json entries recorded yet)",
            "total_recommendations": len(records),
            "decisions_recorded": 0,
        }
    accepted = sum(1 for d in decisions.values() if d.get("accepted"))
    implemented = sum(1 for d in decisions.values() if d.get("implemented"))
    useful = sum(1 for d in decisions.values() if d.get("useful"))
    obsolete = sum(1 for d in decisions.values() if d.get("obsolete"))
    incorrect = sum(1 for d in decisions.values() if d.get("incorrect"))
    return {
        "status": "evaluated from recommendation-decisions.json",
        "total_recommendations": len(records),
        "decisions_recorded": len(decisions),
        "accepted": accepted,
        "implemented": implemented,
        "useful": useful,
        "obsolete": obsolete,
        "incorrect": incorrect,
    }
