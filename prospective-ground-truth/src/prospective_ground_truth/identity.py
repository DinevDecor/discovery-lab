"""Deterministic identity assignment - same convention as
`case_claim_kernel.identity`/`adversarial_review_kernel.identity`:
identity is a hash of the fields that name WHICH real-world case this is,
never of fields that legitimately vary (evidence content, rationale
text). Re-running registration with the same identity tuple always
produces the same id - that is the whole acceptance test.
"""

from __future__ import annotations

import hashlib
import json

from .models import PROTOCOL_VERSION


def _canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str)


def make_prospective_case_id(domain: str, proposition: str, t0_cutoff: str) -> str:
    """Identity = (domain, proposition, t0_cutoff) only - never the
    evidence list or resolution criteria, so this id is stable even if a
    future tool re-derives the same case from the same real-world freeze
    point with, say, differently-worded evidence quotes."""
    material = _canonical({
        "v": PROTOCOL_VERSION,
        "domain": domain,
        "proposition": proposition,
        "t0_cutoff": t0_cutoff,
    })
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()[:32]
    return f"pgt-case:{digest}"


def make_resolution_id(prospective_case_id: str, outcome: str, resolved_at: str) -> str:
    """Identity = (prospective_case_id, outcome, resolved_at). A case is
    expected to receive exactly one Resolution in the normal case, but
    this is not hashed over the full record so an accidental re-append of
    the exact same resolution call is idempotent rather than a duplicate
    line - matching every other ledger's append() contract in this repo."""
    material = _canonical({
        "v": PROTOCOL_VERSION,
        "prospective_case_id": prospective_case_id,
        "outcome": outcome,
        "resolved_at": resolved_at,
    })
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()[:32]
    return f"pgt-resolution:{digest}"
