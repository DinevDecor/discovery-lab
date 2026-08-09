"""The one submission envelope this executor produces.

Deliberately NOT a second ontology. C3's own Capture/Observation shape
(capability_observatory/models.py, capture_intake.py) is the only
authoritative schema. This envelope is executor-side convenience: it
carries a few fields C3's submission shape has no first-class home for yet
(final_url, capture_method, http/api status, structured error_category),
and folds them into C3's existing `notes` field as plain, readable text
rather than inventing new required fields on the wire. `to_c3_submission()`
is the one place that mapping happens; nothing else needs to know about it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from capability_observatory.models import CAPTURE_OUTCOMES, OBSERVATION_PRODUCING_OUTCOMES

#: Free-text convention, matching the "<kind>:<identifier>" shape already
#: used by real submissions (executor="human:jane-doe",
#: executor="ai:claude-code-web-session-..."). Not an enum -- there is no
#: closed set of executor identities, same as today.
CAPTURE_METHODS = ("api", "html", "human")


class EnvelopeValidationError(ValueError):
    """Raised when an ExecutorSubmission cannot be turned into a valid C3
    submission -- checked here, BEFORE C3's own validate_submission runs,
    so the executor fails loudly on its own mistakes rather than relying
    on C3 to catch them."""


@dataclass(frozen=True)
class ExecutorSubmission:
    panel_item_id: str
    provider: str
    requested_url: str
    fetched_at: str
    capture_method: str          # one of CAPTURE_METHODS
    executor: str
    outcome: str                 # one of capability_observatory.models.CAPTURE_OUTCOMES
    final_url: Optional[str] = None
    http_status: Optional[int] = None
    api_status: Optional[str] = None
    error_category: Optional[str] = None
    raw_payload: Optional[str] = None
    raw_payload_reference: Optional[str] = None
    notes: str = ""
    observation: Optional[Dict[str, Any]] = None

    def validate(self) -> None:
        if not self.panel_item_id:
            raise EnvelopeValidationError("panel_item_id is required")
        if not self.provider:
            raise EnvelopeValidationError("provider is required")
        if not self.requested_url:
            raise EnvelopeValidationError("requested_url is required")
        if not self.fetched_at:
            raise EnvelopeValidationError("fetched_at is required")
        if not self.executor:
            raise EnvelopeValidationError("executor is required")
        if self.capture_method not in CAPTURE_METHODS:
            raise EnvelopeValidationError(
                f"capture_method must be one of {CAPTURE_METHODS}, got {self.capture_method!r}"
            )
        if self.outcome not in CAPTURE_OUTCOMES:
            raise EnvelopeValidationError(
                f"outcome must be one of {CAPTURE_OUTCOMES}, got {self.outcome!r}"
            )
        if self.outcome not in OBSERVATION_PRODUCING_OUTCOMES and self.observation:
            raise EnvelopeValidationError(
                f"outcome={self.outcome!r} cannot carry an observation payload"
            )
        if not self.raw_payload and not self.raw_payload_reference and not self.error_category:
            raise EnvelopeValidationError(
                "a submission must carry raw_payload, raw_payload_reference, or "
                "error_category -- never silently empty evidence"
            )

    def _synthesized_raw_content(self) -> str:
        """What C3's required, non-empty `raw_content` field becomes when
        there were no real bytes to keep (e.g. the connection never
        completed). Matches the pattern already used in the real
        week-2026-08-09 incident's own submissions: an honest description
        of what happened, never a fabricated page body."""
        parts = [f"No raw payload captured (capture_method={self.capture_method})."]
        if self.error_category:
            parts.append(f"error_category={self.error_category}.")
        if self.http_status is not None:
            parts.append(f"http_status={self.http_status}.")
        if self.api_status:
            parts.append(f"api_status={self.api_status}.")
        if self.raw_payload_reference:
            parts.append(f"raw_payload_reference={self.raw_payload_reference}.")
        return " ".join(parts)

    def _composed_notes(self) -> str:
        extras = []
        if self.final_url and self.final_url != self.requested_url:
            extras.append(f"final_url={self.final_url}")
        extras.append(f"capture_method={self.capture_method}")
        if self.http_status is not None:
            extras.append(f"http_status={self.http_status}")
        if self.api_status:
            extras.append(f"api_status={self.api_status}")
        if self.error_category:
            extras.append(f"error_category={self.error_category}")
        if self.raw_payload_reference:
            extras.append(f"raw_payload_reference={self.raw_payload_reference}")
        structured = "; ".join(extras)
        if self.notes:
            return f"{structured}; {self.notes}" if structured else self.notes
        return structured

    def to_c3_submission(self) -> Dict[str, Any]:
        """The exact shape capability_observatory.capture_intake expects.
        No field here is invented -- every value traces back to something
        this envelope was actually given."""
        self.validate()
        submission: Dict[str, Any] = {
            "panel_item_id": self.panel_item_id,
            "source": self.provider,
            "source_url": self.requested_url,
            "fetched_at": self.fetched_at,
            "capture_outcome": self.outcome,
            "executor": self.executor,
            "raw_content": self.raw_payload or self._synthesized_raw_content(),
            "notes": self._composed_notes(),
        }
        if self.observation is not None:
            submission["observation"] = self.observation
        return submission
