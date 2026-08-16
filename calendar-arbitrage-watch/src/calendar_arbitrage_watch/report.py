"""Material-event detection + the daily brief renderer.

'Silence is the default' (docs/operations/bca-daily-pipeline.md): most
runs should report NO MATERIAL CALENDAR CHANGE. Only six things are
material, matching the approved architecture review's DAILY OUTPUT
section: new signals (capped at 5 shown), promotions, degradations, dead
clocks, material evidence changes, and one best next action.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .models import REJECTED, STATE_RANK as _RANK

MAX_NEW_SIGNALS_SHOWN = 5


@dataclass
class MaterialEvents:
    new_signals: List[Dict[str, Any]] = field(default_factory=list)
    promotions: List[Dict[str, Any]] = field(default_factory=list)
    degradations: List[Dict[str, Any]] = field(default_factory=list)
    dead_clocks: List[Dict[str, Any]] = field(default_factory=list)
    material_evidence_changes: List[Dict[str, Any]] = field(default_factory=list)

    def is_empty(self) -> bool:
        return not any([self.new_signals, self.promotions, self.degradations,
                        self.dead_clocks, self.material_evidence_changes])


def detect_material_events(previous_current: List[Dict[str, Any]],
                            new_current: List[Dict[str, Any]]) -> MaterialEvents:
    """Pure function over two snapshot 'current' lists (previous run's and
    this run's), both as plain dicts (CalendarAssessment.to_dict() shape).
    Never reads or writes a file itself."""
    prev_by_id = {r["candidate_id"]: r for r in previous_current}
    events = MaterialEvents()

    for record in new_current:
        cid = record["candidate_id"]
        prev = prev_by_id.get(cid)
        state = record["lifecycle_state"]

        if prev is None:
            events.new_signals.append(record)
            continue

        prev_state = prev["lifecycle_state"]
        if state == REJECTED and prev_state != REJECTED:
            events.dead_clocks.append(record)
        elif _RANK.get(state, 0) > _RANK.get(prev_state, 0):
            events.promotions.append(record)
        elif _RANK.get(state, 0) < _RANK.get(prev_state, 0) and state != REJECTED:
            events.degradations.append(record)
        elif _shock_forecast_changed(prev, record):
            events.material_evidence_changes.append(record)

    return events


def _shock_forecast_changed(prev: Dict[str, Any], new: Dict[str, Any]) -> bool:
    p = prev.get("shock_forecast") or {}
    n = new.get("shock_forecast") or {}
    return (p.get("forecast_version") != n.get("forecast_version")
            or (p.get("date_bound") or {}) != (n.get("date_bound") or {}))


def pick_best_next_action(new_current: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Exactly one recommendation, never a ranked list (headquarters'
    Attention Engine precedent: 'never Top 10'). Candidates already at a
    MAX_AUTOMATIC state, ranked by Rivalry Index value (highest first -
    more demand relative to supply means more urgency, ties broken by
    candidate_id for reproducibility), are the ones genuinely waiting on
    the human gate. Every other candidate is reported in the brief's own
    listings, never as a second priority list."""
    from .models import MAX_AUTOMATIC_STATES
    waiting = [r for r in new_current if r["lifecycle_state"] in MAX_AUTOMATIC_STATES]
    if not waiting:
        return None

    def sort_key(r):
        ri = ((r.get("rivalry") or {}).get("rivalry_index") or {}).get("value")
        return (-(ri if ri is not None else -1.0), r["candidate_id"])

    waiting.sort(key=sort_key)
    return waiting[0]


def render_report(as_of: str, events: MaterialEvents, best_action: Optional[Dict[str, Any]],
                   open_findings_summary: List[Dict[str, Any]]) -> str:
    lines = [f"# Calendar Arbitrage Watch — daily brief — {as_of}", ""]

    if events.is_empty():
        lines.append("**NO MATERIAL CALENDAR CHANGE**")
        lines.append("")
        _append_open_findings(lines, open_findings_summary)
        return "\n".join(lines)

    shown_new = events.new_signals[:MAX_NEW_SIGNALS_SHOWN]
    lines.append(f"## New signals ({len(shown_new)} of {len(events.new_signals)} shown)")
    for r in shown_new:
        lines.append(f"- `{r['candidate_id']}` — {r.get('title', '')} ({r.get('category', '')}, {r.get('mode', '')})")
    lines.append("")

    lines.append(f"## Promotions ({len(events.promotions)})")
    for r in events.promotions:
        lines.append(f"- `{r['candidate_id']}` — {r.get('title', '')} -> {r['lifecycle_state']}")
    lines.append("")

    lines.append(f"## Degradations ({len(events.degradations)})")
    for r in events.degradations:
        lines.append(f"- `{r['candidate_id']}` — {r.get('title', '')} -> {r['lifecycle_state']}")
    lines.append("")

    lines.append(f"## Dead clocks ({len(events.dead_clocks)})")
    for r in events.dead_clocks:
        lines.append(f"- `{r['candidate_id']}` — {r.get('title', '')} — {r.get('lifecycle_reason', '')}")
    lines.append("")

    lines.append(f"## Material evidence changes ({len(events.material_evidence_changes)})")
    for r in events.material_evidence_changes:
        sf = r.get("shock_forecast") or {}
        lines.append(f"- `{r['candidate_id']}` — T_shock forecast v{sf.get('forecast_version')} "
                     f"({sf.get('shock_type')}, as_of {sf.get('as_of')})")
    lines.append("")

    lines.append("## One best next action")
    if best_action is None:
        lines.append("No candidate is currently waiting at a MAX_AUTOMATIC state — nothing needs the human gate today.")
    else:
        lines.append(f"`{best_action['candidate_id']}` — {best_action.get('title', '')} is at "
                     f"**{best_action['lifecycle_state']}**. Human decision required — this package never "
                     "acts past this state (see CONTRACT.md's Human Authority Boundary).")
    lines.append("")

    _append_open_findings(lines, open_findings_summary)
    return "\n".join(lines)


def _append_open_findings(lines: List[str], open_findings_summary: List[Dict[str, Any]]) -> None:
    if not open_findings_summary:
        return
    lines.append("## Open findings (non-scoring, for review)")
    for f in open_findings_summary:
        lines.append(f"- `{f.get('finding_id')}` on `{f.get('candidate_id')}`: {f.get('note', '')}")
    lines.append("")


def write_report(reports_dir: str, as_of: str, text: str) -> str:
    os.makedirs(reports_dir, exist_ok=True)
    path = os.path.join(reports_dir, f"daily-{as_of}.md")
    with open(path, "w", encoding="utf-8") as f:  # write mode - report.py is an allowed-write module
        f.write(text)
    return path
