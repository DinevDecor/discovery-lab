"""The ONE module in this package that reads another package's data -
mirrors the "one dispatch module carries all cross-package reads,
everything else stays standalone" convention `blind_analysis_kernel
.dispatch`/`adversarial_review_kernel.falsify` already established,
except this module's whole job IS cross-package aggregation (it is the
console's reason to exist), so it reads across every ledger this repo
has rather than exactly two providers.

READ-ONLY, STRUCTURALLY
    Every function here opens files for reading only - no writing mode
    of any kind appears anywhere in this module (tests/test_safety.py
    checks this). Nothing in this package ever writes to a CA/BCA/kernel
    data path. The one file this package DOES produce - its own
    `mobile-console/data/snapshot.json` - is written by
    `run_mobile_console.py`'s CLI, a different file, never this one.

NO INVENTED METRICS
    Every number in the returned snapshot is a direct count, sum, or max
    over records that already exist in a ledger - never a rate, a
    percentage, a trend, or a funnel-conversion figure computed by
    guessing what the "expected" prior stage size should be. A stage
    with 0 records through it is reported as 0, not omitted and not
    padded.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

CA_ANOMALIES = os.path.join(REPO_ROOT, "constraint-archaeology-agents", "data", "anomalies.json")
CA_OBSERVATIONS = os.path.join(REPO_ROOT, "constraint-archaeology-agents", "data", "observations.jsonl")
BCA_CANDIDATES = os.path.join(REPO_ROOT, "business-candidate-analyst", "data", "candidates.json")
BCA_EVENTS = os.path.join(REPO_ROOT, "business-candidate-analyst", "data", "candidate_events.jsonl")
CASE_ARTIFACTS = os.path.join(REPO_ROOT, "case-claim-kernel", "data", "artifacts.jsonl")
BLIND_ANALYSES = os.path.join(REPO_ROOT, "blind-analysis-kernel", "data", "analyses.jsonl")
BLIND_RUNS = os.path.join(REPO_ROOT, "blind-analysis-kernel", "data", "runs.jsonl")
FALSIFICATIONS = os.path.join(REPO_ROOT, "adversarial-review-kernel", "data", "falsifications.jsonl")
JUDGMENTS = os.path.join(REPO_ROOT, "adversarial-review-kernel", "data", "judgments.jsonl")
PGT_CASES = os.path.join(REPO_ROOT, "prospective-ground-truth", "data", "cases.jsonl")
PGT_RESOLUTIONS = os.path.join(REPO_ROOT, "prospective-ground-truth", "data", "resolutions.jsonl")


def _load_json(path: str, default: Any) -> Any:
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _load_jsonl(path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        return []
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def load_all() -> Dict[str, Any]:
    """Read-only load of every canonical ledger this console aggregates.
    Returns raw records, untouched - all derivation happens in the
    functions below, never here, so the read step and the compute step
    can be tested independently."""
    return {
        "anomalies": _load_json(CA_ANOMALIES, []),
        "observations": _load_jsonl(CA_OBSERVATIONS),
        "candidates": _load_json(BCA_CANDIDATES, []),
        "candidate_events": _load_jsonl(BCA_EVENTS),
        "case_artifacts": _load_jsonl(CASE_ARTIFACTS),
        "blind_analyses": _load_jsonl(BLIND_ANALYSES),
        "blind_runs": _load_jsonl(BLIND_RUNS),
        "falsifications": _load_jsonl(FALSIFICATIONS),
        "judgments": _load_jsonl(JUDGMENTS),
        "pgt_cases": _load_jsonl(PGT_CASES),
        "pgt_resolutions": _load_jsonl(PGT_RESOLUTIONS),
    }


def _is_past_watch(candidate: Dict[str, Any]) -> bool:
    """The one definition of 'past WATCH' this console uses anywhere -
    shared by compute_machine_status's candidates_past_watch count, the
    Pipeline row's own count, and the Candidates-past-WATCH drill-down
    list, so the three can never silently disagree. Any state other than
    WATCH or an absent state counts as past WATCH - unchanged from the
    rule already in place before the drill-down was added."""
    return candidate.get("state") not in ("WATCH", None)


def compute_machine_status(raw: Dict[str, Any]) -> Dict[str, Any]:
    validating_or_further = [c for c in raw["candidates"] if _is_past_watch(c)]
    pgt_awaiting = [c for c in raw["pgt_cases"]
                     if not any(r["prospective_case_id"] == c["prospective_case_id"] for r in raw["pgt_resolutions"])]
    all_timestamps = _collect_all_timestamps(raw)
    return {
        "total_observations": len(raw["observations"]),
        "total_anomalies": len(raw["anomalies"]),
        "total_candidates": len(raw["candidates"]),
        "candidates_past_watch": len(validating_or_further),
        "total_blind_analyses": len(raw["blind_analyses"]),
        "total_falsifications": len(raw["falsifications"]),
        "total_judgments": len(raw["judgments"]),
        "total_prospective_cases": len(raw["pgt_cases"]),
        "prospective_cases_awaiting_outcome": len(pgt_awaiting),
        "total_resolutions": len(raw["pgt_resolutions"]),
        "last_activity_at": max(all_timestamps) if all_timestamps else None,
    }


def _observation_summary(o: Dict[str, Any]) -> Dict[str, Any]:
    """The real, exposed fields for one observation record - shared by a
    candidate's Case facts and the Pipeline's Observations drill-down so
    the two never drift into two different ideas of what an observation
    looks like."""
    return {
        "observation_id": o["observation_id"], "source": o.get("source"), "url": o.get("url"),
        "published_at": o.get("published_at"), "process": o.get("process"), "pain": o.get("pain"),
        "failure_mode": o.get("failure_mode"), "evidence_quote": o.get("evidence_quote"),
    }


def _candidate_evidence(raw: Dict[str, Any], candidate: Dict[str, Any]) -> Dict[str, Any]:
    """Real evidence for one candidate's Case stage - the anomaly's
    canonical_pattern plus its observations' process/pain/evidence_quote,
    exactly as recorded, no rewriting."""
    obs_by_id = {o["observation_id"]: o for o in raw["observations"]}
    anomalies_by_id = {a["anomaly_id"]: a for a in raw["anomalies"]}
    anomaly = anomalies_by_id.get(candidate["anomaly_ids"][0]) if candidate.get("anomaly_ids") else None
    observations = [obs_by_id[oid] for oid in candidate.get("observation_ids", []) if oid in obs_by_id]
    return {"anomaly": anomaly, "observations": observations}


def _find_full_docket(raw: Dict[str, Any], candidate: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """A candidate has a 'full docket' (blind analysis through judgment)
    only if a real blind-analysis run's source_case_ids traces back to
    this candidate via case-claim-kernel's own case-id wrapping - never
    assumed from the candidate_id alone.

    The real pipeline wraps identity at the ANOMALY level (Stage 3 keyed
    off ANOM-0001's own case_id, not BC-0001's), so a candidate's own
    case-wrapped id AND every one of its anomaly_ids' case-wrapped ids
    are both eligible matches - both are legitimate case-claim-kernel
    identities for the same underlying real-world situation."""
    source_record_ids = {candidate["candidate_id"], *candidate.get("anomaly_ids", [])}
    case_ids_for_candidate = {
        a["artifact_id"] for a in raw["case_artifacts"]
        if a.get("kind") == "case" and a.get("payload", {}).get("source_record_id") in source_record_ids
    }
    if not case_ids_for_candidate:
        return None
    matching_run = next(
        (r for r in raw["blind_runs"] if case_ids_for_candidate & set(r.get("source_case_ids", []))), None
    )
    if not matching_run:
        return None

    analyses_by_id = {a["artifact_id"]: a for a in raw["blind_analyses"]}
    claude = analyses_by_id.get(matching_run["claude_artifact_id"])
    gpt = analyses_by_id.get(matching_run["gpt_artifact_id"])

    falsifications_for_run = [f for f in raw["falsifications"] if f.get("run_id") == matching_run["run_id"]]
    judgment = next((j for j in raw["judgments"] if j.get("source_run_id") == matching_run["run_id"]), None)

    if not (claude and gpt and judgment):
        return None
    return {
        "run_id": matching_run["run_id"],
        "claude_analysis": claude,
        "gpt_analysis": gpt,
        "falsifications": falsifications_for_run,
        "judgment": judgment,
    }


_CASE_FACT_DIMENSIONS = (
    "underlying_job_or_problem", "why_solutions_fail", "potential_product_function", "current_workaround",
)


def _real_case_facts(raw: Dict[str, Any], candidate: Dict[str, Any]) -> Dict[str, Any]:
    """Real, source-cited facts for a candidate's Case stage - used by
    every candidate that does NOT have a full docket, so 'open into the
    Case Detail docket' never means fabricating a claim for the other
    160 candidates. `dimensions` are copied verbatim, including each
    field's own `note`/`status` - a dimension the BCA pipeline itself
    marked 'FRAMING ONLY' or INSUFFICIENT_DATA is passed through with
    that same label, never upgraded to look like settled evidence."""
    ev = _candidate_evidence(raw, candidate)
    dims = candidate.get("dimensions", {})
    return {
        "anomaly": ev["anomaly"],
        "observations": [_observation_summary(o) for o in ev["observations"]],
        "dimensions": {k: dims[k] for k in _CASE_FACT_DIMENSIONS if k in dims},
    }


def compute_opportunities(raw: Dict[str, Any]) -> List[Dict[str, Any]]:
    """One entry per real BCA candidate - sorted newest-first by
    created_at, the candidate's own real timestamp, never a synthetic
    rank."""
    out = []
    for c in sorted(raw["candidates"], key=lambda c: c.get("created_at", ""), reverse=True):
        docket = _find_full_docket(raw, c)
        out.append({
            "candidate_id": c["candidate_id"],
            "candidate_type": c.get("candidate_type"),
            "state": c.get("state"),
            "pain_severity": c.get("dimensions", {}).get("pain_severity", {}).get("value"),
            "created_at": c.get("created_at"),
            "updated_at": c.get("updated_at"),
            "anomaly_ids": c.get("anomaly_ids", []),
            "has_full_docket": docket is not None,
            "case_facts": _real_case_facts(raw, c),
        })
    return out


def compute_pipeline(raw: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Every stage count is a direct len() over a real ledger - the
    order mirrors the pipeline's own README.md diagram
    (observations -> anomalies -> candidates -> blind analysis ->
    falsification -> judgment), nothing invented in between.

    Each stage's own `id` matches a key in `compute_pipeline_records()`
    (or, for "candidates", the existing `opportunities` section) - the
    drill-down list a tapped row opens is always sized from the exact
    same underlying records this count was taken from, never a second,
    independently-filtered copy."""
    return [
        {"id": "observations", "stage": "Observations captured", "count": len(raw["observations"])},
        {"id": "anomalies", "stage": "Anomalies clustered", "count": len(raw["anomalies"])},
        {"id": "candidates", "stage": "Business candidates opened", "count": len(raw["candidates"])},
        {"id": "candidates_past_watch", "stage": "Candidates past WATCH",
         "count": len([c for c in raw["candidates"] if _is_past_watch(c)])},
        {"id": "blind_analyses", "stage": "Blind dual-model analyses (Stage 3)", "count": len(raw["blind_analyses"])},
        {"id": "falsifications", "stage": "Adversarial falsifications (Stage 4)", "count": len(raw["falsifications"])},
        {"id": "judgments", "stage": "Deterministic judgments (Stage 4)", "count": len(raw["judgments"])},
    ]


