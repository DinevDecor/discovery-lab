"""Renders the human-readable report. The only two modules in this
package allowed to write a file are this one and ledger.py - enforced by
tests/test_safety.py.

This report answers exactly one question per record: did this constraint
change, and how do we know? It never recommends a product, a market, or
an action - there is no field in the schema for one (schema.py has none,
by design - see the design doc §14) and this renderer does not invent
one either. If a sentence here starts to read like a pitch, that is a
bug in this file, not a feature.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List

from .schema import (
    INCREMENTAL, INSUFFICIENT_DATA, INVERTED, MULTIPLE_X, ORDER_OF_MAGNITUDE, SHIFTED,
    STILL_BINDING, WEAKENED,
)

_STATE_ORDER = (WEAKENED, SHIFTED, INVERTED, STILL_BINDING, INSUFFICIENT_DATA)
_MAGNITUDE_RANK = {ORDER_OF_MAGNITUDE: 0, MULTIPLE_X: 1, INCREMENTAL: 2, "DIRECTION_ONLY": 3,
                    INSUFFICIENT_DATA: 4}


def _fmt_evidence(items: List[Dict[str, Any]], limit: int = 2) -> str:
    if not items:
        return "(none)"
    parts = [f"{e.get('citation', '?')} ({e.get('as_of_date', '?')})" for e in items[:limit]]
    more = f" +{len(items) - limit} more" if len(items) > limit else ""
    return "; ".join(parts) + more


def _find_conflicts(records: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
    """Records sharing (constraint_family, domain, constrained_activity)
    but disagreeing on current_constraint_state - surfaced, never
    auto-resolved. See CONTRACT.md: conflicting claims are preserved."""
    groups: Dict[tuple, List[Dict[str, Any]]] = {}
    for r in records:
        key = (r["constraint_family"], r["domain"], r["constrained_activity"])
        groups.setdefault(key, []).append(r)
    conflicts = []
    for key, group in groups.items():
        states = {g["current_constraint_state"] for g in group}
        if len(group) > 1 and len(states) > 1:
            conflicts.append(group)
    return conflicts


def render(path: str, snapshot: Dict[str, Any], newly_added_ids: List[str], now: str) -> None:
    current = snapshot["current"]
    superseded = snapshot["superseded"]
    by_id = {r["record_id"]: r for r in current}

    lines = [
        f"# Constraint Change Observatory — {now}", "",
        f"Current records: **{len(current)}** · Superseded: **{len(superseded)}** · "
        f"Newly added this run: **{len(newly_added_ids)}**", "",
        "This report states, per constraint, whether the evidence shows it weakened, still "
        "binds, shifted to a different bottleneck, or inverted. It does not assess what that "
        "means commercially - no field in this schema exists for such a judgment, and none is "
        "added here. See `CONTRACT.md`.", "",
    ]

    lines += ["## Newly added constraint changes", ""]
    new_records = [by_id[rid] for rid in newly_added_ids if rid in by_id]
    if not new_records:
        lines.append("_None this run._\n")
    for r in new_records:
        lines.append(f"- **{r['record_id']}** ({r['constraint_family']} / {r['domain']}) → "
                      f"`{r['current_constraint_state']}` — {r['constrained_activity']}")
    lines.append("")

    lines += ["## Constraint states", ""]
    by_state: Dict[str, List[Dict[str, Any]]] = {}
    for r in current:
        by_state.setdefault(r["current_constraint_state"], []).append(r)
    for state in _STATE_ORDER:
        group = by_state.get(state, [])
        lines.append(f"- **{state}**: {len(group)}" +
                      (f" — {', '.join(sorted(r['record_id'] for r in group))}" if group else ""))
    lines.append("")

    lines += ["## Old bottleneck → new bottleneck transitions", ""]
    transitions = [r for r in current if r["current_constraint_state"] in (SHIFTED, INVERTED)
                    and r.get("replacement_constraint")]
    if not transitions:
        lines.append("_None this run._\n")
    for r in sorted(transitions, key=lambda r: r["record_id"]):
        rc = r["replacement_constraint"]
        lines.append(f"- **{r['record_id']}** [{r['current_constraint_state']}]: "
                      f"`{r['constraint_family']}` ({r['historical_constraint']['statement']}) → "
                      f"`{rc.get('family') or '?'}` ({rc.get('statement') or '(no statement)'}) "
                      f"[{rc.get('evidence_status')}]")
    lines.append("")

    lines += ["## Strongest quantitative changes", ""]
    deltas = []
    for r in current:
        for dim, dd in (r.get("constraint_delta") or {}).items():
            deltas.append((r["record_id"], dim, dd))
    deltas.sort(key=lambda t: _MAGNITUDE_RANK.get(t[2].get("magnitude_class"), 9))
    strong = [d for d in deltas if d[2].get("magnitude_class") in (ORDER_OF_MAGNITUDE, MULTIPLE_X)]
    if not strong:
        lines.append("_None this run._\n")
    for record_id, dim, dd in strong:
        ratio_str = f", ratio={dd['ratio']:.4g}" if dd.get("ratio") is not None else ""
        lines.append(f"- **{record_id}**.`{dim}` [{dd.get('magnitude_class')}]: "
                      f"{dd.get('then_value')} → {dd.get('now_value')} {dd.get('unit') or ''}{ratio_str}")
    lines.append("")

    lines += ["## Still-binding constraints", ""]
    still = by_state.get(STILL_BINDING, [])
    if not still:
        lines.append("_None this run._\n")
    for r in sorted(still, key=lambda r: r["record_id"]):
        lines.append(f"- **{r['record_id']}**: `{r['constraint_family']}` on {r['constrained_activity']} — "
                      f"current evidence: {_fmt_evidence(r.get('current_evidence', []))}")
    lines.append("")

    lines += ["## INSUFFICIENT_DATA", ""]
    insuff = by_state.get(INSUFFICIENT_DATA, [])
    if not insuff:
        lines.append("_None this run._\n")
    for r in sorted(insuff, key=lambda r: r["record_id"]):
        lines.append(f"- **{r['record_id']}**: `{r['constraint_family']}` on {r['constrained_activity']} — "
                      "no current_evidence established the original constraint's present state")
    # Field-level gaps on records that DID reach a state - honest partial-record reporting,
    # mirroring business-candidate-analyst's evidence_gaps convention.
    partial_gap_records = [r for r in current if r["current_constraint_state"] != INSUFFICIENT_DATA and
                            (r["historical_adaptation"]["evidence_status"] == INSUFFICIENT_DATA)]
    if partial_gap_records:
        lines.append("")
        lines.append("Records with a populated state but an `INSUFFICIENT_DATA` sub-claim "
                      "(not a defect - see CONTRACT.md):")
        for r in sorted(partial_gap_records, key=lambda r: r["record_id"]):
            lines.append(f"- **{r['record_id']}**: `historical_adaptation` is INSUFFICIENT_DATA")
    lines.append("")

    lines += ["## Unresolved questions", ""]
    any_q = False
    for r in sorted(current, key=lambda r: r["record_id"]):
        qs = r.get("unresolved_questions") or []
        if qs:
            any_q = True
            lines.append(f"- **{r['record_id']}**:")
            for q in qs:
                lines.append(f"  - {q}")
    if not any_q:
        lines.append("_None this run._\n")
    lines.append("")

    conflicts = _find_conflicts(current)
    lines += [f"## Possible conflicts ({len(conflicts)})", "",
               "Current records that share the same (constraint_family, domain, constrained_activity) "
               "but disagree on current_constraint_state. Neither is overwritten; both are listed here "
               "for a human to reconcile.", ""]
    if not conflicts:
        lines.append("_None this run._\n")
    for group in conflicts:
        ids = ", ".join(f"{r['record_id']}={r['current_constraint_state']}" for r in
                         sorted(group, key=lambda r: r["record_id"]))
        lines.append(f"- {group[0]['constraint_family']} / {group[0]['domain']}: {ids}")
    lines.append("")

    if superseded:
        lines += [f"## Superseded records ({len(superseded)})", "",
                   "Retained for audit, excluded from current-state sections above.", ""]
        for r in sorted(superseded, key=lambda r: r["record_id"]):
            lines.append(f"- **{r['record_id']}** — {r['constraint_family']} / {r['domain']}")
        lines.append("")

    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
