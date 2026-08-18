"""Envelope validation. Mirrors `ca_agents.findings_ledger.validate()`
field-for-field (non-empty ids, UTC-Z timestamps, non-empty
`derived_from` unless explicitly justified) - deliberately re-implemented
rather than imported, for the same "read data, never code, across
packages" reason given in wrap.py and models.py.
"""

from __future__ import annotations

from .models import ARTIFACT_KINDS, ArtifactEnvelope, ORIGIN_GENERATED


class EnvelopeValidationError(ValueError):
    pass


def validate(envelope: ArtifactEnvelope, allow_empty_provenance: bool = False) -> None:
    if envelope.kind not in ARTIFACT_KINDS:
        raise EnvelopeValidationError(f"unknown kind: {envelope.kind!r}")

    if envelope.origin != ORIGIN_GENERATED:
        raise EnvelopeValidationError(
            "Case/Claim envelopes are derived; origin must be "
            f"{ORIGIN_GENERATED!r}. Raw evidence does not belong in this ledger."
        )

    for name in ("artifact_id", "recorded_at", "analyst", "analyst_version"):
        value = getattr(envelope, name)
        if not isinstance(value, str) or not value:
            raise EnvelopeValidationError(f"{name} must be a non-empty string")

    if not envelope.recorded_at.endswith("Z"):
        raise EnvelopeValidationError("recorded_at must be UTC ISO ending in 'Z'")

    if not isinstance(envelope.derived_from, list) or \
            any(not isinstance(x, str) or not x for x in envelope.derived_from):
        raise EnvelopeValidationError("derived_from must be a list of non-empty strings")

    if not envelope.derived_from:
        if not allow_empty_provenance:
            raise EnvelopeValidationError(
                f"{envelope.kind} has empty derived_from; pass "
                "allow_empty_provenance=True and set payload['provenance_note']"
            )
        if not envelope.payload.get("provenance_note"):
            raise EnvelopeValidationError(
                "empty provenance requires payload['provenance_note'] stating why"
            )

    if not isinstance(envelope.payload, dict):
        raise EnvelopeValidationError("payload must be an object")