def list_observations(raw: Dict[str, Any]) -> List[Dict[str, Any]]:
    """One entry per real observation record - the Pipeline's
    'Observations captured' drill-down. Unfiltered, so its length always
    equals that row's own count by construction."""
    return [_observation_summary(o) for o in raw["observations"]]


def list_anomalies(raw: Dict[str, Any]) -> List[Dict[str, Any]]:
    """One entry per real anomaly record - the Pipeline's 'Anomalies
    clustered' drill-down. Unfiltered."""
    return [{
        "anomaly_id": a["anomaly_id"],
        "canonical_pattern": a.get("canonical_pattern"),
        "status": a.get("status"),
        "first_seen": a.get("first_seen"),
        "last_seen": a.get("last_seen"),
        "observation_ids": a.get("observation_ids", []),
    } for a in raw["anomalies"]]


def list_candidates_past_watch_ids(raw: Dict[str, Any]) -> List[str]:
    """Just the ids of candidates past WATCH, via the one shared
    `_is_past_watch` predicate - the client resolves each id against the
    `opportunities` section it already has, so this list is never a
    second, heavier copy of candidate data."""
    return [c["candidate_id"] for c in raw["candidates"] if _is_past_watch(c)]


def list_blind_analyses(raw: Dict[str, Any]) -> List[Dict[str, Any]]:
    """One entry per real Stage 3 independent-analysis artifact - the
    Pipeline's 'Blind dual-model analyses' drill-down. Unfiltered."""
    out = []
    for a in raw["blind_analyses"]:
        analysis = a.get("analysis", {})
        out.append({
            "artifact_id": a["artifact_id"],
            "run_id": a.get("run_id"),
            "provider": a.get("provider"),
            "model": a.get("model"),
            "created_at": a.get("created_at"),
            "hidden_function": analysis.get("hidden_function"),
            "failure_class": analysis.get("failure_class"),
            "confidence": analysis.get("confidence"),
        })
    return out


