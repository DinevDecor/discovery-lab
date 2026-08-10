"""Data shapes for the Business Candidate Analyst.

Nothing here reads or writes a file - see evidence_reader.py (read-only,
Constraint Archaeology side) and registry.py (the only write path, this
package's own side).
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

# Lifecycle states, in advancement order. REJECTED is reachable from any
# state and is not "further along" than PROMISING.
STATES = ("WATCH", "VALIDATING", "INVESTIGATE", "PROMISING", "REJECTED")

EVIDENCED = "EVIDENCED"
INSUFFICIENT_DATA = "INSUFFICIENT_DATA"

# Two analytical modes, conceptually distinct (see rearchitecture/ package):
#   NEW_MARKET               - Mode A: missing function/unmet need -> candidate.
#   OLD_BUSINESS_REARCHITECTURE - Mode B: historical constraint that shaped an
#     existing business, and whether that constraint still binds.
# Every Candidate carries exactly one. Never inferred from shape; always
# stamped explicitly by whichever analyst (Mode A's analyst.py or Mode B's
# rearchitecture/analyst.py) created the candidate_created event.
NEW_MARKET = "NEW_MARKET"
OLD_BUSINESS_REARCHITECTURE = "OLD_BUSINESS_REARCHITECTURE"
CANDIDATE_TYPES = (NEW_MARKET, OLD_BUSINESS_REARCHITECTURE)

# Mode B's evidence-quality scale is three-valued, not two: a historical
# constraint claim is OBSERVED (the text itself states it), INFERRED (a
# structural pattern match without an explicit causal statement in the
# text), or INSUFFICIENT_DATA (no signal at all). Collapsing OBSERVED and
# INFERRED together, the way Mode A's binary EVIDENCED does, would hide
# exactly the distinction lifecycle.py's VALIDATING bar depends on.
OBSERVED = "OBSERVED"
INFERRED = "INFERRED"
EVIDENCE_QUALITIES = (OBSERVED, INFERRED, INSUFFICIENT_DATA)


@dataclass(frozen=True)
class DimensionResult:
    """One answer to one item of the required evaluation checklist.

    `evidence` holds only observation_ids actually consulted for this
    dimension - never fabricated to make the record look fuller.
    """
    name: str
    status: str  # EVIDENCED | INSUFFICIENT_DATA
    value: Any
    evidence: List[str] = field(default_factory=list)
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RearchitectureField:
    """One answer to one item of Mode B's eight-item checklist.

    Unlike Mode A's DimensionResult, `status` is three-valued
    (OBSERVED/INFERRED/INSUFFICIENT_DATA) - see EVIDENCE_QUALITIES.
    `evidence` holds only observation_ids actually consulted.
    """
    name: str
    status: str  # OBSERVED | INFERRED | INSUFFICIENT_DATA
    value: Any
    evidence: List[str] = field(default_factory=list)
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class OpportunitySignature:
    """The deterministic grouping key computed by signature.py.

    Two evidence groups may only merge into one candidate when both fields
    match - see signature.py's merge gate for why text similarity alone is
    not enough.
    """
    buyer_bucket: str
    function_class: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CandidateEvent:
    """One immutable entry in data/candidate_events.jsonl.

    event_type in {"candidate_created", "state_changed", "evidence_added",
    "candidates_merged"}. `derived_from` lists the exact anomaly_id /
    observation_id / evaluation reference values used to produce this event
    - never invented to satisfy a schema.
    """
    event_id: str
    event_type: str
    candidate_id: str
    recorded_at: str
    reason: str
    derived_from: List[str]
    payload: Dict[str, Any]
    analyst_version: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "candidate_id": self.candidate_id,
            "recorded_at": self.recorded_at,
            "reason": self.reason,
            "derived_from": list(self.derived_from),
            "payload": self.payload,
            "analyst_version": self.analyst_version,
        }


@dataclass
class Candidate:
    """Rebuilt snapshot view, replayed fresh from candidate_events.jsonl on
    every run - never hand-edited, never read-modify-written."""
    candidate_id: str
    state: str
    created_at: str
    updated_at: str
    candidate_type: str = NEW_MARKET
    anomaly_ids: List[str] = field(default_factory=list)
    observation_ids: List[str] = field(default_factory=list)
    signature: Optional[Dict[str, str]] = None
    dimensions: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    # Populated only when candidate_type == OLD_BUSINESS_REARCHITECTURE - the
    # eight Mode B fields (existing_business, historical_constraint, ...),
    # each a RearchitectureField.to_dict(). None for NEW_MARKET candidates.
    rearchitecture: Optional[Dict[str, Dict[str, Any]]] = None
    history: List[Dict[str, Any]] = field(default_factory=list)
    merged_into: Optional[str] = None
    merged_from: List[str] = field(default_factory=list)
    rejected_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
