"""Detects which of a run's freshly-appended registry events are material
enough to surface to a human, vs. ordinary silent accumulation.

Policy (see docs/operations/bca-daily-pipeline.md for the full contract):
WATCH candidate creation and same-state evidence_reassessed events are
never material - that is the expected, silent, day-to-day shape of the
system. Only these cross a threshold worth a human's attention:

  1. WATCH -> VALIDATING
  2. VALIDATING -> INVESTIGATE
  3. INVESTIGATE -> PROMISING
  4. any transition to REJECTED from VALIDATING or higher
     (REJECTED directly from WATCH is not material - it never earned
     attention in the first place)
  5. a candidates_merged event whose target (merged_into) ALSO had a
     state_changed event in the same run - a merge that left lifecycle
     state unchanged (the common case) is not material
  6. pipeline failures - handled separately by the orchestrator, since
     they are not BCA registry events at all

This module only implements 1-5: a pure function over already-appended
event dicts, no I/O, so it is trivially unit-testable offline.
"""

from __future__ import annotations

from typing import Any, Dict, List

_ESCALATIONS = {
    ("WATCH", "VALIDATING"),
    ("VALIDATING", "INVESTIGATE"),
    ("INVESTIGATE", "PROMISING"),
}
_SUBSTANTIAL_STATES = {"VALIDATING", "INVESTIGATE", "PROMISING"}


def detect_material_events(new_events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """`new_events`: the event dicts appended by ONE run, in file order
    (e.g. `registry.all_events()[events_before:]`). Returns material-event
    dicts ordered the same way, each carrying enough context to explain
    itself without re-reading the full registry."""
    merged_into_targets_this_run = {
        e["payload"]["merged_into"]
        for e in new_events
        if e["event_type"] == "candidates_merged"
    }

    material: List[Dict[str, Any]] = []
    for e in new_events:
        if e["event_type"] != "state_changed":
            continue
        from_state = e["payload"]["from_state"]
        to_state = e["payload"]["to_state"]
        entry = {
            "candidate_id": e["candidate_id"],
            "event_id": e["event_id"],
            "recorded_at": e["recorded_at"],
            "from_state": from_state,
            "to_state": to_state,
            "reason": e.get("reason", ""),
        }
        if (from_state, to_state) in _ESCALATIONS:
            material.append({**entry, "material_type": "lifecycle_escalation"})
        elif to_state == "REJECTED" and from_state in _SUBSTANTIAL_STATES:
            material.append({**entry, "material_type": "lifecycle_rejection"})
        elif e["candidate_id"] in merged_into_targets_this_run:
            material.append({**entry, "material_type": "merge_with_lifecycle_change"})
    return material
