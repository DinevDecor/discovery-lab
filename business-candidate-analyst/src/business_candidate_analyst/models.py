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
    anomaly_ids: List[str] = field(default_factory=list)
    observation_ids: List[str] = field(default_factory=list)
    signature: Optional[Dict[str, str]] = None
    dimensions: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    history: List[Dict[str, Any]] = field(default_factory=list)
    merged_into: Optional[str] = None
    merged_from: List[str] = field(default_factory=list)
    rejected_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
