"""Shared record builders for tests - not a test module itself."""

import _pathsetup  # noqa: F401

from constraint_change_observatory.schema import (
    INSUFFICIENT_DATA, OBSERVED, ChangeDriver, ClaimField, ConstraintChangeRecord,
    DeltaDimension, EvidenceItem, ReplacementConstraint,
)


def ev(citation="Test Source", value=100, unit="USD", as_of_date="2000", deployment_context="unknown", note=""):
    return EvidenceItem(citation=citation, value=value, unit=unit, as_of_date=as_of_date,
                         deployment_context=deployment_context, note=note)


def make_record(**overrides) -> ConstraintChangeRecord:
    base = dict(
        record_id="ccov-test-0001",
        constraint_family="cost",
        domain="test domain",
        constrained_activity="test activity",
        historical_constraint=ClaimField("historical constraint statement", OBSERVED),
        historical_evidence=[ev("Historical Source", 100, "USD", "2000")],
        historical_adaptation=ClaimField(None, INSUFFICIENT_DATA),
        change_driver=ChangeDriver("technological_improvement", "change happened", OBSERVED),
        change_evidence=[ev("Change Source", 10, "USD", "2010")],
        current_constraint_state=INSUFFICIENT_DATA,
        current_evidence=[],
        constraint_delta={},
        replacement_constraint=None,
        first_seen="2026-08-10",
        last_updated="2026-08-10",
        provenance=["Historical Source", "Change Source"],
        unresolved_questions=[],
        analyst="test-suite",
    )
    base.update(overrides)
    return ConstraintChangeRecord(**base)
