"""Data shapes for the X Signal Probe.

RawPost is in-memory only. Its `text` field must never be written to
any file this package persists - dedupe.py and probe.py only ever pass
it through mechanical filters/similarity checks, never to disk (see
CONTRACT.md's data-minimization rule and
tests/test_secret_never_persisted.py, which proves this dynamically).

ProbeObservation is the only representation of an X post this package
ever writes to disk. It deliberately carries no post text, no quote,
and no author identifier: `canonical_url` alone (https://x.com/i/status/
<id>, which needs no username) is enough for a human to open the live
post and verify it - so an author identifier is not necessary for
provenance, and `post_id` alone is enough for dedupe, so it is not
necessary there either. Per the approved data-minimization rule, a
field is added only when something in this package actually needs it.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import asdict, dataclass


@dataclass
class RawPost:
    post_id: str
    text: str
    created_at: str
    retrieved_at: str
    query_id: str
    query_family: str
    is_retweet: bool = False


@dataclass
class ProbeObservation:
    source: str
    post_id: str
    canonical_url: str
    created_at: str
    retrieved_at: str
    query_id: str
    query_family: str
    text_hash: str
    probe_version: str
    api_version: str
    classification: str
    matched_existing_observation_id: str = ""


def to_dict(obj) -> dict:
    return asdict(obj)


def canonical_url(post_id: str) -> str:
    """X's generic, username-independent permalink form - resolves the
    same regardless of the author's current handle, so no username or
    author_id needs to be captured just to make the post referenceable."""
    return f"https://x.com/i/status/{post_id}"


def text_hash(text: str) -> str:
    """Whitespace/case-normalized SHA-256 of post text, for dedupe and
    audit - the hash is persisted, the text it was computed from never
    is."""
    normalized = re.sub(r"\s+", " ", (text or "").strip().lower())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
