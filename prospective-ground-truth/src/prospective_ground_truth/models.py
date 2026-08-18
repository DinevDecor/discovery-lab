"""Data shapes for the Prospective Ground-Truth Stream.

Four durable concepts, per the task's own naming, realized as three
dataclasses across two append-only ledgers:

  T0Freeze            the frozen evidence packet a ProspectiveCase is
                       registered against - nested inside ProspectiveCase,
                       not a separate ledger, because a case cannot exist
                       without one (task Sec 5: freezing T0 IS registering
                       the case).
  ExpectedResolution   the pre-registered resolution criteria - also
                       nested inside ProspectiveCase for the same reason
                       (task Sec 6: criteria must exist BEFORE the case is
                       usable at all, so they cannot be a later append).
  ProspectiveCase      one case: proposition + T0Freeze + ExpectedResolution
                       + a status derived at snapshot-rebuild time, never
                       stored as a mutable field on the raw ledger line.
  Resolution           the T1 outcome - a SEPARATE, later ledger entry,
                       so a case's frozen T0 content is structurally
                       incapable of being touched by resolving it (see
                       ledger.py: CaseLedger and ResolutionLedger are two
                       different append-only files).

Nothing here reads or writes a file, calls a model, or touches the
network - pure data shapes and (de)serialization only, the same split
`constraint_change_observatory.schema` and `blind_analysis_kernel.packet`
already use.

WHY resolver_type CAN NEVER BE A BARE "model"
    Task Sec 8: "Models are never resolution evidence." RESOLVER_TYPES
    intentionally has no plain "model" value - only HUMAN and
    MODEL_ASSISTED_HUMAN_CONFIRMED exist, so a model can help a human
    FIND a resolution source, but a human must always be the one who
    confirms it is authoritative. validator.py enforces this is one of
    the two allowed values, never anything else.

WHY Resolution.outcome HAS FIVE VALUES, NOT THE TASK'S LITERAL FOUR
    Task Sec 7 lists outcome as POSITIVE | NEGATIVE | AMBIGUOUS |
    EXPIRED_UNRESOLVED. ProspectiveCase.status (Sec 4) separately
    requires a fifth terminal state, INVALIDATED (e.g. the case is later
    found to have been malformed at registration - contaminated T0
    evidence, a proposition that was never actually falsifiable).
    Building a THIRD ledger file just to carry that one rare terminal
    state would violate Sec 2's "avoid... unless absolutely required" -
    reusing the Resolution ledger's existing evidence/rationale/
    resolver_type fields (which apply equally well to "this case is
    invalid because X" as to "this case resolved POSITIVE because Y") is
    the smaller, more defensible choice. This is a deliberate, minimal
    extension, not a silent deviation - see OUTCOMES below.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

PROTOCOL_VERSION = "pgt0.1"

# --- ProspectiveCase.status - derived at snapshot-rebuild time, never a
# mutable field an append can silently change (ledger.py). ---
STATUS_OPEN = "OPEN"
STATUS_AWAITING_OUTCOME = "AWAITING_OUTCOME"
STATUS_RESOLVED = "RESOLVED"
STATUS_EXPIRED_UNRESOLVED = "EXPIRED_UNRESOLVED"
STATUS_INVALIDATED = "INVALIDATED"
STATUSES = (STATUS_OPEN, STATUS_AWAITING_OUTCOME, STATUS_RESOLVED,
            STATUS_EXPIRED_UNRESOLVED, STATUS_INVALIDATED)

# --- Resolution.outcome ---
OUTCOME_POSITIVE = "POSITIVE"
OUTCOME_NEGATIVE = "NEGATIVE"
OUTCOME_AMBIGUOUS = "AMBIGUOUS"
OUTCOME_EXPIRED_UNRESOLVED = "EXPIRED_UNRESOLVED"
OUTCOME_INVALIDATED = "INVALIDATED"  # see module docstring for why this exists
OUTCOMES = (OUTCOME_POSITIVE, OUTCOME_NEGATIVE, OUTCOME_AMBIGUOUS,
            OUTCOME_EXPIRED_UNRESOLVED, OUTCOME_INVALIDATED)
# Outcomes that require real T1 evidence and an authoritative source -
# EXPIRED_UNRESOLVED and INVALIDATED are about absence/defect, not a
# positive claim about reality, so they are exempt (validator.py).
OUTCOMES_REQUIRING_EVIDENCE = (OUTCOME_POSITIVE, OUTCOME_NEGATIVE, OUTCOME_AMBIGUOUS)

# --- Resolution.resolver_type - task Sec 8: "Models are never resolution
# evidence." No plain "model" value exists in this tuple, by construction. ---
RESOLVER_HUMAN = "human"
RESOLVER_MODEL_ASSISTED_HUMAN_CONFIRMED = "model_assisted_human_confirmed"
RESOLVER_TYPES = (RESOLVER_HUMAN, RESOLVER_MODEL_ASSISTED_HUMAN_CONFIRMED)


def _dc(cls, data: Dict[str, Any]):
    """Construct a dataclass from a dict, ignoring unknown keys - same
    tolerance constraint_change_observatory.schema._dc grants."""
    field_names = {f.name for f in cls.__dataclass_fields__.values()}
    return cls(**{k: v for k, v in data.items() if k in field_names})


@dataclass(frozen=True)
class T0EvidenceItem:
    """One frozen piece of T0 evidence. `captured_at` is the date this
    evidence was itself observed/published - validator.py rejects any
    item whose captured_at is after the case's t0_cutoff, which is the
    structural half of "no post-T0 evidence enters the frozen packet"
    (the other half is that T0Freeze, once written, is never re-appended
    to - see ledger.py)."""
    artifact_id: str
    citation: str
    source_url: str
    captured_at: str
    quote_or_summary: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "T0EvidenceItem":
        return _dc(T0EvidenceItem, data)


@dataclass(frozen=True)
class T0Freeze:
    """The frozen evidence packet. `packet_sha256` is computed by
    packet.py over the canonical JSON of (t0_cutoff, evidence) - never
    hand-set, always independently recomputable and checked by
    validator.py before a case can enter the ledger."""
    t0_cutoff: str
    evidence: List[T0EvidenceItem]
    packet_sha256: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "t0_cutoff": self.t0_cutoff,
            "evidence": [e.to_dict() for e in self.evidence],
            "packet_sha256": self.packet_sha256,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "T0Freeze":
        return T0Freeze(
            t0_cutoff=data["t0_cutoff"],
            evidence=[T0EvidenceItem.from_dict(e) for e in data.get("evidence", [])],
            packet_sha256=data["packet_sha256"],
        )


@dataclass(frozen=True)
class ExpectedResolutionWindow:
    """A date interval, never a fabricated point estimate - same
    discipline as calendar_arbitrage_watch.models.DateBound. A single
    expected date is represented as earliest == latest."""
    earliest: str
    latest: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ExpectedResolutionWindow":
        return _dc(ExpectedResolutionWindow, data)


@dataclass(frozen=True)
class ExpectedResolution:
    """Resolution criteria, pre-registered before the outcome is known
    (task Sec 6). All three conditions are required - validator.py
    rejects a case where any is blank."""
    resolution_question: str
    expected_resolution_window: ExpectedResolutionWindow
    resolution_sources_expected: List[str]
    positive_condition: str
    negative_condition: str
    ambiguous_condition: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "resolution_question": self.resolution_question,
            "expected_resolution_window": self.expected_resolution_window.to_dict(),
            "resolution_sources_expected": list(self.resolution_sources_expected),
            "positive_condition": self.positive_condition,
            "negative_condition": self.negative_condition,
            "ambiguous_condition": self.ambiguous_condition,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ExpectedResolution":
        return ExpectedResolution(
            resolution_question=data["resolution_question"],
            expected_resolution_window=ExpectedResolutionWindow.from_dict(data["expected_resolution_window"]),
            resolution_sources_expected=list(data.get("resolution_sources_expected", [])),
            positive_condition=data["positive_condition"],
            negative_condition=data["negative_condition"],
            ambiguous_condition=data["ambiguous_condition"],
        )


@dataclass(frozen=True)
class ProspectiveCase:
    prospective_case_id: str
    source_case_id: Optional[str]
    created_at: str
    domain: str
    proposition: str
    decision_relevance: str
    t0: T0Freeze
    expected_resolution: ExpectedResolution
    protocol_version: str = PROTOCOL_VERSION

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prospective_case_id": self.prospective_case_id,
            "source_case_id": self.source_case_id,
            "created_at": self.created_at,
            "domain": self.domain,
            "proposition": self.proposition,
            "decision_relevance": self.decision_relevance,
            "t0": self.t0.to_dict(),
            "expected_resolution": self.expected_resolution.to_dict(),
            "protocol_version": self.protocol_version,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ProspectiveCase":
        return ProspectiveCase(
            prospective_case_id=data["prospective_case_id"],
            source_case_id=data.get("source_case_id"),
            created_at=data["created_at"],
            domain=data["domain"],
            proposition=data["proposition"],
            decision_relevance=data["decision_relevance"],
            t0=T0Freeze.from_dict(data["t0"]),
            expected_resolution=ExpectedResolution.from_dict(data["expected_resolution"]),
            protocol_version=data.get("protocol_version", PROTOCOL_VERSION),
        )


@dataclass(frozen=True)
class Resolution:
    resolution_id: str
    prospective_case_id: str
    resolved_at: str
    outcome: str
    t1_evidence_artifact_ids: List[str]
    authoritative_source_type: str
    resolution_rationale: str
    resolver_type: str
    created_at: str
    protocol_version: str = PROTOCOL_VERSION

    def to_dict(self) -> Dict[str, Any]:
        return {
            "resolution_id": self.resolution_id,
            "prospective_case_id": self.prospective_case_id,
            "resolved_at": self.resolved_at,
            "outcome": self.outcome,
            "t1_evidence_artifact_ids": list(self.t1_evidence_artifact_ids),
            "authoritative_source_type": self.authoritative_source_type,
            "resolution_rationale": self.resolution_rationale,
            "resolver_type": self.resolver_type,
            "created_at": self.created_at,
            "protocol_version": self.protocol_version,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Resolution":
        return Resolution(
            resolution_id=data["resolution_id"],
            prospective_case_id=data["prospective_case_id"],
            resolved_at=data["resolved_at"],
            outcome=data["outcome"],
            t1_evidence_artifact_ids=list(data.get("t1_evidence_artifact_ids", [])),
            authoritative_source_type=data["authoritative_source_type"],
            resolution_rationale=data["resolution_rationale"],
            resolver_type=data["resolver_type"],
            created_at=data["created_at"],
            protocol_version=data.get("protocol_version", PROTOCOL_VERSION),
        )
