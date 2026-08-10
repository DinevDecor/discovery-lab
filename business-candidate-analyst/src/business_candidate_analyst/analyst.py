"""Orchestration: Constraint Archaeology evidence -> opportunity groups ->
dimension assessment -> lifecycle decision -> registry events.

Candidate identity is stable across runs the same way Constraint
Archaeology's own anomalies are stable across runs: not by re-hashing
current membership (which changes as evidence accumulates), but by
tracking which anomaly_ids a candidate already owns and looking up
overlap on each new run. A brand-new anomaly set with no overlap becomes
a new candidate; overlap with exactly one existing candidate continues
it; overlap with more than one existing candidate means this run's
evidence has bridged two previously-separate candidates, which is
recorded as an explicit `candidates_merged` event, never a silent
overwrite.

The one non-obvious ordering rule: grouping (signature.py's gate) always
runs first, purely from current CA evidence, before any comparison
against registry history - so the gate itself is never biased by what
this tool has decided before. History only decides IDENTITY, never
whether a merge is evidence-warranted.
"""

from __future__ import annotations

import datetime as dt
import json
import os
from typing import Any, Dict, List, Optional

from .config import load_thresholds
from .dimensions import assess_all
from .evidence_reader import load_ca_evidence
from .lifecycle import decide_state, meets_watch_bar
from .models import CandidateEvent, NEW_MARKET
from .registry import CandidateRegistry, make_event_id, persist_snapshot, rebuild_snapshot
from .signature import same_opportunity, signature_for_group

STATE_RANK = {"REJECTED": -1, "WATCH": 0, "VALIDATING": 1, "INVESTIGATE": 2, "PROMISING": 3}


def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _dims_key(dims: Dict[str, Any]) -> Dict[str, Any]:
    out = {}
    for name, v in dims.items():
        d = v.to_dict() if hasattr(v, "to_dict") else v
        out[name] = {"status": d.get("status"), "value": json.dumps(d.get("value"), sort_keys=True, default=str)}
    return out


def _dims_dicts(dims: Dict[str, Any]) -> Dict[str, Any]:
    return {name: (v.to_dict() if hasattr(v, "to_dict") else v) for name, v in dims.items()}


