"""Builds validated ArtifactEnvelopes from a Case or a Claim. The only
place `identity.make_artifact_id`, `models.ArtifactEnvelope`, and
`validator.validate` come together - kept separate from `wrap.py` (which
only ever reads source data and builds Case/Claim objects, never an
envelope) and from `ledger.py` (which only ever writes an already-built,
already-validated envelope).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from .identity import make_artifact_id
from .models import CASE, CLAIM, Case, Claim, ArtifactEnvelope, KERNEL_VERSION
from .validator import validate

ANALYST_NAME = "case_claim_kernel"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_case_envelope(case: Case, recorded_at: Optional[str] = None) -> ArtifactEnvelope:
    envelope = ArtifactEnvelope(
        artifact_id=make_artifact_id(case.case_id),
        kind=CASE,
        recorded_at=recorded_at or utc_now_iso(),
        derived_from=list(case.derived_from),
        analyst=ANALYST_NAME,
        analyst_version=KERNEL_VERSION,
        payload=case.to_dict(),
    )
    validate(envelope)  # Case.derived_from is always [source_record_id] - never empty.
    return envelope


def build_claim_envelope(claim: Claim, recorded_at: Optional[str] = None) -> ArtifactEnvelope:
    empty = not claim.evidence
    payload = claim.to_dict()
    if empty:
        # claim.note is guaranteed non-empty by wrap.py whenever evidence
        # is empty - see wrap_bca_candidate's docstring.
        payload["provenance_note"] = claim.note
    envelope = ArtifactEnvelope(
        artifact_id=make_artifact_id(claim.claim_id),
        kind=CLAIM,
        recorded_at=recorded_at or utc_now_iso(),
        derived_from=list(claim.evidence),
        analyst=ANALYST_NAME,
        analyst_version=KERNEL_VERSION,
        payload=payload,
    )
    validate(envelope, allow_empty_provenance=empty)
    return envelope
