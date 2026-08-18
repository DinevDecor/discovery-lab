"""Deterministic identity assignment. This module has exactly one job:
turn an already-existing source id into a stable case_id/claim_id, and
never anything else.

NO FUZZY OR SEMANTIC IDENTITY INFERENCE, BY CONSTRUCTION
    Every function here is a pure hash of an explicit identity tuple the
    caller already knows to be correct - never a text-similarity score,
    never an embedding distance, never a "these look like the same thing"
    judgment. That kind of matching is exactly what
    `capability_observatory`'s ADR 002 (`docs/decisions/002-c3-identity-
    continuity-asserted-not-assumed.md`) rejected for a harder version of
    this same problem ("Automatic merging when the fingerprint match rate
    is 'high enough' ... was considered and rejected. No threshold is safe
    enough to automate.") - this module holds itself to the same rule one
    level up: identity is asserted from an already-known source id, never
    inferred from content.

IDENTITY, NOT CONTENT
    `make_case_id`/`make_claim_id` hash only the fields that name WHICH
    real-world record this is - never `status`/`value`/`evidence`/any
    other field that legitimately changes between runs. This is a
    deliberate difference from `ca_agents.findings_ledger.make_finding_id`,
    which correctly hashes `derived_from` too (a Finding's identity IS what
    it was derived from). A Case's identity is the source record it wraps,
    full stop - that must not change just because the source record's
    dimensions were re-evaluated. Content drift belongs to the ledger's
    append-only history (see ledger.py), never to the id.
"""

from __future__ import annotations

import hashlib
import json
from typing import Sequence

from .models import KERNEL_VERSION


def _canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str)


def make_case_id(source_system: str, source_record_type: str, source_record_id: str) -> str:
    """Deterministic id from (source_system, source_record_type,
    source_record_id) alone. Re-running this function against the same
    source record, on any day, always returns the same case_id - that is
    the entire acceptance test for this function.
    """
    material = _canonical({
        "v": KERNEL_VERSION,
        "source_system": source_system,
        "source_record_type": source_record_type,
        "source_record_id": source_record_id,
    })
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()[:32]
    return f"case:{digest}"


def make_claim_id(case_id: str, name: str) -> str:
    """Deterministic id from (case_id, name) alone - never from the
    claim's own status/value/evidence, so a Claim's identity survives a
    later re-run that revises its content (see module docstring).
    """
    material = _canonical({"v": KERNEL_VERSION, "case_id": case_id, "name": name})
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()[:32]
    return f"claim:{digest}"


def make_artifact_id(identity_id: str) -> str:
    """The ArtifactEnvelope's own id is simply the Case/Claim id it
    carries - not a third, independently-hashed identity scheme. An
    envelope has no identity of its own beyond the object it wraps; giving
    it one would let the same Case end up under two different envelope
    ids on two different runs, which would break requirement 6
    (re-running produces exactly the same ids) for no benefit.
    """
    return identity_id


def stable_evidence_ids(evidence: Sequence[str]) -> list:
    """Evidence/observation id lists are copied through verbatim and
    sorted only for deterministic serialization - sorting never changes
    which ids are present, only their on-disk order, so this cannot be
    mistaken for the kind of interpretation this module otherwise refuses
    to do.
    """
    return sorted(dict.fromkeys(evidence))
