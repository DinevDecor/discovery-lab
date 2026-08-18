"""T0 packet hashing - same canonical-JSON + sha256 approach as
`blind_analysis_kernel.packet.packet_sha256`, applied to this package's
own T0Freeze shape instead of importing that module (this package has
zero cross-package import dependency - see CONTRACT.md).

The hash covers t0_cutoff and the full evidence list, so any change to
either - a different freeze date, a reworded quote, an added or removed
evidence item - changes the hash. This is what makes "the T0 packet
never changes" independently checkable rather than merely promised:
validator.py recomputes this hash from a case's own t0.evidence and
t0.t0_cutoff and rejects the case if it disagrees with the stored
t0.packet_sha256.
"""

from __future__ import annotations

import hashlib
import json
from typing import List

from .models import T0EvidenceItem


def _canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str)


def compute_packet_sha256(t0_cutoff: str, evidence: List[T0EvidenceItem]) -> str:
    material = _canonical({
        "t0_cutoff": t0_cutoff,
        "evidence": [e.to_dict() for e in evidence],
    })
    return hashlib.sha256(material.encode("utf-8")).hexdigest()
