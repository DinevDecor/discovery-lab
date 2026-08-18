"""Structural validation - same shape as
`constraint_change_observatory.validator`: `validate_*(record) ->
List[str]` returns violation messages (empty = valid), deterministic,
offline, no model call. `ValidationError` is raised by ledger.py when the
list is non-empty - invalid records are rejected loudly, never silently
dropped or coerced.

This module is where every hard rule from the task spec becomes an
actual, testable check rather than a convention someone could forget:
T0 packet hash must be internally consistent (Sec 5), resolution
criteria must all be present before a case is usable at all (Sec 6),
outcomes requiring a real-world claim must carry real evidence and an
authoritative source (Sec 7/8), resolver_type can never be a bare model
call (Sec 8), and AMBIGUOUS/EXPIRED_UNRESOLVED/INVALIDATED are first-class
values a case can legitimately resolve to, never silently coerced toward
NEGATIVE (Sec 15's "no premature calibration" - there is no scoring
logic anywhere in this package to do such a coercion in the first place).
"""

from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from .identity import make_prospective_case_id, make_resolution_id
from .models import OUTCOMES, OUTCOMES_REQUIRING_EVIDENCE, RESOLVER_TYPES, ProspectiveCase, Resolution
from .packet import compute_packet_sha256


class ValidationError(ValueError):
    def __init__(self, record_id: str, violations: List[str]):
        self.record_id = record_id
        self.violations = violations
        super().__init__(f"{record_id}: {len(violations)} validation violation(s):\n  - " +
                          "\n  - ".join(violations))


def _parse_date(value: str) -> Optional[date]:
    """Accepts a bare YYYY-MM-DD or a full ISO8601 timestamp (with an
    optional trailing 'Z'). Returns None (not an exception) on anything
    else, so callers can report a clean violation message instead of a
    traceback."""
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    try:
        if text.endswith("Z"):
            return datetime.fromisoformat(text[:-1] + "+00:00").date()
        if "T" in text:
            return datetime.fromisoformat(text).date()
        return date.fromisoformat(text)
    except ValueError:
        return None


