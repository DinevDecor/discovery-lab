"""Structural validation for ConstraintChangeRecord - design doc §12 hard
gates, plus the task's explicit validation-rule list. Deterministic,
offline, no model call: every rule here is a structural/arithmetic check
over the record's own fields, never a judgment about whether the cited
source is *actually* convincing (that stays a human's job).

`validate(record) -> List[str]` returns violation messages; empty means
valid. `ValidationError` is raised by intake.py when the list is
non-empty - "invalid records rejected loudly," never silently dropped or
silently coerced into a valid shape.
"""

from __future__ import annotations

import re
from typing import Any, List, Optional

from .schema import (
    CONSTRAINT_STATES, DEPLOYMENT_CONTEXTS, EVIDENCE_STATUSES, INSUFFICIENT_DATA, INVERTED,
    LAB_ONLY, MAGNITUDE_CLASSES, OBSERVED, PROTOCOL_VERSION, SHIFTED, STILL_BINDING, WEAKENED,
    ConstraintChangeRecord, EvidenceItem,
)

_STATES_REQUIRING_CURRENT_EVIDENCE = (WEAKENED, STILL_BINDING, SHIFTED, INVERTED)
_STATES_REQUIRING_REPLACEMENT = (SHIFTED, INVERTED)
_MAGNITUDE_NEEDS_SUPPORT = ("ORDER_OF_MAGNITUDE", "MULTIPLE_X", "INCREMENTAL")

_YEAR_RE = re.compile(r"\b(1[6-9]\d{2}|20\d{2})\b")


class ValidationError(ValueError):
    """Raised by intake.py (never by this module) when validate() returns
    one or more violations. Carries the full list, not just the first."""

    def __init__(self, record_id: str, violations: List[str]):
        self.record_id = record_id
        self.violations = violations
        super().__init__(f"{record_id}: {len(violations)} validation violation(s):\n  - " +
                          "\n  - ".join(violations))


def _years(items: List[EvidenceItem]) -> List[int]:
    years = []
    for item in items:
        m = _YEAR_RE.findall(item.as_of_date or "")
        years.extend(int(y) for y in m)
    return years


def _evidence_nonempty_with_citations(items: List[EvidenceItem]) -> bool:
    return bool(items) and all((e.citation or "").strip() for e in items)


def _same_evidence_list(a: List[EvidenceItem], b: List[EvidenceItem]) -> bool:
    key = lambda e: (e.citation, str(e.value), e.unit, e.as_of_date)  # noqa: E731
    return bool(a) and sorted(map(key, a)) == sorted(map(key, b))


