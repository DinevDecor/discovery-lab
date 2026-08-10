"""Renders the human-readable report. The only two modules in this
package allowed to write a file are this one and registry.py (report.py
writes only under business-candidate-analyst/reports/) - enforced by
tests/test_safety.py.
"""

from __future__ import annotations

import datetime as dt
import os
from typing import Any, Dict, List

STATE_RANK = {"REJECTED": -1, "WATCH": 0, "VALIDATING": 1, "INVESTIGATE": 2, "PROMISING": 3}

_DIM_ORDER = [
    "underlying_job_or_problem", "pain_severity", "economic_consequence", "frequency",
    "identifiable_buyer", "current_workaround", "why_solutions_fail", "potential_product_function",
    "willingness_to_pay", "scalability", "evidence_diversity", "independent_observation_count",
    "contradictory_evidence", "confidence_quality",
]


def _fmt_value(v: Any) -> str:
    if isinstance(v, list):
        return "; ".join(str(x) for x in v[:3]) + (" …" if len(v) > 3 else "")
    if isinstance(v, dict):
        return ", ".join(f"{k}={v[k]}" for k in v)
    return str(v)


def _dims_lines(dims: Dict[str, Any]) -> List[str]:
    lines = []
    for name in _DIM_ORDER:
        d = dims.get(name)
        if not d:
            continue
        mark = "✓" if d["status"] == "EVIDENCED" else "·"
        lines.append(f"  - {mark} **{name}**: {d['status']} — {_fmt_value(d['value'])}"
                      + (f" _(evidence: {', '.join(d['evidence'][:4])}{'…' if len(d['evidence']) > 4 else ''})_"
                         if d.get("evidence") else ""))
    return lines


def _candidate_header(entry: Dict[str, Any]) -> str:
    cid = entry.get("candidate_id") or "(not created)"
    state = entry.get("state") or ""
    return f"### {cid} — {state}" if state else f"### {cid}"


def render(path: str, result: Dict[str, Any]) -> None:
    now = result["now"]
    reports = result["group_reports"]
    candidates_by_id = {c.candidate_id: c for c in result["candidates"]}

    created = [g for g in reports if g["kind"] == "created"]
    merged = [g for g in reports if g["kind"] == "merged"]
    not_yet_watch = [g for g in reports if g["kind"] == "not_yet_watch"]

    state_changes = [g for g in reports if g["kind"] == "state_changed"]
    strengthened = [g for g in state_changes if g["state"] != "REJECTED"
                    and STATE_RANK[g["state"]] > STATE_RANK[g["from_state"]]]
    weakened = [g for g in state_changes if g["state"] != "REJECTED"
                and STATE_RANK[g["state"]] < STATE_RANK[g["from_state"]]]
    rejected = [g for g in state_changes if g["state"] == "REJECTED"] + \
               [g for g in created if g["state"] == "REJECTED"]

    approaching = []
    for g in reports:
        audit = g.get("audit") or {}
        if g.get("state") == "VALIDATING":
            missing = audit.get("INVESTIGATE", {}).get("missing", [])
            if 0 < len(missing) <= 1:
                approaching.append((g, "INVESTIGATE", missing))
        elif g.get("state") == "INVESTIGATE":
            missing = audit.get("PROMISING", {}).get("missing", [])
            if 0 < len(missing) <= 1:
                approaching.append((g, "PROMISING", missing))

    lines = [
        f"# Business Candidate Analyst — {now}", "",
        f"Anomalies considered: **{result['anomalies_considered']}** · "
        f"Opportunity groups formed: **{result['groups_formed']}** · "
        f"Registry events appended: **{result['events_appended']}** · "
        f"Candidates on file: **{len(candidates_by_id)}**", "",
        "This report is produced by a downstream, read-only consumer of Constraint "
        "Archaeology's published evidence (`observations.jsonl`, `anomalies.json`, "
        "`latest-evaluations.json`). It never modifies that evidence, never calls a "
        "model, and never searches the web — see `CONTRACT.md`.", "",
        "## Candidates by state", "",
    ]
    by_state: Dict[str, List[str]] = {}
    for c in candidates_by_id.values():
        by_state.setdefault(c.state, []).append(c.candidate_id)
    for state in ("PROMISING", "INVESTIGATE", "VALIDATING", "WATCH", "REJECTED"):
        ids = sorted(by_state.get(state, []))
        lines.append(f"- **{state}**: {len(ids)}" + (f" — {', '.join(ids)}" if ids else ""))
    lines.append("")

    lines += [f"## New candidates ({len(created)})", ""]
    if not created:
        lines.append("_None this run._\n")
    for g in created:
        lines.append(_candidate_header(g))
        lines.append(f"From anomalies: `{', '.join(g['anomaly_ids'])}`")
        lines += _dims_lines(g["dims"])
        lines.append("")

    lines += [f"## Strengthened ({len(strengthened)})", ""]
    if not strengthened:
        lines.append("_None this run._\n")
    for g in strengthened:
        lines.append(f"- **{g['candidate_id']}**: {g['from_state']} → {g['state']} "
                      f"(anomalies: `{', '.join(g['anomaly_ids'])}`)")
    lines.append("")

    lines += [f"## Weakened ({len(weakened)})", ""]
    if not weakened:
        lines.append("_None this run._\n")
    for g in weakened:
        lines.append(f"- **{g['candidate_id']}**: {g['from_state']} → {g['state']} "
                      f"(anomalies: `{', '.join(g['anomaly_ids'])}`)")
    lines.append("")

    lines += [f"## Merged ({len(merged)})", ""]
    if not merged:
        lines.append("_None this run._\n")
    for g in merged:
        lines.append(f"- **{g['candidate_id']}** merged into **{g['merged_into']}** "
                      f"(bridging anomalies: `{', '.join(g['anomaly_ids'])}`)")
    lines.append("")

    lines += [f"## Rejected ({len(rejected)})", ""]
    if not rejected:
        lines.append("_None this run._\n")
    for g in rejected:
        lines.append(f"- **{g['candidate_id']}** (anomalies: `{', '.join(g['anomaly_ids'])}`)")
    lines.append("")

    lines += [f"## Approaching INVESTIGATE / PROMISING ({len(approaching)})", ""]
    if not approaching:
        lines.append("_None this run._\n")
    for g, target, missing in approaching:
        lines.append(f"- **{g['candidate_id']}** ({g['state']}) is one step from **{target}** — "
                      f"missing: {missing[0]}")
    lines.append("")

    if not_yet_watch:
        lines += [f"## Evidence seen but not yet a WATCH candidate ({len(not_yet_watch)})", "",
                   "Anomaly groups that did not clear the minimum bar (identifiable buyer + current "
                   "workaround + why existing solutions fail, all EVIDENCED). Recorded here for "
                   "transparency only — nothing is written to the registry for these.", ""]
        for g in not_yet_watch[:20]:
            lines.append(f"- anomalies `{', '.join(g['anomaly_ids'])}` — missing: {g['watch_missing']}")
        if len(not_yet_watch) > 20:
            lines.append(f"- … and {len(not_yet_watch) - 20} more")
        lines.append("")

    lines += ["## Why — full dimension detail for every touched candidate", ""]
    for g in reports:
        if g["kind"] in ("not_yet_watch", "merged") or not g.get("dims"):
            continue
        lines.append(_candidate_header(g))
        lines += _dims_lines(g["dims"])
        lines.append("")

    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
