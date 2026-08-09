"""Validate and record one executor-supplied capture submission.

This module is the explicit boundary between FETCHING and RECORDING /
NORMALIZING (see README.md "Capture execution"). Fetching a source page is
never performed anywhere in this package -- a human or an authorized AI
executor performs it externally (an interactive browser-fetch tool, a
plain browser, etc.) and writes the result as a submission dict matching
SUBMISSION SHAPE below. Everything
from that point on -- validation, hashing, fingerprinting, continuity
checking, append-only persistence -- is this module's job, and it never
opens a network connection to do it (enforced by tests/test_safety.py).

SUBMISSION SHAPE (what an executor supplies, as one JSON object):
    panel_item_id       str, required
    source               str, required -- provider name as the executor saw it
    source_url            str, required -- the exact URL fetched
    fetched_at            str, required -- ISO-8601 UTC, when the fetch happened
    capture_outcome       str, required -- one of models.CAPTURE_OUTCOMES
    executor               str, required -- who/what performed the fetch
    raw_content            str, required -- the raw text actually fetched (or,
                            for a failure outcome, whatever evidence exists,
                            e.g. an error page body or a short description)
    notes                  str, optional
    observation             dict, optional, only meaningful when
                            capture_outcome is in OBSERVATION_PRODUCING_OUTCOMES:
        price, currency, unit, quantity_basis, lead_time_days,
        availability, quote_type, identity_values (dict of the panel
        item's declared identity_fields -> raw values as shown)

Nothing here invents a value for a field the executor did not supply.
Missing optional fields stay None; missing availability defaults to the
explicit "unknown" vocabulary member, never a guess.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from .canonical import sha256_hex, utc_now_iso
from .fingerprint import compute_spec_fingerprint
from .identity import last_known_fingerprint
from .models import (
    AVAILABILITY_VALUES,
    CAPTURE_OUTCOMES,
    Capture,
    IdentityBreak,
    Observation,
    OBSERVATION_PRODUCING_OUTCOMES,
    QUOTE_TYPES,
)
from .storage import AppendOnlyStore

REQUIRED_SUBMISSION_FIELDS = (
    "panel_item_id", "source", "source_url", "fetched_at",
    "capture_outcome", "executor", "raw_content",
)


class CaptureValidationError(ValueError):
    """Raised when a submission does not satisfy the intake contract."""


def _capture_id(panel_item_id: str, fetched_at: str, raw_content_hash: str) -> str:
    return "CAP-" + sha256_hex(f"{panel_item_id}|{fetched_at}|{raw_content_hash}")[:24]


def _observation_id(capture_id: str) -> str:
    return "OBS-" + sha256_hex(capture_id)[:24]


def _identity_break_id(panel_item_id: str, previous_fp: Optional[str], new_fp: str, capture_id: str) -> str:
    return "BRK-" + sha256_hex(f"{panel_item_id}|{previous_fp}|{new_fp}|{capture_id}")[:24]


def validate_submission(submission: Dict[str, Any], panel_item: Dict[str, Any]) -> None:
    missing = [f for f in REQUIRED_SUBMISSION_FIELDS if not submission.get(f)]
    if missing:
        raise CaptureValidationError(f"submission missing required field(s): {missing}")

    if submission["panel_item_id"] != panel_item["panel_item_id"]:
        raise CaptureValidationError(
            "submission panel_item_id does not match the supplied panel item"
        )

    outcome = submission["capture_outcome"]
    if outcome not in CAPTURE_OUTCOMES:
        raise CaptureValidationError(f"capture_outcome must be one of {CAPTURE_OUTCOMES}, got {outcome!r}")

    if outcome not in OBSERVATION_PRODUCING_OUTCOMES and submission.get("observation"):
        raise CaptureValidationError(
            f"capture_outcome={outcome!r} cannot carry an observation payload; "
            f"only {OBSERVATION_PRODUCING_OUTCOMES} may produce an Observation"
        )

    if outcome in OBSERVATION_PRODUCING_OUTCOMES:
        obs = submission.get("observation") or {}
        availability = obs.get("availability", "unknown")
        if availability not in AVAILABILITY_VALUES:
            raise CaptureValidationError(
                f"observation.availability must be one of {AVAILABILITY_VALUES}, got {availability!r}"
            )
        quote_type = obs.get("quote_type", "list_price")
        if quote_type not in QUOTE_TYPES:
            raise CaptureValidationError(
                f"observation.quote_type must be one of {QUOTE_TYPES}, got {quote_type!r}"
            )


def record_capture(
    submission: Dict[str, Any],
    panel_item: Dict[str, Any],
    captures: AppendOnlyStore,
    observations: AppendOnlyStore,
    identity_breaks: AppendOnlyStore,
) -> Dict[str, Any]:
    """Validate one submission and append whatever it produces.

    Returns a small result dict describing what was written, for the
    caller's own run summary. Idempotent: resubmitting the exact same
    (panel_item_id, fetched_at, raw_content) is a no-op, not a duplicate.
    """
    validate_submission(submission, panel_item)

    raw_content_hash = sha256_hex(submission["raw_content"])
    capture_id = _capture_id(submission["panel_item_id"], submission["fetched_at"], raw_content_hash)
    recorded_at = utc_now_iso()

    capture = Capture(
        capture_id=capture_id,
        panel_item_id=submission["panel_item_id"],
        source=submission["source"],
        source_url=submission["source_url"],
        fetched_at=submission["fetched_at"],
        capture_outcome=submission["capture_outcome"],
        raw_content_hash=raw_content_hash,
        executor=submission["executor"],
        notes=submission.get("notes", ""),
        recorded_at=recorded_at,
    )
    capture_written = captures.append(capture.to_dict())

    result: Dict[str, Any] = {
        "capture_id": capture_id,
        "capture_written": capture_written,
        "observation_id": None,
        "observation_written": False,
        "identity_break_id": None,
        "identity_break_written": False,
    }

    if not capture_written:
        # Retry of an already-recorded capture. The original submission
        # already produced whatever Observation/IdentityBreak it was going
        # to produce -- redoing that here would double-count.
        return result

    if submission["capture_outcome"] not in OBSERVATION_PRODUCING_OUTCOMES:
        return result

    obs_payload = submission.get("observation") or {}
    identity_field_names = panel_item.get("identity_fields", [])
    identity_values = obs_payload.get("identity_values", {})
    spec_fingerprint, _identity_incomplete = compute_spec_fingerprint(identity_field_names, identity_values)

    # Read the prior baseline BEFORE this observation is appended, so the
    # comparison below is against history, never against itself.
    previous_fingerprint = (
        last_known_fingerprint(observations, submission["panel_item_id"])
        if identity_field_names else None
    )

    observation_id = _observation_id(capture_id)
    observation = Observation(
        observation_id=observation_id,
        capture_id=capture_id,
        panel_item_id=submission["panel_item_id"],
        provider=panel_item.get("provider", submission["source"]),
        observed_at=submission["fetched_at"],
        price=obs_payload.get("price"),
        currency=obs_payload.get("currency"),
        unit=obs_payload.get("unit"),
        quantity_basis=obs_payload.get("quantity_basis"),
        lead_time_days=obs_payload.get("lead_time_days"),
        availability=obs_payload.get("availability", "unknown"),
        quote_type=obs_payload.get("quote_type", "list_price"),
        spec_fingerprint=spec_fingerprint,
        identity_fields=identity_values,
        origin="captured",
        recorded_at=recorded_at,
    )
    observation_written = observations.append(observation.to_dict())
    result["observation_id"] = observation_id
    result["observation_written"] = observation_written

    if (
        observation_written
        and spec_fingerprint is not None
        and previous_fingerprint is not None
        and previous_fingerprint != spec_fingerprint
    ):
        identity_break_id = _identity_break_id(
            submission["panel_item_id"], previous_fingerprint, spec_fingerprint, capture_id
        )
        identity_break = IdentityBreak(
            identity_break_id=identity_break_id,
            panel_item_id=submission["panel_item_id"],
            previous_fingerprint=previous_fingerprint,
            new_fingerprint=spec_fingerprint,
            capture_id=capture_id,
            observation_id=observation_id,
            status="UNRESOLVED",
            recorded_at=recorded_at,
        )
        identity_break_written = identity_breaks.append(identity_break.to_dict())
        result["identity_break_id"] = identity_break_id
        result["identity_break_written"] = identity_break_written

    return result
