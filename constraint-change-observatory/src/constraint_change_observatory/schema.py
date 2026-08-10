"""Constraint Change Record schema — implements design doc §8-9
(`docs/constraint-change-observatory-design.md`, merged from PR #24).

Nothing here reads or writes a file, calls a model, or touches the
network. Pure data shapes and (de)serialization only — see ledger.py for
the only write path and validator.py for the rules that decide whether a
constructed record is admissible.

One deliberate departure from the design doc's literal schema, stated
here because it affects every other module: the design proposes
`superseded_by` as a field written ON the old record once a new one
replaces it. That requires mutating history, which contradicts this
repo's append-only discipline (and the design doc's own §10: "no field is
corrected in place, ever"). Instead, a *new* record carries `supersedes`
(pointing backward at the record_id it replaces), exactly the direction
`ca_agents.findings_ledger` and `business_candidate_analyst.registry`
already use for their own SUPERSEDES-shaped links. Which records are
"current" is computed by ledger.rebuild_snapshot, never written back.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

PROTOCOL_VERSION = "ccov0.1"

# --- Evidence discipline (design doc §7) ------------------------------
OBSERVED = "OBSERVED"
INFERRED = "INFERRED"
INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
EVIDENCE_STATUSES = (OBSERVED, INFERRED, INSUFFICIENT_DATA)

# --- Constraint-state taxonomy (design doc §6) -------------------------
WEAKENED = "WEAKENED"
STILL_BINDING = "STILL_BINDING"
SHIFTED = "SHIFTED"
INVERTED = "INVERTED"
# INSUFFICIENT_DATA reused from evidence statuses - same string, same meaning:
# "no cited link established this", not a fallback to minimize.
CONSTRAINT_STATES = (WEAKENED, STILL_BINDING, SHIFTED, INVERTED, INSUFFICIENT_DATA)

# --- Delta magnitude buckets (design doc §9) - descriptive, not a gate --
ORDER_OF_MAGNITUDE = "ORDER_OF_MAGNITUDE"
MULTIPLE_X = "MULTIPLE_X"
INCREMENTAL = "INCREMENTAL"
DIRECTION_ONLY = "DIRECTION_ONLY"
MAGNITUDE_CLASSES = (ORDER_OF_MAGNITUDE, MULTIPLE_X, INCREMENTAL, DIRECTION_ONLY, INSUFFICIENT_DATA)

# Non-exhaustive, extendable reference lists (design doc §4/§5) - free-text
# fields, not enforced enums, per the design doc's own reasoning: a fixed
# enum here would force a schema change for every new constraint family a
# researcher legitimately encounters. Kept for documentation/tooling, not
# validation.
KNOWN_CONSTRAINT_FAMILIES = (
    "cost", "latency", "bandwidth", "compute", "storage", "energy", "battery_density_cost",
    "material_properties", "manufacturing_capability", "minimum_economic_scale",
    "labor_availability_cost", "labor_cost", "expertise_scarcity", "information_scarcity",
    "search_cost", "transaction_cost", "coordination_cost", "verification_cost", "trust",
    "identity", "geographic_distance", "logistics_speed_cost", "inventory_uncertainty",
    "capital_requirements", "financing_access", "regulation", "licensing",
    "standards_interoperability", "distribution_access", "communication",
    "measurement_observability", "consumer_behavior", "demographics",
    "infrastructure_availability",
)

KNOWN_CHANGE_DRIVER_CATEGORIES = (
    "technological_improvement", "commoditization", "falling_component_prices",
    "infrastructure_deployment", "new_standards", "regulation_change", "new_materials",
    "manufacturing_improvements", "logistics_improvements", "new_financial_infrastructure",
    "new_distribution_channels", "behavioral_change", "demographic_change", "economies_of_scale",
    "open_source_availability", "increased_reliability", "improved_measurement",
    "smartphones_gps_connectivity", "robotics", "cloud_infrastructure", "ai", "other",
)

# Deployment context for a piece of evidence - design doc §13 case E
# (lab-only capability must not read as broadly weakened).
DEPLOYED = "deployed"
LAB_ONLY = "lab_only"
UNKNOWN_CONTEXT = "unknown"
DEPLOYMENT_CONTEXTS = (DEPLOYED, LAB_ONLY, UNKNOWN_CONTEXT)


def _dc(cls, data: Dict[str, Any]):
    """Construct a dataclass from a dict, ignoring unknown keys - tolerant
    of records authored by hand with extra commentary fields."""
    field_names = {f.name for f in cls.__dataclass_fields__.values()}
    return cls(**{k: v for k, v in data.items() if k in field_names})


@dataclass(frozen=True)
class EvidenceItem:
    citation: str
    value: Any = None
    unit: str = ""
    as_of_date: str = ""
    deployment_context: str = UNKNOWN_CONTEXT
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "EvidenceItem":
        return _dc(EvidenceItem, data)


@dataclass(frozen=True)
class ClaimField:
    """historical_constraint / historical_adaptation - a statement plus its
    own independent evidence_status (design doc §7)."""
    statement: Optional[str] = None
    evidence_status: str = INSUFFICIENT_DATA

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ClaimField":
        return _dc(ClaimField, data)


@dataclass(frozen=True)
class ChangeDriver:
    category: str = ""
    statement: Optional[str] = None
    evidence_status: str = INSUFFICIENT_DATA

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ChangeDriver":
        return _dc(ChangeDriver, data)


@dataclass(frozen=True)
class ReplacementConstraint:
    family: Optional[str] = None
    statement: Optional[str] = None
    evidence_status: str = INSUFFICIENT_DATA

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ReplacementConstraint":
        return _dc(ReplacementConstraint, data)


@dataclass(frozen=True)
class DeltaDimension:
    then_value: Any = None
    now_value: Any = None
    unit: str = ""
    ratio: Optional[float] = None
    magnitude_class: str = INSUFFICIENT_DATA
    evidence_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "DeltaDimension":
        return _dc(DeltaDimension, data)


@dataclass
class ConstraintChangeRecord:
    record_id: str
    constraint_family: str
    domain: str
    constrained_activity: str

    historical_constraint: ClaimField
    change_driver: ChangeDriver
    current_constraint_state: str

    protocol_version: str = PROTOCOL_VERSION
    supersedes: Optional[str] = None  # see module docstring: replaces design's superseded_by

    historical_evidence: List[EvidenceItem] = field(default_factory=list)
    historical_adaptation: ClaimField = field(default_factory=ClaimField)
    change_evidence: List[EvidenceItem] = field(default_factory=list)
    current_evidence: List[EvidenceItem] = field(default_factory=list)

    constraint_delta: Dict[str, DeltaDimension] = field(default_factory=dict)
    replacement_constraint: Optional[ReplacementConstraint] = None

    first_seen: str = ""
    last_updated: str = ""
    provenance: List[str] = field(default_factory=list)
    unresolved_questions: List[str] = field(default_factory=list)
    analyst: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "record_id": self.record_id,
            "protocol_version": self.protocol_version,
            "supersedes": self.supersedes,
            "constraint_family": self.constraint_family,
            "domain": self.domain,
            "constrained_activity": self.constrained_activity,
            "historical_constraint": self.historical_constraint.to_dict(),
            "historical_evidence": [e.to_dict() for e in self.historical_evidence],
            "historical_adaptation": self.historical_adaptation.to_dict(),
            "change_driver": self.change_driver.to_dict(),
            "change_evidence": [e.to_dict() for e in self.change_evidence],
            "current_constraint_state": self.current_constraint_state,
            "current_evidence": [e.to_dict() for e in self.current_evidence],
            "constraint_delta": {k: v.to_dict() for k, v in self.constraint_delta.items()},
            "replacement_constraint": self.replacement_constraint.to_dict() if self.replacement_constraint else None,
            "first_seen": self.first_seen,
            "last_updated": self.last_updated,
            "provenance": list(self.provenance),
            "unresolved_questions": list(self.unresolved_questions),
            "analyst": self.analyst,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ConstraintChangeRecord":
        rc = data.get("replacement_constraint")
        return ConstraintChangeRecord(
            record_id=data["record_id"],
            protocol_version=data.get("protocol_version", PROTOCOL_VERSION),
            supersedes=data.get("supersedes"),
            constraint_family=data.get("constraint_family", ""),
            domain=data.get("domain", ""),
            constrained_activity=data.get("constrained_activity", ""),
            historical_constraint=ClaimField.from_dict(data.get("historical_constraint") or {}),
            historical_evidence=[EvidenceItem.from_dict(e) for e in data.get("historical_evidence", [])],
            historical_adaptation=ClaimField.from_dict(data.get("historical_adaptation") or {}),
            change_driver=ChangeDriver.from_dict(data.get("change_driver") or {}),
            change_evidence=[EvidenceItem.from_dict(e) for e in data.get("change_evidence", [])],
            current_constraint_state=data.get("current_constraint_state", INSUFFICIENT_DATA),
            current_evidence=[EvidenceItem.from_dict(e) for e in data.get("current_evidence", [])],
            constraint_delta={k: DeltaDimension.from_dict(v) for k, v in (data.get("constraint_delta") or {}).items()},
            replacement_constraint=ReplacementConstraint.from_dict(rc) if rc else None,
            first_seen=data.get("first_seen", ""),
            last_updated=data.get("last_updated", ""),
            provenance=list(data.get("provenance", [])),
            unresolved_questions=list(data.get("unresolved_questions", [])),
            analyst=data.get("analyst", ""),
        )
