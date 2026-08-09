"""Small, dependency-free canonicalization helpers.

Mirrors the exact conventions constraint-archaeology-agents/findings_ledger.py
already established in this repo (sorted-key JSON for stable hashing, UTC
ISO timestamps ending in "Z") rather than inventing a second style.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def canonical_json(obj) -> str:
    """Stable serialisation used for both hashing and written records."""
    return json.dumps(obj, sort_keys=True, ensure_ascii=False,
                       separators=(",", ":"), default=str)


def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonicalize_identity_value(value):
    """Deterministic normalization for one identity-field value.

    Strings: whitespace-collapsed and uppercased, so cosmetic formatting
    differences (extra spaces, case) never fake an identity break.
    Everything else (numbers) is left as-is -- already directly comparable,
    and coercing them here would risk silently changing their meaning.
    """
    if isinstance(value, str):
        return " ".join(value.split()).upper()
    return value
