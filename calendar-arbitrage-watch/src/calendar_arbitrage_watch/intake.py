"""Validates a human/AI-executor-submitted capture/assessment file and
turns it into a CalendarAssessment.

Capture (fetching regulatory filings, permit registries, accreditation
listings, grid-connection queues, tender portals) happens OUTSIDE this
package entirely, the same capture/processing split reality-sensor and
capability-observatory already use - a human or an AI executor with
explicit task authorization visits the source and writes a submission
JSON file; this module only ever reads that file from local disk. No
network client anywhere in this package (enforced by tests/test_safety.py).

JSON only - no third-party parser dependency, matching this repo's
established convention (constraint-archaeology-agents/README.md,
constraint_change_observatory/intake.py).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List

from .models import CATEGORIES, MODES, SHOCK_TYPES, CalendarAssessment


class IntakeError(ValueError):
    """Raised when a submission fails structural validation."""


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    violations: List[str]
    assessment: Any = None  # CalendarAssessment when ok is True


REQUIRED_TOP_LEVEL = ("candidate_id", "mode", "category", "title")


def validate_submission(data: Dict[str, Any]) -> ValidationResult:
    """Structural validation only - never coerces a value to make it
    pass, never fabricates a missing field. Every violation is listed;
    the caller decides whether to reject the whole submission (see
    cli.py, which rejects loudly per-file the same way
    constraint_change_observatory's `add` command does)."""
    violations: List[str] = []

    for key in REQUIRED_TOP_LEVEL:
        if not data.get(key):
            violations.append(f"missing required field: {key}")

    mode = data.get("mode")
    if mode is not None and mode not in MODES:
        violations.append(f"mode must be one of {MODES}, got {mode!r}")

    category = data.get("category")
    if category is not None and category not in CATEGORIES:
        violations.append(f"category must be one of {CATEGORIES}, got {category!r}")

    shock_forecast = data.get("shock_forecast") or {}
    shock_type = shock_forecast.get("shock_type")
    if shock_type is not None and shock_type not in SHOCK_TYPES:
        violations.append(f"shock_forecast.shock_type must be one of {SHOCK_TYPES}, got {shock_type!r}")

    date_bound = shock_forecast.get("date_bound") or {}
    if shock_type == "DATED" and date_bound.get("evidence_status") not in (None, "INSUFFICIENT_DATA"):
        earliest = date_bound.get("earliest")
        latest = date_bound.get("latest")
        if earliest and latest and earliest != latest:
            violations.append(
                "shock_forecast.date_bound: shock_type=DATED requires earliest == latest "
                "(a single known date), got an interval - use ROLLING for a genuine forecast range")

    if not data.get("evidence_ids") and not data.get("provenance"):
        violations.append("submission cites no evidence_ids and no provenance - every assessment must cite something")

    if violations:
        return ValidationResult(ok=False, violations=violations, assessment=None)

    assessment = CalendarAssessment.from_dict(data)
    return ValidationResult(ok=True, violations=[], assessment=assessment)


def load_submissions(path: str) -> List[Dict[str, Any]]:
    """Loads one submission JSON file - a single object or a JSON array
    of objects. Malformed JSON raises IntakeError with the path named, so
    the caller can report exactly which file failed (never silently
    skipped)."""
    with open(path, encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as exc:
            raise IntakeError(f"{path}: not valid JSON ({exc})") from exc
    if isinstance(data, dict):
        return [data]
    if isinstance(data, list):
        return data
    raise IntakeError(f"{path}: submission file must be a JSON object or array of objects")
