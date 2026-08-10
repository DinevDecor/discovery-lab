"""Manual intake path: load ConstraintChangeRecord(s) from a JSON file,
validate, append the valid ones to the ledger. Deterministic, no network,
no LLM - a human (or an agent in one directed research session, per
design doc §17) authors the JSON by hand and runs this.

Each record in a batch file is validated and appended independently: one
bad record in a file does not block the good ones in the same file, and
every outcome (added / duplicate / rejected-with-reasons) is reported
back explicitly - "invalid records rejected loudly," never silently
dropped.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List

from .ledger import ConstraintLedger
from .schema import ConstraintChangeRecord
from .validator import validate

ADDED = "added"
DUPLICATE = "duplicate"
REJECTED = "rejected"


@dataclass(frozen=True)
class IntakeResult:
    record_id: str
    outcome: str  # ADDED | DUPLICATE | REJECTED
    violations: List[str]


def load_records_from_file(path: str) -> List[ConstraintChangeRecord]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    rows: List[Dict[str, Any]] = data if isinstance(data, list) else [data]
    records = []
    for i, row in enumerate(rows):
        if "record_id" not in row:
            raise ValueError(f"{path}: entry {i} has no record_id - cannot load")
        records.append(ConstraintChangeRecord.from_dict(row))
    return records


def validate_file(path: str) -> List[IntakeResult]:
    """Dry run: validate every record in the file, append nothing."""
    results = []
    for record in load_records_from_file(path):
        violations = validate(record)
        results.append(IntakeResult(record.record_id, REJECTED if violations else ADDED, violations))
    return results


def intake_file(path: str, ledger: ConstraintLedger, recorded_at: str) -> List[IntakeResult]:
    results = []
    for record in load_records_from_file(path):
        violations = validate(record)
        if violations:
            results.append(IntakeResult(record.record_id, REJECTED, violations))
            continue
        added = ledger.append(record, recorded_at)
        results.append(IntakeResult(record.record_id, ADDED if added else DUPLICATE, []))
    return results


def intake_files(paths: List[str], ledger: ConstraintLedger, recorded_at: str) -> List[IntakeResult]:
    results = []
    for path in paths:
        results.extend(intake_file(path, ledger, recorded_at))
    return results
