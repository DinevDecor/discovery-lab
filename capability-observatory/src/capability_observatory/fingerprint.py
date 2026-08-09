"""Deterministic spec_fingerprint computation.

Invariant this module exists to enforce: a fingerprint change must never be
silently treated as a continuing series. This module only computes the
fingerprint; deciding what a change MEANS (break, and whether it should ever
be resolved) lives in identity.py, never here.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from .canonical import canonical_json, canonicalize_identity_value, sha256_hex

#: Matches constraint-archaeology-agents/src/ca_agents/sensor.py's own
#: _fingerprint() truncation length -- reused for repo-wide consistency
#: rather than picking a new number.
FINGERPRINT_HASH_LENGTH = 20


def compute_spec_fingerprint(
    identity_field_names: List[str],
    identity_values: Dict[str, Any],
) -> Tuple[Optional[str], bool]:
    """Returns (spec_fingerprint, identity_incomplete).

    identity_field_names is the panel item's declared identity schema.
    identity_values is whatever the executor actually supplied for this
    capture.

    A missing, empty, or None value for ANY declared identity field makes
    the result (None, True) -- never fingerprinted with a placeholder. A
    None fingerprint must never be compared as equal OR different to a
    prior one; callers must skip continuity checking entirely when this
    returns identity_incomplete=True.
    """
    if not identity_field_names:
        return None, True

    canonical_identity: Dict[str, Any] = {}
    for field_name in identity_field_names:
        value = identity_values.get(field_name)
        if value is None or (isinstance(value, str) and not value.strip()):
            return None, True
        canonical_identity[field_name] = canonicalize_identity_value(value)

    material = canonical_json({
        "fields": sorted(identity_field_names),
        "identity": canonical_identity,
    })
    digest = sha256_hex(material)[:FINGERPRINT_HASH_LENGTH]
    return digest, False
