"""Continuity checking: the one job this module has.

Reads the append-only Observation log to find whatever spec_fingerprint was
last recorded for a panel item, so capture_intake.py can decide whether a
new fingerprint continues or breaks that series. This module never writes
anything and never decides that a break should be resolved -- resolving a
SAME_ENTITY_AS assertion is explicitly future analyst work, out of scope
for C3 (see README.md).
"""

from __future__ import annotations

from typing import Optional

from .storage import AppendOnlyStore


def last_known_fingerprint(observations_store: AppendOnlyStore, panel_item_id: str) -> Optional[str]:
    """Most recent non-null spec_fingerprint previously recorded for this
    panel item, or None if none exists yet.

    Always recomputed by scanning the append-only log in full -- there is
    no separate "latest fingerprint" cache to fall out of sync with it.
    Observations with spec_fingerprint=None (identity_incomplete at capture
    time) are skipped: an incomplete reading must never stand in as the
    baseline for a continuity comparison.
    """
    matches = [
        row for row in observations_store.read_all()
        if row.get("panel_item_id") == panel_item_id and row.get("spec_fingerprint")
    ]
    if not matches:
        return None
    matches.sort(key=lambda r: (r.get("observed_at") or "", r.get("recorded_at") or ""))
    return matches[-1]["spec_fingerprint"]