def _is_number(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _validate_state_taxonomy(r: ConstraintChangeRecord, v: List[str]) -> None:
    if r.current_constraint_state not in CONSTRAINT_STATES:
        v.append(f"current_constraint_state {r.current_constraint_state!r} is not one of {CONSTRAINT_STATES}")
    for name, cf in (("historical_constraint", r.historical_constraint),
                      ("historical_adaptation", r.historical_adaptation),
                      ("change_driver", r.change_driver)):
        if cf.evidence_status not in EVIDENCE_STATUSES:
            v.append(f"{name}.evidence_status {cf.evidence_status!r} is not one of {EVIDENCE_STATUSES}")
    if r.replacement_constraint is not None and r.replacement_constraint.evidence_status not in EVIDENCE_STATUSES:
        v.append(f"replacement_constraint.evidence_status {r.replacement_constraint.evidence_status!r} "
                 f"is not one of {EVIDENCE_STATUSES}")
    for dim, dd in r.constraint_delta.items():
        if dd.magnitude_class not in MAGNITUDE_CLASSES:
            v.append(f"constraint_delta[{dim!r}].magnitude_class {dd.magnitude_class!r} "
                      f"is not one of {MAGNITUDE_CLASSES}")
    for name, items in (("historical_evidence", r.historical_evidence), ("change_evidence", r.change_evidence),
                         ("current_evidence", r.current_evidence)):
        for e in items:
            if e.deployment_context not in DEPLOYMENT_CONTEXTS:
                v.append(f"{name} item {e.citation!r} has deployment_context {e.deployment_context!r} "
                          f"not in {DEPLOYMENT_CONTEXTS}")


def _validate_temporal_ordering(r: ConstraintChangeRecord, v: List[str]) -> None:
    hist_years = _years(r.historical_evidence)
    change_years = _years(r.change_evidence)
    current_years = _years(r.current_evidence)
    # Deliberately lenient: only flag when a comparison is actually
    # parseable from both sides. Free-text as_of_date strings ("2015
    # (late)", "~2021-2022") that yield no 4-digit year are skipped, not
    # treated as violations - see README's temporal-ordering limitation.
    if hist_years and current_years and max(current_years) < max(hist_years):
        v.append(f"current_evidence (latest year {max(current_years)}) is dated before "
                  f"historical_evidence (latest year {max(hist_years)}) - THEN/NOW appear swapped")
    if hist_years and change_years and max(change_years) < min(hist_years):
        v.append(f"change_evidence (latest year {max(change_years)}) predates all historical_evidence "
                  f"(earliest year {min(hist_years)})")


def _validate_provenance(r: ConstraintChangeRecord, v: List[str]) -> None:
    any_evidence = bool(r.historical_evidence or r.change_evidence or r.current_evidence)
    any_observed = (r.historical_constraint.evidence_status == OBSERVED or
                     r.change_driver.evidence_status == OBSERVED or
                     (r.replacement_constraint is not None and r.replacement_constraint.evidence_status == OBSERVED))
    if (any_evidence or any_observed) and not r.provenance:
        v.append("provenance is empty but this record cites evidence or asserts an OBSERVED claim - "
                  "every material claim must preserve provenance")


def _validate_observed_requires_evidence(r: ConstraintChangeRecord, v: List[str]) -> None:
    if r.historical_constraint.evidence_status == OBSERVED and not _evidence_nonempty_with_citations(r.historical_evidence):
        v.append("historical_constraint is OBSERVED but historical_evidence is empty or has an uncited item")
    if r.change_driver.evidence_status == OBSERVED and not _evidence_nonempty_with_citations(r.change_evidence):
        v.append("change_driver is OBSERVED but change_evidence is empty or has an uncited item")
    if r.historical_adaptation.evidence_status == OBSERVED and not (r.historical_adaptation.statement or "").strip():
        v.append("historical_adaptation is OBSERVED but has no statement")
    if r.replacement_constraint is not None and r.replacement_constraint.evidence_status == OBSERVED:
        if not _evidence_nonempty_with_citations(r.current_evidence):
            v.append("replacement_constraint is OBSERVED but current_evidence is empty or has an uncited item")


def _validate_current_evidence_requirement(r: ConstraintChangeRecord, v: List[str]) -> None:
    """The design doc's central hard rule (§12): a state other than
    INSUFFICIENT_DATA requires current_evidence that speaks to the
    ORIGINAL constraint's present state - change_evidence alone is never
    enough. This is the direct implementation of "new technology exists
    does NOT imply WEAKENED." """
    state = r.current_constraint_state
    if state in _STATES_REQUIRING_CURRENT_EVIDENCE:
        if not _evidence_nonempty_with_citations(r.current_evidence):
            v.append(f"current_constraint_state={state} requires at least one cited current_evidence item "
                      "speaking to the ORIGINAL constraint's present state - change_evidence alone is not "
                      "sufficient (design doc §12's central rule)")
        elif state == WEAKENED and _same_evidence_list(r.current_evidence, r.change_evidence):
            v.append("current_constraint_state=WEAKENED but current_evidence is identical to change_evidence - "
                      "this looks like change_evidence was copied to satisfy the non-empty check rather than "
                      "genuinely evidencing the constraint's current state")


def _validate_replacement_requirement(r: ConstraintChangeRecord, v: List[str]) -> None:
    state = r.current_constraint_state
    if state not in _STATES_REQUIRING_REPLACEMENT:
        return
    has_replacement = r.replacement_constraint is not None and (r.replacement_constraint.statement or "").strip()
    if state == INVERTED and not has_replacement:
        v.append("current_constraint_state=INVERTED requires replacement_constraint with a statement "
                  "describing the new bottleneck the reversal creates - no escape hatch for INVERTED")
        return
    if state == SHIFTED and not has_replacement and not r.unresolved_questions:
        v.append("current_constraint_state=SHIFTED requires either replacement_constraint (with a statement) "
                  "or at least one unresolved_questions entry explaining why no replacement is named")


def _validate_lab_only_evidence(r: ConstraintChangeRecord, v: List[str]) -> None:
    """Design doc §13 case E: a record whose only current_evidence is
    lab-context should not claim a broadly-weakened real-world state."""
    state = r.current_constraint_state
    if state in (WEAKENED, SHIFTED, INVERTED) and r.current_evidence:
        if all(e.deployment_context == LAB_ONLY for e in r.current_evidence):
            v.append(f"current_constraint_state={state} but every current_evidence item is deployment_context="
                      "lab_only - lab-only capability must not be read as a broadly weakened real-world "
                      "constraint (design doc §13 case E); use INSUFFICIENT_DATA or STILL_BINDING and note "
                      "the deployment gap in unresolved_questions")


def _validate_quantitative_deltas(r: ConstraintChangeRecord, v: List[str]) -> None:
    for dim, dd in r.constraint_delta.items():
        has_then = dd.then_value is not None
        has_now = dd.now_value is not None
        if (has_then and _is_number(dd.then_value)) or (has_now and _is_number(dd.now_value)):
            if not (dd.unit or "").strip():
                v.append(f"constraint_delta[{dim!r}] has a numeric then_value/now_value but no unit - "
                          "quantitative deltas must not leave the unit implicit")
        if dd.ratio is not None and _is_number(dd.then_value) and _is_number(dd.now_value):
            if dd.then_value == 0:
                v.append(f"constraint_delta[{dim!r}] has then_value=0, ratio is undefined - use null")
            else:
                expected = dd.now_value / dd.then_value
                tolerance = max(1e-9, abs(expected) * 0.05)
                if abs(dd.ratio - expected) > tolerance:
                    v.append(f"constraint_delta[{dim!r}].ratio={dd.ratio} is inconsistent with "
                              f"now_value/then_value={expected:.6g} - possible unit mismatch or arithmetic error")
        if dd.magnitude_class in _MAGNITUDE_NEEDS_SUPPORT:
            if not ((has_then and has_now) or dd.evidence_ids):
                v.append(f"constraint_delta[{dim!r}].magnitude_class={dd.magnitude_class} asserted without "
                          "then_value+now_value or evidence_ids to support it")


def _validate_required_fields(r: ConstraintChangeRecord, v: List[str]) -> None:
    for field_name in ("record_id", "constraint_family", "domain", "constrained_activity", "analyst"):
        if not (getattr(r, field_name) or "").strip():
            v.append(f"{field_name} is required and must be non-empty")
    if r.protocol_version != PROTOCOL_VERSION:
        v.append(f"protocol_version {r.protocol_version!r} does not match expected {PROTOCOL_VERSION!r}")
    if not (r.first_seen or "").strip():
        v.append("first_seen is required")
    if not (r.last_updated or "").strip():
        v.append("last_updated is required")


def validate(record: ConstraintChangeRecord) -> List[str]:
    violations: List[str] = []
    _validate_required_fields(record, violations)
    _validate_state_taxonomy(record, violations)
    _validate_temporal_ordering(record, violations)
    _validate_provenance(record, violations)
    _validate_observed_requires_evidence(record, violations)
    _validate_current_evidence_requirement(record, violations)
    _validate_replacement_requirement(record, violations)
    _validate_lab_only_evidence(record, violations)
    _validate_quantitative_deltas(record, violations)
    return violations


def validate_or_raise(record: ConstraintChangeRecord) -> None:
    violations = validate(record)
    if violations:
        raise ValidationError(record.record_id, violations)