def list_falsifications(raw: Dict[str, Any]) -> List[Dict[str, Any]]:
    """One entry per real Stage 4 falsification artifact - the
    Pipeline's 'Adversarial falsifications' drill-down. `findings_count`
    is a direct len() over that artifact's own `findings` list, the same
    license every other count in this module already uses - never a
    rate or a synthesized verdict. Unfiltered."""
    return [{
        "artifact_id": f["artifact_id"],
        "run_id": f.get("run_id"),
        "critic_provider": f.get("critic_provider"),
        "critic_model": f.get("critic_model"),
        "target_artifact_id": f.get("target_artifact_id"),
        "created_at": f.get("created_at"),
        "findings_count": len(f.get("findings", [])),
    } for f in raw["falsifications"]]


def list_judgments(raw: Dict[str, Any]) -> List[Dict[str, Any]]:
    """One entry per real Stage 4 deterministic judgment - the
    Pipeline's 'Deterministic judgments' drill-down. Unfiltered."""
    return [{
        "judgment_id": j["judgment_id"],
        "case_id": j.get("case_id"),
        "source_run_id": j.get("source_run_id"),
        "status": j.get("status"),
        "material_disagreements": j.get("material_disagreements", []),
        "created_at": j.get("created_at"),
    } for j in raw["judgments"]]