def validate_prospective_case(case: ProspectiveCase) -> List[str]:
    violations: List[str] = []

    for field_name, value in (("domain", case.domain), ("proposition", case.proposition),
                               ("decision_relevance", case.decision_relevance)):
        if not (value or "").strip():
            violations.append(f"{field_name} must not be blank")

    t0_cutoff_date = _parse_date(case.t0.t0_cutoff)
    if t0_cutoff_date is None:
        violations.append(f"t0.t0_cutoff {case.t0.t0_cutoff!r} is not a valid date")

    if not case.t0.evidence:
        violations.append("t0.evidence must be non-empty - a case cannot be registered without frozen T0 evidence")
    for item in case.t0.evidence:
        if not (item.artifact_id or "").strip():
            violations.append("a t0.evidence item has a blank artifact_id")
        if not (item.citation or "").strip():
            violations.append(f"t0.evidence item {item.artifact_id!r} has a blank citation")
        if not (item.quote_or_summary or "").strip():
            violations.append(f"t0.evidence item {item.artifact_id!r} has a blank quote_or_summary")
        item_date = _parse_date(item.captured_at)
        if item_date is None:
            violations.append(f"t0.evidence item {item.artifact_id!r} has an invalid captured_at {item.captured_at!r}")
        elif t0_cutoff_date is not None and item_date > t0_cutoff_date:
            violations.append(
                f"t0.evidence item {item.artifact_id!r} has captured_at {item.captured_at!r} AFTER "
                f"t0_cutoff {case.t0.t0_cutoff!r} - post-T0 evidence cannot enter the frozen packet"
            )

    recomputed_hash = compute_packet_sha256(case.t0.t0_cutoff, case.t0.evidence)
    if case.t0.packet_sha256 != recomputed_hash:
        violations.append(
            f"t0.packet_sha256 {case.t0.packet_sha256!r} does not match the recomputed hash "
            f"{recomputed_hash!r} of t0_cutoff+evidence - the packet is not internally consistent"
        )

    er = case.expected_resolution
    if not (er.resolution_question or "").strip():
        violations.append("expected_resolution.resolution_question must not be blank")
    for cond_name, cond_value in (("positive_condition", er.positive_condition),
                                   ("negative_condition", er.negative_condition),
                                   ("ambiguous_condition", er.ambiguous_condition)):
        if not (cond_value or "").strip():
            violations.append(f"expected_resolution.{cond_name} must be pre-registered (non-blank) before the "
                               f"case can be used - resolution criteria may never be written after the outcome")

    earliest = _parse_date(er.expected_resolution_window.earliest)
    latest = _parse_date(er.expected_resolution_window.latest)
    if earliest is None:
        violations.append(f"expected_resolution_window.earliest {er.expected_resolution_window.earliest!r} "
                           f"is not a valid date")
    if latest is None:
        violations.append(f"expected_resolution_window.latest {er.expected_resolution_window.latest!r} "
                           f"is not a valid date")
    if earliest is not None and latest is not None and earliest > latest:
        violations.append("expected_resolution_window.earliest is after expected_resolution_window.latest")
    if earliest is not None and t0_cutoff_date is not None and earliest < t0_cutoff_date:
        violations.append("expected_resolution_window.earliest is before t0_cutoff - "
                           "a case cannot resolve before it was frozen")

    if not er.resolution_sources_expected:
        violations.append("expected_resolution.resolution_sources_expected must be non-empty - "
                           "state where you expect to find the outcome before you go looking for it")

    expected_id = make_prospective_case_id(case.domain, case.proposition, case.t0.t0_cutoff)
    if case.prospective_case_id != expected_id:
        violations.append(f"prospective_case_id {case.prospective_case_id!r} does not match the deterministic id "
                           f"{expected_id!r} derived from (domain, proposition, t0_cutoff)")

    if not (case.created_at or "").strip() or _parse_date(case.created_at) is None:
        violations.append(f"created_at {case.created_at!r} is not a valid date")

    return violations


def validate_resolution(resolution: Resolution) -> List[str]:
    violations: List[str] = []

    if not (resolution.prospective_case_id or "").strip():
        violations.append("prospective_case_id must not be blank")

    if _parse_date(resolution.resolved_at) is None:
        violations.append(f"resolved_at {resolution.resolved_at!r} is not a valid date")

    if resolution.outcome not in OUTCOMES:
        violations.append(f"outcome {resolution.outcome!r} is not one of {OUTCOMES}")

    if resolution.outcome in OUTCOMES_REQUIRING_EVIDENCE:
        if not resolution.t1_evidence_artifact_ids:
            violations.append(f"outcome {resolution.outcome!r} requires at least one t1_evidence_artifact_id - "
                               f"a POSITIVE/NEGATIVE/AMBIGUOUS resolution can never be evidence-free")
        if not (resolution.authoritative_source_type or "").strip():
            violations.append(f"outcome {resolution.outcome!r} requires a non-blank authoritative_source_type")

    if not (resolution.resolution_rationale or "").strip():
        violations.append("resolution_rationale must not be blank - every resolution states why, even "
                           "EXPIRED_UNRESOLVED and INVALIDATED")

    if resolution.resolver_type not in RESOLVER_TYPES:
        violations.append(f"resolver_type {resolution.resolver_type!r} is not one of {RESOLVER_TYPES} - "
                           f"a bare model call can never resolve a case (task Sec 8)")

    if _parse_date(resolution.created_at) is None:
        violations.append(f"created_at {resolution.created_at!r} is not a valid date")

    expected_id = make_resolution_id(resolution.prospective_case_id, resolution.outcome, resolution.resolved_at)
    if resolution.resolution_id != expected_id:
        violations.append(f"resolution_id {resolution.resolution_id!r} does not match the deterministic id "
                           f"{expected_id!r} derived from (prospective_case_id, outcome, resolved_at)")

    return violations
