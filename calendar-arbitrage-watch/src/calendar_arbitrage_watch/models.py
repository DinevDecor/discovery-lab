"""Core data shapes for Calendar Arbitrage Watch.

Nothing here reads or writes a file, calls a model, or touches the
network - pure data shapes and (de)serialization only, the same split
`constraint_change_observatory.schema` and `ca_agents.models` already use.

Every quantity that isn't a literal identifier or free-text label is
wrapped in `NumberClaim`/`DateBound` rather than a bare float/string, so
"we don't actually know this yet" is always representable as
`evidence_status=INSUFFICIENT_DATA` with `value=None` - a complete, honest
record, never a defect to paper over (repo-wide convention, see
constraint-change-observatory/README.md's evidence-status section).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

PROTOCOL_VERSION = "caw0.1.2"

# --- evidence-status discipline (mirrors constraint_change_observatory) ---
OBSERVED = "OBSERVED"
INFERRED = "INFERRED"
INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
EVIDENCE_STATUSES = (OBSERVED, INFERRED, INSUFFICIENT_DATA)

# --- number-provenance discipline, independently adopted for this package.
# The convention this echoes (mark every load-bearing number MEASURED or
# REPEATED) lives in the frozen constraint-archaeology-v0.5-patch.md S1
# addition - that file is never imported or modified here; this is a
# parallel, separately-owned adoption of the same discipline, not a
# dependency on it. ---
MEASURED = "MEASURED"
REPEATED = "REPEATED"
NUMBER_PROVENANCE = (MEASURED, REPEATED)

# --- mode: docs/method/calendar-arbitrage-screener-v0.1.1-delta.md section
# "Calendar Archaeology" ---
DISCOVERY = "DISCOVERY"
ARCHAEOLOGY = "ARCHAEOLOGY"
CONVERSION = "CONVERSION"
MODES = (DISCOVERY, ARCHAEOLOGY, CONVERSION)

# --- source categories - the six research-doc "hunter" roles collapsed
# into one registry field read by one specialist module (approved
# architecture review, section 5: role collapse) ---
CATEGORY_REGULATORY_CLOCK = "regulatory_clock"
CATEGORY_ACCREDITATION = "accreditation_qualification"
CATEGORY_INFRASTRUCTURE_QUEUE = "infrastructure_calendar"
CATEGORY_ARCHAEOLOGY_ASSET = "calendar_archaeology"
CATEGORY_ENVIRONMENTAL_RIGHTS = "environmental_scarcity_rights"
CATEGORY_DEMAND_SHOCK = "demand_shock"
CATEGORIES = (
    CATEGORY_REGULATORY_CLOCK, CATEGORY_ACCREDITATION, CATEGORY_INFRASTRUCTURE_QUEUE,
    CATEGORY_ARCHAEOLOGY_ASSET, CATEGORY_ENVIRONMENTAL_RIGHTS, CATEGORY_DEMAND_SHOCK,
)

# --- shock forecast type - mandatory from v0.1.2 per the 2026-08-15 approval ---
DATED = "DATED"
ROLLING = "ROLLING"
SHOCK_TYPES = (DATED, ROLLING)

# --- lifecycle states. START_CLOCK_CANDIDATE / BUY_CALENDAR_CANDIDATE are
# the maximum automatic output - see CONTRACT.md's Human Authority
# Boundary. Nothing in this package ever writes a state beyond these two
# on its own initiative; there is no "APPLIED"/"PURCHASED"/"CONTACTED"
# state anywhere in this enum, which is a stronger boundary than a policy
# sentence - the state simply does not exist to be reached. ---
WATCH = "WATCH"
CHEAP_TEST = "CHEAP_TEST"
START_CLOCK_CANDIDATE = "START_CLOCK_CANDIDATE"
BUY_CALENDAR_CANDIDATE = "BUY_CALENDAR_CANDIDATE"
REJECTED = "REJECTED"
LIFECYCLE_STATES = (WATCH, CHEAP_TEST, START_CLOCK_CANDIDATE, BUY_CALENDAR_CANDIDATE, REJECTED)
MAX_AUTOMATIC_STATES = (START_CLOCK_CANDIDATE, BUY_CALENDAR_CANDIDATE)
# Rank order for "is this a promotion" comparisons - REJECTED is terminal,
# not "below WATCH". Shared by lifecycle.py and report.py so both modules
# agree on what counts as a promotion/degradation.
STATE_RANK = {WATCH: 0, CHEAP_TEST: 1, START_CLOCK_CANDIDATE: 2, BUY_CALENDAR_CANDIDATE: 2, REJECTED: -1}

# --- adversarial review outcomes. All three are always persisted
# (CLAUDE.md: "All gate outcomes persist"), applied here to a single
# candidate's own longitudinal review rather than a two-anomaly pairwise
# merge - see gate.py's module docstring for why the shape differs from
# ca_agents.same_mechanism_gate.GateDecision. ---
REVIEW_CONFIRMED = "CONFIRMED"
REVIEW_CHALLENGED = "CHALLENGED"
REVIEW_KILLED = "KILLED"
REVIEW_OUTCOMES = (REVIEW_CONFIRMED, REVIEW_CHALLENGED, REVIEW_KILLED)


def _dc(cls, data: Dict[str, Any]):
    """Construct a dataclass from a dict, ignoring unknown keys - tolerant
    of submissions authored by hand with extra commentary fields (same
    tolerance constraint_change_observatory.schema._dc grants)."""
    field_names = {f.name for f in cls.__dataclass_fields__.values()}
    return cls(**{k: v for k, v in data.items() if k in field_names})


@dataclass(frozen=True)
class NumberClaim:
    """One measured/derived quantity plus its own honesty tags - never a
    bare float. `value=None` with `evidence_status=INSUFFICIENT_DATA` is a
    complete, valid record."""
    value: Optional[float] = None
    unit: str = ""
    provenance: str = REPEATED  # MEASURED | REPEATED
    evidence_status: str = INSUFFICIENT_DATA
    as_of: str = ""
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "NumberClaim":
        return _dc(NumberClaim, data)


@dataclass(frozen=True)
class DateBound:
    """An interval, never a fabricated point estimate - required whenever
    a date is inferred rather than directly observed (unknown competitor
    filing date, forecast shock dates under ROLLING, clock_open_date).

    `earliest`/`latest` are ISO date strings (`YYYY-MM-DD`); either may be
    None. If neither can be defended, `evidence_status` stays
    INSUFFICIENT_DATA and both stay None - callers must never synthesize a
    midpoint (2026-08-15 approval, point 8)."""
    earliest: Optional[str] = None
    latest: Optional[str] = None
    basis: str = ""
    evidence_status: str = INSUFFICIENT_DATA

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "DateBound":
        return _dc(DateBound, data)

    def is_defensible(self) -> bool:
        return self.evidence_status != INSUFFICIENT_DATA and bool(self.earliest or self.latest)


@dataclass(frozen=True)
class ShockForecast:
    """T_shock, versioned. `shock_type=DATED` means `date_bound` collapses
    to a single known date (`earliest == latest`); `ROLLING` means it is a
    genuine forecast that must be RE-ISSUED (a new `ShockForecast` with
    `forecast_version + 1`, appended as a new ledger line) as evidence
    changes - never edited in place. See ledger.py."""
    shock_type: str = DATED
    date_bound: DateBound = field(default_factory=DateBound)
    as_of: str = ""
    forecast_version: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ShockForecast":
        return ShockForecast(
            shock_type=data.get("shock_type", DATED),
            date_bound=DateBound.from_dict(data.get("date_bound") or {}),
            as_of=data.get("as_of", ""),
            forecast_version=int(data.get("forecast_version", 1)),
        )


@dataclass(frozen=True)
class ReadinessAssessment:
    """Inputs kept deliberately separate (methodology delta v0.1.1 #1):
    `elapsed_days` and `slippage_days` are historical-record context only.
    `l_remaining_days` MUST be an independently asserted remaining-work
    estimate, never derived from `elapsed_days` inside this dataclass or
    by specialist.py - that is precisely the bug the delta forbids. See
    specialist.compute_readiness_gap."""
    elapsed_days: Optional[float] = None
    actual_progress_fraction: Optional[float] = None  # 0..1, against a stated milestone plan
    slippage_days: Optional[float] = None  # positive = behind plan, negative = ahead
    l_remaining_days: NumberClaim = field(default_factory=NumberClaim)
    g_r_days: NumberClaim = field(default_factory=NumberClaim)  # derived; see specialist.py

    def to_dict(self) -> Dict[str, Any]:
        return {
            "elapsed_days": self.elapsed_days,
            "actual_progress_fraction": self.actual_progress_fraction,
            "slippage_days": self.slippage_days,
            "l_remaining_days": self.l_remaining_days.to_dict(),
            "g_r_days": self.g_r_days.to_dict(),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ReadinessAssessment":
        return ReadinessAssessment(
            elapsed_days=data.get("elapsed_days"),
            actual_progress_fraction=data.get("actual_progress_fraction"),
            slippage_days=data.get("slippage_days"),
            l_remaining_days=NumberClaim.from_dict(data.get("l_remaining_days") or {}),
            g_r_days=NumberClaim.from_dict(data.get("g_r_days") or {}),
        )


@dataclass(frozen=True)
class DefensiveGapAssessment:
    """G_d split by competitor posture (methodology delta v0.1.1 #2):
    `g_d_novo_days` assumes a competitor starting today; `g_d_active_days`
    assumes one whose clock is already running, anchored to
    `competitor_start_bound` (an interval, never a point)."""
    g_d_novo_days: NumberClaim = field(default_factory=NumberClaim)
    g_d_active_days: NumberClaim = field(default_factory=NumberClaim)
    competitor_start_bound: DateBound = field(default_factory=DateBound)
    bound_used: str = ""  # "earliest" | "latest" | "" - always the bound UNFAVORABLE to us

    def to_dict(self) -> Dict[str, Any]:
        return {
            "g_d_novo_days": self.g_d_novo_days.to_dict(),
            "g_d_active_days": self.g_d_active_days.to_dict(),
            "competitor_start_bound": self.competitor_start_bound.to_dict(),
            "bound_used": self.bound_used,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "DefensiveGapAssessment":
        return DefensiveGapAssessment(
            g_d_novo_days=NumberClaim.from_dict(data.get("g_d_novo_days") or {}),
            g_d_active_days=NumberClaim.from_dict(data.get("g_d_active_days") or {}),
            competitor_start_bound=DateBound.from_dict(data.get("competitor_start_bound") or {}),
            bound_used=data.get("bound_used", ""),
        )


@dataclass(frozen=True)
class DemandProfile:
    """Four separate 0..1 fields, never collapsed to one confidence
    multiplier (methodology delta v0.1.1 #3, plus the 2026-08-15 approval
    point 5's explicit split of deadline_relief_risk from
    demand_suppression_risk: the obligation staying certain while its DATE
    moves is a different risk from the obligation itself shrinking)."""
    demand_obligation_certainty: NumberClaim = field(default_factory=NumberClaim)
    shock_date_stability: NumberClaim = field(default_factory=NumberClaim)
    deadline_relief_risk: NumberClaim = field(default_factory=NumberClaim)
    demand_suppression_risk: NumberClaim = field(default_factory=NumberClaim)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "demand_obligation_certainty": self.demand_obligation_certainty.to_dict(),
            "shock_date_stability": self.shock_date_stability.to_dict(),
            "deadline_relief_risk": self.deadline_relief_risk.to_dict(),
            "demand_suppression_risk": self.demand_suppression_risk.to_dict(),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "DemandProfile":
        return DemandProfile(
            demand_obligation_certainty=NumberClaim.from_dict(data.get("demand_obligation_certainty") or {}),
            shock_date_stability=NumberClaim.from_dict(data.get("shock_date_stability") or {}),
            deadline_relief_risk=NumberClaim.from_dict(data.get("deadline_relief_risk") or {}),
            demand_suppression_risk=NumberClaim.from_dict(data.get("demand_suppression_risk") or {}),
        )


@dataclass(frozen=True)
class PendingCompetitionAssessment:
    """Infrastructure candidates: formal free capacity alone is
    insufficient (methodology delta v0.1.1 #5). A large pending queue
    against nominal free capacity is not a free calendar slot - all five
    fields are reported side by side, never collapsed into one
    'availability' number."""
    formal_free_capacity: NumberClaim = field(default_factory=NumberClaim)
    pending_applications: NumberClaim = field(default_factory=NumberClaim)
    issued_connection_opinions: NumberClaim = field(default_factory=NumberClaim)
    known_queue_ahead: NumberClaim = field(default_factory=NumberClaim)
    committed_competing_projects: NumberClaim = field(default_factory=NumberClaim)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "formal_free_capacity": self.formal_free_capacity.to_dict(),
            "pending_applications": self.pending_applications.to_dict(),
            "issued_connection_opinions": self.issued_connection_opinions.to_dict(),
            "known_queue_ahead": self.known_queue_ahead.to_dict(),
            "committed_competing_projects": self.committed_competing_projects.to_dict(),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "PendingCompetitionAssessment":
        return PendingCompetitionAssessment(
            formal_free_capacity=NumberClaim.from_dict(data.get("formal_free_capacity") or {}),
            pending_applications=NumberClaim.from_dict(data.get("pending_applications") or {}),
            issued_connection_opinions=NumberClaim.from_dict(data.get("issued_connection_opinions") or {}),
            known_queue_ahead=NumberClaim.from_dict(data.get("known_queue_ahead") or {}),
            committed_competing_projects=NumberClaim.from_dict(data.get("committed_competing_projects") or {}),
        )


@dataclass(frozen=True)
class OpenFinding:
    """An explicitly uncalibrated rule or diagnostic quantity that MUST
    NOT influence scoring yet (2026-08-15 approval, points 4 and 7).
    specialist.py computes/records these but score() never reads them."""
    finding_id: str
    description: str
    status: str = "OPEN_FINDING"
    affects_scoring: bool = False
    value: Optional[float] = None
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "OpenFinding":
        return _dc(OpenFinding, data)


@dataclass
class CalendarAssessment:
    """One full point-in-time assessment of one candidate. A revision is a
    NEW CalendarAssessment sharing `candidate_id` (the stable lineage key)
    with a fresh `supersedes` pointer - never an edit of a past one. See
    ledger.py, which mirrors constraint_change_observatory.ledger's
    append-only + rebuilt-snapshot split exactly."""
    candidate_id: str
    protocol_version: str = PROTOCOL_VERSION
    supersedes: Optional[str] = None

    mode: str = DISCOVERY
    category: str = ""
    title: str = ""
    summary: str = ""

    shock_forecast: ShockForecast = field(default_factory=ShockForecast)
    latest_safe_date_as_of: DateBound = field(default_factory=DateBound)  # was "t_lockout_self"
    clock_open_date: DateBound = field(default_factory=DateBound)

    readiness: ReadinessAssessment = field(default_factory=ReadinessAssessment)
    defensive: DefensiveGapAssessment = field(default_factory=DefensiveGapAssessment)
    demand: DemandProfile = field(default_factory=DemandProfile)
    pending_competition: PendingCompetitionAssessment = field(default_factory=PendingCompetitionAssessment)

    demand_stability_index: str = INSUFFICIENT_DATA  # DSI: heuristic tier, see specialist.py
    s_ready: NumberClaim = field(default_factory=NumberClaim)  # same 0..1 unit as demand fields
    readiness_index: NumberClaim = field(default_factory=NumberClaim)  # RI: composite, see specialist.py

    open_findings: List[OpenFinding] = field(default_factory=list)

    lifecycle_state: str = WATCH
    lifecycle_reason: str = ""

    evidence_ids: List[str] = field(default_factory=list)
    provenance: List[str] = field(default_factory=list)

    first_seen: str = ""
    last_updated: str = ""
    analyst: str = "calendar_arbitrage_specialist"
    analyst_version: str = ""
    origin: str = "generated"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "protocol_version": self.protocol_version,
            "supersedes": self.supersedes,
            "mode": self.mode,
            "category": self.category,
            "title": self.title,
            "summary": self.summary,
            "shock_forecast": self.shock_forecast.to_dict(),
            "latest_safe_date_as_of": self.latest_safe_date_as_of.to_dict(),
            "clock_open_date": self.clock_open_date.to_dict(),
            "readiness": self.readiness.to_dict(),
            "defensive": self.defensive.to_dict(),
            "demand": self.demand.to_dict(),
            "pending_competition": self.pending_competition.to_dict(),
            "demand_stability_index": self.demand_stability_index,
            "s_ready": self.s_ready.to_dict(),
            "readiness_index": self.readiness_index.to_dict(),
            "open_findings": [f.to_dict() for f in self.open_findings],
            "lifecycle_state": self.lifecycle_state,
            "lifecycle_reason": self.lifecycle_reason,
            "evidence_ids": list(self.evidence_ids),
            "provenance": list(self.provenance),
            "first_seen": self.first_seen,
            "last_updated": self.last_updated,
            "analyst": self.analyst,
            "analyst_version": self.analyst_version,
            "origin": self.origin,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "CalendarAssessment":
        return CalendarAssessment(
            candidate_id=data["candidate_id"],
            protocol_version=data.get("protocol_version", PROTOCOL_VERSION),
            supersedes=data.get("supersedes"),
            mode=data.get("mode", DISCOVERY),
            category=data.get("category", ""),
            title=data.get("title", ""),
            summary=data.get("summary", ""),
            shock_forecast=ShockForecast.from_dict(data.get("shock_forecast") or {}),
            latest_safe_date_as_of=DateBound.from_dict(data.get("latest_safe_date_as_of") or {}),
            clock_open_date=DateBound.from_dict(data.get("clock_open_date") or {}),
            readiness=ReadinessAssessment.from_dict(data.get("readiness") or {}),
            defensive=DefensiveGapAssessment.from_dict(data.get("defensive") or {}),
            demand=DemandProfile.from_dict(data.get("demand") or {}),
            pending_competition=PendingCompetitionAssessment.from_dict(data.get("pending_competition") or {}),
            demand_stability_index=data.get("demand_stability_index", INSUFFICIENT_DATA),
            s_ready=NumberClaim.from_dict(data.get("s_ready") or {}),
            readiness_index=NumberClaim.from_dict(data.get("readiness_index") or {}),
            open_findings=[OpenFinding.from_dict(f) for f in data.get("open_findings", [])],
            lifecycle_state=data.get("lifecycle_state", WATCH),
            lifecycle_reason=data.get("lifecycle_reason", ""),
            evidence_ids=list(data.get("evidence_ids", [])),
            provenance=list(data.get("provenance", [])),
            first_seen=data.get("first_seen", ""),
            last_updated=data.get("last_updated", ""),
            analyst=data.get("analyst", "calendar_arbitrage_specialist"),
            analyst_version=data.get("analyst_version", ""),
            origin=data.get("origin", "generated"),
        )