def compute_pipeline_records(raw: Dict[str, Any]) -> Dict[str, Any]:
    """The real records behind 5 of the 7 Pipeline rows. The other two
    ('candidates' and 'candidates_past_watch's full rows) are resolved by
    the client against the already-present `opportunities` section - see
    `list_candidates_past_watch_ids` - so this dict never duplicates the
    174-candidate list a second time."""
    return {
        "observations": list_observations(raw),
        "anomalies": list_anomalies(raw),
        "candidates_past_watch": list_candidates_past_watch_ids(raw),
        "blind_analyses": list_blind_analyses(raw),
        "falsifications": list_falsifications(raw),
        "judgments": list_judgments(raw),
    }


def compute_ground_truth(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Prospective Ground-Truth cases, listed on their own terms - never
    presented as a continuation of any Stage 4 case unless that specific
    case's own source_case_id field says so."""
    resolutions_by_case: Dict[str, List[Dict[str, Any]]] = {}
    for r in raw["pgt_resolutions"]:
        resolutions_by_case.setdefault(r["prospective_case_id"], []).append(r)

    cases = []
    for c in raw["pgt_cases"]:
        case_resolutions = resolutions_by_case.get(c["prospective_case_id"], [])
        status = "OPEN"
        if case_resolutions:
            latest = max(case_resolutions, key=lambda r: r.get("resolved_at", ""))
            status = latest["outcome"] if latest["outcome"] not in ("POSITIVE", "NEGATIVE", "AMBIGUOUS") else "RESOLVED"
        cases.append({
            "prospective_case_id": c["prospective_case_id"],
            "source_case_id": c.get("source_case_id"),
            "domain": c["domain"],
            "proposition": c["proposition"],
            "t0_cutoff": c["t0"]["t0_cutoff"],
            "expected_resolution_window": c["expected_resolution"]["expected_resolution_window"],
            "status": status,
            "resolutions": case_resolutions,
        })
    return {"cases": cases}


def _collect_all_timestamps(raw: Dict[str, Any]) -> List[str]:
    ts = []
    ts += [a.get("first_seen") for a in raw["anomalies"] if a.get("first_seen")]
    ts += [o.get("published_at") for o in raw["observations"] if o.get("published_at")]
    ts += [c.get("created_at") for c in raw["candidates"] if c.get("created_at")]
    ts += [c.get("updated_at") for c in raw["candidates"] if c.get("updated_at")]
    ts += [e.get("recorded_at") for e in raw["candidate_events"] if e.get("recorded_at")]
    ts += [a.get("recorded_at") for a in raw["case_artifacts"] if a.get("recorded_at")]
    ts += [a.get("created_at") for a in raw["blind_analyses"] if a.get("created_at")]
    ts += [f.get("created_at") for f in raw["falsifications"] if f.get("created_at")]
    ts += [j.get("created_at") for j in raw["judgments"] if j.get("created_at")]
    ts += [c.get("created_at") for c in raw["pgt_cases"] if c.get("created_at")]
    ts += [r.get("created_at") for r in raw["pgt_resolutions"] if r.get("created_at")]
    return sorted(ts)


def compute_activity(raw: Dict[str, Any], limit: int = 40) -> List[Dict[str, Any]]:
    """A real event log built only from records that already carry their
    own timestamp - sorted newest-first, capped at `limit`. Every entry
    traces to one real ledger record; nothing here is synthesized."""
    events: List[Dict[str, Any]] = []

    for e in raw["candidate_events"]:
        if e.get("recorded_at"):
            events.append({"timestamp": e["recorded_at"], "kind": e.get("event_type", "candidate_event"),
                            "summary": e.get("reason") or e.get("event_type", ""), "ref_id": e.get("candidate_id")})
    for a in raw["case_artifacts"]:
        if a.get("recorded_at"):
            events.append({"timestamp": a["recorded_at"], "kind": "case_identity_wrapped",
                            "summary": f"{a.get('kind')} wrapped for {', '.join(a.get('derived_from', []))}",
                            "ref_id": a.get("artifact_id")})
    for a in raw["blind_analyses"]:
        if a.get("created_at"):
            events.append({"timestamp": a["created_at"], "kind": "blind_analysis",
                            "summary": f"{a.get('provider')} independent analysis (run {a.get('run_id')})",
                            "ref_id": a.get("artifact_id")})
    for f in raw["falsifications"]:
        if f.get("created_at"):
            events.append({"timestamp": f["created_at"], "kind": "falsification",
                            "summary": f"{f.get('critic_provider')} falsifier critiqued {f.get('target_artifact_id')}",
                            "ref_id": f.get("artifact_id")})
    for j in raw["judgments"]:
        if j.get("created_at"):
            events.append({"timestamp": j["created_at"], "kind": "judgment",
                            "summary": f"deterministic judgment: {j.get('status')}", "ref_id": j.get("judgment_id")})
    for c in raw["pgt_cases"]:
        if c.get("created_at"):
            events.append({"timestamp": c["created_at"], "kind": "prospective_case_registered",
                            "summary": c.get("proposition", "")[:120], "ref_id": c.get("prospective_case_id")})
    for r in raw["pgt_resolutions"]:
        if r.get("created_at"):
            events.append({"timestamp": r["created_at"], "kind": "prospective_case_resolved",
                            "summary": f"resolved {r.get('outcome')}", "ref_id": r.get("resolution_id")})

    events.sort(key=lambda e: e["timestamp"], reverse=True)
    return events[:limit]


def build_snapshot() -> Dict[str, Any]:
    raw = load_all()
    return {
        "machine_status": compute_machine_status(raw),
        "opportunities": compute_opportunities(raw),
        "pipeline": compute_pipeline(raw),
        "pipeline_records": compute_pipeline_records(raw),
        "ground_truth": compute_ground_truth(raw),
        "activity": compute_activity(raw),
    }
