"""Human browser-assisted capture -- same envelope, same ingestion path.

Not a second truth model. A human fills in HUMAN_SUBMISSION_TEMPLATE (or an
equivalent dict with the same keys), `parse_human_submission()` turns it
into the identical ExecutorSubmission every automated path produces, and it
flows through the identical incoming/ -> capability_observatory.capture_intake
pipeline. Primary fallback for McMaster-Carr and Grainger (no viable public
API found, per the Slice 03 design doc's Section 4), and for any
AutomationDirect item the probe in automationdirect.py classifies as
PROVIDER_BLOCKED or EXECUTOR_FAILURE.
"""

from __future__ import annotations

from typing import Any, Dict

from .envelope import ExecutorSubmission

#: Fields a human must fill in. price/availability/lead_time_days are
#: optional at this dict level (an access_blocked/source_missing report has
#: none of them), but requested_url, fetched_at, executor, and
#: raw_evidence_reference are always required -- "no retrospective
#: reconstruction" (design doc Section 10) means every human submission
#: must point at real, contemporaneous evidence.
HUMAN_SUBMISSION_TEMPLATE: Dict[str, Any] = {
    "panel_item_id": "",              # e.g. "C3-009"
    "provider": "",                    # e.g. "provider_c_mcmaster"
    "requested_url": "",               # exact product page URL landed on
    "fetched_at": "",                  # ISO-8601 UTC, the moment actually viewed
    "executor": "",                    # "human:<real name or handle>"
    "outcome": "ok",                   # ok | unavailable | provider_access_blocked | source_missing | ...
    "raw_evidence_reference": "",      # screenshot/view-source file reference, kept alongside the submission
    "price": None,
    "currency": None,
    "unit": None,
    "quantity_basis": None,
    "lead_time_days": None,
    "availability": "unknown",
    "identity_values": {},
    "notes": "",
}

REQUIRED_KEYS = ("panel_item_id", "provider", "requested_url", "fetched_at", "executor",
                  "outcome", "raw_evidence_reference")


class HumanSubmissionError(ValueError):
    pass


def parse_human_submission(data: Dict[str, Any], identity_field_names=None) -> ExecutorSubmission:
    missing = [k for k in REQUIRED_KEYS if not data.get(k)]
    if missing:
        raise HumanSubmissionError(f"human submission missing required field(s): {missing}")

    if not data["executor"].startswith("human:"):
        raise HumanSubmissionError(
            f"human submission's executor must start with 'human:', got {data['executor']!r}"
        )

    from capability_observatory.models import OBSERVATION_PRODUCING_OUTCOMES

    observation = None
    if data["outcome"] in OBSERVATION_PRODUCING_OUTCOMES:
        identity_field_names = identity_field_names or []
        identity_values = {
            k: v for k, v in (data.get("identity_values") or {}).items() if k in identity_field_names
        }
        observation = {
            "price": data.get("price"),
            "currency": data.get("currency"),
            "unit": data.get("unit"),
            "quantity_basis": data.get("quantity_basis"),
            "lead_time_days": data.get("lead_time_days"),
            "availability": data.get("availability", "unknown"),
            "quote_type": "list_price",
            "identity_values": identity_values,
        }

    return ExecutorSubmission(
        panel_item_id=data["panel_item_id"],
        provider=data["provider"],
        requested_url=data["requested_url"],
        fetched_at=data["fetched_at"],
        capture_method="human",
        executor=data["executor"],
        outcome=data["outcome"],
        raw_payload_reference=data["raw_evidence_reference"],
        raw_payload=data.get("raw_payload"),
        notes=data.get("notes", ""),
        observation=observation,
    )