def _build_groups(anomalies: List[Dict[str, Any]], obs_by_id: Dict[str, Any],
                   thresholds: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Greedy grouping in deterministic anomaly_id order - same style as
    ca_agents.memory.rebuild_anomalies's own greedy clustering.

    Deliberately compares each candidate new anomaly against every existing
    group's ANCHOR (the observations of the first anomaly that founded that
    group) rather than the group's full accumulated text. A first version
    compared against the growing pooled text instead, and on the real
    corpus a large group's ever-expanding keyword-hit set made it
    increasingly likely to coincidentally share one generic word (e.g.
    "cost") with a same-bucket but unrelated anomaly (grid curtailment,
    hardware procurement) - a snowball effect, not evidence. Anchoring on
    a single fixed representative bounds that, mirroring
    ca_agents.same_mechanism_gate's own use of the group's first
    observation as its comparison basis. The tradeoff (accepted, same as
    upstream's) is that a genuine A-B-C chain where B bridges A and C but
    A and C alone don't match will not fully merge - that is read as the
    gate correctly refusing a merge it cannot evidence, not a bug."""
    groups: List[Dict[str, Any]] = []
    for a in sorted(anomalies, key=lambda x: x["anomaly_id"]):
        obs = [obs_by_id[oid] for oid in a.get("observation_ids", []) if oid in obs_by_id]
        if not obs:
            continue
        own_sig = signature_for_group(obs, thresholds)
        placed = False
        for g in groups:
            ok, reasons = same_opportunity(g["anchor_signature"], g["anchor_observations"], own_sig, obs, thresholds)
            if ok:
                g["anomaly_ids"].add(a["anomaly_id"])
                g["observation_ids"].update(a.get("observation_ids", []))
                g["merge_reasons"].append({"anomaly_id": a["anomaly_id"], "reasons": reasons})
                combined = [obs_by_id[oid] for oid in sorted(g["observation_ids"]) if oid in obs_by_id]
                g["signature"] = signature_for_group(combined, thresholds)
                placed = True
                break
        if not placed:
            groups.append({
                "anomaly_ids": {a["anomaly_id"]}, "observation_ids": set(a.get("observation_ids", [])),
                "signature": own_sig, "anchor_signature": own_sig, "anchor_observations": obs,
                "merge_reasons": [],
            })
    return groups


def run_analysis(ca_data_dir: str, bca_data_dir: str,
                  thresholds: Optional[Dict[str, Any]] = None,
                  now: Optional[str] = None) -> Dict[str, Any]:
    thresholds = thresholds or load_thresholds()
    now = now or utc_now_iso()

    evidence = load_ca_evidence(ca_data_dir)
    obs_by_id = evidence.observations_by_id()
    evals_by_anomaly = evidence.evaluations_by_anomaly_id()

    events_path = os.path.join(bca_data_dir, "candidate_events.jsonl")
    snapshot_path = os.path.join(bca_data_dir, "candidates.json")

    registry = CandidateRegistry(events_path)
    prior_candidates = rebuild_snapshot(registry.all_events())
    prior_by_id = {c.candidate_id: c for c in prior_candidates}

    anomaly_to_candidate: Dict[str, str] = {}
    for c in prior_candidates:
        target, seen = c.candidate_id, set()
        while prior_by_id.get(target) and prior_by_id[target].merged_into and target not in seen:
            seen.add(target)
            target = prior_by_id[target].merged_into
        for aid in c.anomaly_ids:
            anomaly_to_candidate[aid] = target

    groups = _build_groups(evidence.anomalies, obs_by_id, thresholds)

    events_to_append: List[CandidateEvent] = []
    absorbed_this_run: set = set()
    next_seq = len(prior_by_id) + 1
    group_reports: List[Dict[str, Any]] = []

    def new_candidate_id() -> str:
        nonlocal next_seq
        cid = f"BC-{next_seq:04d}"
        next_seq += 1
        return cid

    for g in groups:
        obs = [obs_by_id[oid] for oid in sorted(g["observation_ids"]) if oid in obs_by_id]
        dims = assess_all(obs, thresholds)
        distinct_sources = dims["evidence_diversity"].value["distinct_sources"]
        ca_evals = [evals_by_anomaly[aid] for aid in sorted(g["anomaly_ids"]) if aid in evals_by_anomaly]
        decision = decide_state(dims, distinct_sources, ca_evals, thresholds)
        dims_dicts = _dims_dicts(dims)

        existing_ids = sorted({anomaly_to_candidate[aid] for aid in g["anomaly_ids"] if aid in anomaly_to_candidate})

        if not existing_ids:
            watch_ok, watch_missing = meets_watch_bar(dims)
            if not watch_ok and decision["state"] != "REJECTED":
                group_reports.append({"candidate_id": None, "kind": "not_yet_watch", "state": None,
                                       "anomaly_ids": sorted(g["anomaly_ids"]), "watch_missing": watch_missing,
                                       "dims": dims_dicts, "audit": {}})
                continue
            cid = new_candidate_id()
            derived_from = sorted(g["anomaly_ids"] | g["observation_ids"])
            ev = CandidateEvent(
                event_id=make_event_id("candidate_created", cid, {"anomaly_ids": sorted(g["anomaly_ids"])}),
                event_type="candidate_created", candidate_id=cid, recorded_at=now,
                reason=f"created at {decision['state']}: {decision['reason']}",
                derived_from=derived_from,
                payload={
                    "state": decision["state"], "candidate_type": NEW_MARKET,
                    "anomaly_ids": sorted(g["anomaly_ids"]),
                    "observation_ids": sorted(g["observation_ids"]), "signature": g["signature"].to_dict(),
                    "dimensions": dims_dicts, "merge_reasons": g["merge_reasons"],
                },
                analyst_version=thresholds["analyst_version"],
            )
            events_to_append.append(ev)
            group_reports.append({"candidate_id": cid, "kind": "created", "state": decision["state"],
                                   "anomaly_ids": sorted(g["anomaly_ids"]), "dims": dims_dicts,
                                   "audit": decision["audit"]})
            continue

        canonical, others = existing_ids[0], existing_ids[1:]
        for other in others:
            if other in absorbed_this_run:
                continue
            merge_ev = CandidateEvent(
                event_id=make_event_id("candidates_merged", other,
                                        {"merged_into": canonical, "anomaly_ids": sorted(g["anomaly_ids"])}),
                event_type="candidates_merged", candidate_id=other, recorded_at=now,
                reason=f"evidence now bridges {other} and {canonical} under the same buyer/function "
                       "signature - see merge_reasons on the canonical candidate's next event",
                derived_from=sorted(g["anomaly_ids"]),
                payload={"merged_into": canonical},
                analyst_version=thresholds["analyst_version"],
            )
            events_to_append.append(merge_ev)
            absorbed_this_run.add(other)
            group_reports.append({"candidate_id": other, "kind": "merged", "merged_into": canonical,
                                   "anomaly_ids": sorted(g["anomaly_ids"]), "dims": {}, "audit": {}})

        prior = prior_by_id.get(canonical)
        prior_state = prior.state if prior else "WATCH"
        state_changed = decision["state"] != prior_state
        dims_changed = prior is None or _dims_key(prior.dimensions) != _dims_key(dims_dicts)
        membership_changed = prior is None or sorted(g["observation_ids"]) != sorted(prior.observation_ids)

        if state_changed:
            ev = CandidateEvent(
                event_id=make_event_id("state_changed", canonical, {
                    "from_state": prior_state, "to_state": decision["state"],
                    "observation_ids": sorted(g["observation_ids"])}),
                event_type="state_changed", candidate_id=canonical, recorded_at=now, reason=decision["reason"],
                derived_from=sorted(g["anomaly_ids"] | g["observation_ids"]),
                payload={
                    "from_state": prior_state, "to_state": decision["state"],
                    "anomaly_ids": sorted(g["anomaly_ids"]), "observation_ids": sorted(g["observation_ids"]),
                    "dimensions": dims_dicts, "merge_reasons": g["merge_reasons"], "merged_from": others,
                },
                analyst_version=thresholds["analyst_version"],
            )
            events_to_append.append(ev)
            group_reports.append({"candidate_id": canonical, "kind": "state_changed", "from_state": prior_state,
                                   "state": decision["state"], "anomaly_ids": sorted(g["anomaly_ids"]),
                                   "dims": dims_dicts, "audit": decision["audit"]})
        elif dims_changed or membership_changed or others:
            ev = CandidateEvent(
                event_id=make_event_id("evidence_reassessed", canonical,
                                        {"observation_ids": sorted(g["observation_ids"]), "dims": _dims_key(dims_dicts)}),
                event_type="evidence_reassessed", candidate_id=canonical, recorded_at=now,
                reason=f"re-assessed with current evidence; state remains {decision['state']}: {decision['reason']}",
                derived_from=sorted(g["anomaly_ids"] | g["observation_ids"]),
                payload={
                    "anomaly_ids": sorted(g["anomaly_ids"]), "observation_ids": sorted(g["observation_ids"]),
                    "dimensions": dims_dicts, "merge_reasons": g["merge_reasons"], "merged_from": others,
                },
                analyst_version=thresholds["analyst_version"],
            )
            events_to_append.append(ev)
            group_reports.append({"candidate_id": canonical, "kind": "evidence_reassessed", "state": decision["state"],
                                   "anomaly_ids": sorted(g["anomaly_ids"]), "dims": dims_dicts,
                                   "audit": decision["audit"]})
        else:
            group_reports.append({"candidate_id": canonical, "kind": "unchanged", "state": decision["state"],
                                   "anomaly_ids": sorted(g["anomaly_ids"]), "dims": dims_dicts,
                                   "audit": decision["audit"]})

    appended = registry.append_many(events_to_append)
    all_events = registry.all_events()
    candidates = rebuild_snapshot(all_events)
    persist_snapshot(snapshot_path, candidates)

    return {
        "now": now,
        "thresholds": thresholds,
        "anomalies_considered": len(evidence.anomalies),
        "groups_formed": len(groups),
        "events_appended": appended,
        "group_reports": group_reports,
        "candidates": candidates,
        "prior_candidates_by_id": prior_by_id,
        "snapshot_path": snapshot_path,
        "events_path": events_path,
    }
