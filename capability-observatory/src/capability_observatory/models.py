"""Record shapes for C3.

Three append-only kinds, matching the Reality Observatory design doc's
RAW CAPTURE / RAW OBSERVATION / (never: DERIVED FINDING) split:

    Capture        what a source contained at a point in time (or that we
                   failed to read it) -- written for every submission.
    Observation    a typed reading extracted from exactly one successful
                   Capture -- written only when the capture produced
                   trustworthy content.
    IdentityBreak  a flag that a panel item's spec_fingerprint changed --
                   written instead of silently continuing the series.

C3 never writes a Finding. There is no fourth dataclass here for that
reason, not by omission.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Any, Dict, Optional

#: Closed vocabulary. A capture is always exactly one of these -- never
#: inferred after the fact from whether an Observation happened to result.
CAPTURE_OUTCOMES = ("ok", "unavailable", "access_blocked", "parse_error", "source_missing")

#: Only these outcomes may produce an Observation. "access_blocked",
#: "parse_error" and "source_missing" mean we have no trustworthy content
#: to assert anything from -- the Capture record is still written (failure
#: is evidence), but no Observation follows it.
OBSERVATION_PRODUCING_OUTCOMES = ("ok", "unavailable")

AVAILABILITY_VALUES = (
    "in_stock", "out_of_stock", "backorder", "discontinued",
    "contact_for_availability", "unknown",
)

#: Only list_price is supported in this slice -- see docs on why negotiated/
#: contract pricing is out of scope. The field exists so adding that mode
#: later is a vocabulary extension, not a schema break.
QUOTE_TYPES = ("list_price",)

#: C3 never uses a model to interpret content; every C3 Observation is a
#: structural reading of what was displayed. "generated" is not a value
#: this package ever writes, but the field itself follows the ledger's own
#: origin convention (constraint-archaeology-agents/findings_ledger.py).
ORIGIN_VALUES = ("captured",)


@dataclass(frozen=True)
class Capture:
    capture_id: str
    panel_item_id: str
    source: str
    source_url: str
    fetched_at: str
    capture_outcome: str
    raw_content_hash: str
    executor: str
    notes: str = ""
    recorded_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Observation:
    observation_id: str
    capture_id: str
    panel_item_id: str
    provider: str
    observed_at: str
    price: Optional[float]
    currency: Optional[str]
    unit: Optional[str]
    quantity_basis: Optional[str]
    lead_time_days: Optional[float]
    availability: str
    quote_type: str
    spec_fingerprint: Optional[str]
    identity_fields: Dict[str, Any] = field(default_factory=dict)
    origin: str = "captured"
    recorded_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class IdentityBreak:
    identity_break_id: str
    panel_item_id: str
    previous_fingerprint: Optional[str]
    new_fingerprint: str
    capture_id: str
    observation_id: str
    status: str
    recorded_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
