"""Mode B orchestration: Constraint Archaeology evidence -> URL-connected
anomaly groups -> eight-field rearchitecture assessment -> lifecycle
decision -> registry events, written into the SAME registry Mode A uses
(data/candidate_events.jsonl / data/candidates.json), tagged
candidate_type=OLD_BUSINESS_REARCHITECTURE.

Grouping is deliberately simpler than Mode A's buyer/function signature
gate: two anomalies are grouped into one Mode B candidate only when they
share an observation URL (the same article/thread, split by Constraint
Archaeology's own mechanism-based clustering into more than one anomaly -
see README's Mode B section for a real example: the solar-curtailment
story was split into ANOM-0067 and ANOM-0101 by the same-mechanism gate,
but is one narrative for rearchitecture purposes). Mode B does not attempt
Mode A's cross-anomaly "same underlying opportunity" merge - a historical-
constraint claim is grounded in one narrative source, not a pattern that
recurs worded differently across independent sources, so that dedup
concern does not apply the same way here.

Candidate identity persistence follows the same overlap-tracking approach
as Mode A's analyst.py (anomaly_id -> existing candidate_id, followed
through merges), scoped to only this mode's own OLD_BUSINESS_REARCHITECTURE
candidates so it can never collide with Mode A's tracking of the same
anomaly_id - the same anomaly can legitimately seed both a NEW_MARKET and
an OLD_BUSINESS_REARCHITECTURE candidate; they are different candidates.
"""

from __future__ import annotations

import datetime as dt
import json
from collections import defaultdict
from typing import Any, Dict, List, Optional

from ..evidence_reader import load_ca_evidence
from ..models import CandidateEvent, OLD_BUSINESS_REARCHITECTURE
from ..registry import CandidateRegistry, make_event_id, persist_snapshot, rebuild_snapshot
from .dimensions import assess_all, evidence_gaps
from .lifecycle import decide_state, meets_watch_bar


def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _dims_key(fields: Dict[str, Any]) -> Dict[str, Any]:
    out = {}
    for name, v in fields.items():
        d = v.to_dict() if hasattr(v, "to_dict") else v
        out[name] = {"status": d.get("status"), "value": json.dumps(d.get("value"), sort_keys=True, default=str)}
    return out


def _field_dicts(fields: Dict[str, Any]) -> Dict[str, Any]:
    return {name: (v.to_dict() if hasattr(v, "to_dict") else v) for name, v in fields.items()}


def _build_groups(anomalies: List[Dict[str, Any]], obs_by_id: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Union-find on shared observation URLs. See module docstring for why
    this is intentionally simpler than Mode A's signature gate."""
    parent: Dict[str, str] = {}

    def find(x: str) -> str:
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    anomaly_obs: Dict[str, List[Dict[str, Any]]] = {}
    url_to_anomaly: Dict[str, str] = {}
    for a in sorted(anomalies, key=lambda x: x["anomaly_id"]):
        aid = a["anomaly_id"]
        obs = [obs_by_id[oid] for oid in a.get("observation_ids", []) if oid in obs_by_id]
        if not obs:
            continue
        anomaly_obs[aid] = obs
        find(aid)
        for o in obs:
            url = o.get("url")
            if not url:
                continue
            if url in url_to_anomaly:
                union(aid, url_to_anomaly[url])
            else:
                url_to_anomaly[url] = aid

    groups: Dict[str, Dict[str, Any]] = defaultdict(lambda: {"anomaly_ids": set(), "observation_ids": set()})
    for aid, obs in anomaly_obs.items():
        root = find(aid)
        groups[root]["anomaly_ids"].add(aid)
        groups[root]["observation_ids"].update(o["observation_id"] for o in obs)
    return list(groups.values())


def run_analysis(ca_data_dir: str, bca_data_dir: str, config: Dict[str, Any],
                  now: Optional[str] = None) -> Dict[str, Any]:
    now = now or utc_now_iso()

    evidence = load_ca_evidence(ca_data_dir)
    obs_by_id = evidence.observations_by_id()
    evals_by_anomaly = evidence.evaluations_by_anomaly_id()

    events_path = f"{bca_data_dir}/candidate_events.jsonl"
    snapshot_path = f"{bca_data_dir}/candidates.json"

    registry = CandidateRegistry(events_path)
    all_prior_candidates = rebuild_snapshot(registry.all_events())
    all_prior_by_id = {c.candidate_id: c for c in all_prior_candidates}
    mode_b_prior = [c for c in all_prior_candidates if c.candidate_type == OLD_BUSINESS_REARCHITECTURE]
    mode_b_prior_by_id = {c.candidate_id: c for c in mode_b_prior}

    anomaly_to_candidate: Dict[str, str] = {}
    for c in mode_b_prior:
        target, seen = c.candidate_id, set()
        while mode_b_prior_by_id.get(target) and mode_b_prior_by_id[target].merged_into and target not in seen:
            seen.add(target)
            target = mode_b_prior_by_id[target].merged_into
        for aid in c.anomaly_ids:
            anomaly_to_candidate[aid] = target

    groups = _build_groups(evidence.anomalies, obs_by_id)

    events_to_append: List[CandidateEvent] = []
    absorbed_this_run: set = set()
    next_seq = len(all_prior_by_id) + 1
    group_reports: List[Dict[str, Any]] = []

    def new_candidate_id() -> str:
        nonlocal next_seq
        cid = f"BC-{next_seq:04d}"
        next_seq += 1
        return cid

    for g in groups:
        obs = [obs_by_id[oid] for oid in sorted(g["observation_ids"]) if oid in obs_by_id]
        fields = assess_all(obs, config)
        field_dicts = _field_dicts(fields)
        distinct_sources = len({o.get("source", "") for o in obs})
        ca_evals = [evals_by_anomaly[aid] for aid in sorted(g["anomaly_ids"]) if aid in evals_by_anomaly]
        decision = decide_state(fields, obs, distinct_sources, ca_evals, config)
        gaps = evidence_gaps(fields)

        existing_ids = sorted({anomaly_to_candidate[aid] for aid in g["anomaly_ids"] if aid in anomaly_to_candidate})

        if not existing_ids:
            watch_ok, watch_missing = meets_watch_bar(fields)
            if not watch_ok and decision["state"] != "REJECTED":
                group_reports.append({"candidate_id": None, "kind": "not_yet_watch", "state": None,
                                       "anomaly_ids": sorted(g["anomaly_ids"]), "watch_missing": watch_missing,
                                       "fields": field_dicts, "gaps": gaps, "audit": {}})
                continue
            cid = new_candidate_id()
            derived_from = sorted(g["anomaly_ids"] | g["observation_ids"])
            ev = CandidateEvent(
                event_id=make_event_id("candidate_created", cid, {"anomaly_ids": sorted(g["anomaly_ids"])}),
                event_type="candidate_created", candidate_id=cid, recorded_at=now,
                reason=f"created at {decision['state']}: {decision['reason']}",
                derived_from=derived_from,
                payload={
                    "state": decision["state"], "candidate_type": OLD_BUSINESS_REARCHITECTURE,
                    "anomaly_ids": sorted(g["anomaly_ids"]), "observation_ids": sorted(g["observation_ids"]),
                    "rearchitecture": field_dicts,
                },
                analyst_version=config["analyst_version"],
            )
            events_to_append.append(ev)
            group_reports.append({"candidate_id": cid, "kind": "created", "state": decision["state"],
                                   "anomaly_ids": sorted(g["anomaly_ids"]), "fields": field_dicts, "gaps": gaps,
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
                reason=f"evidence now bridges {other} and {canonical} via a shared source URL",
                derived_from=sorted(g["anomaly_ids"]),
                payload={"merged_into": canonical},
                analyst_version=config["analyst_version"],
            )
            events_to_append.append(merge_ev)
            absorbed_this_run.add(other)
            group_reports.append({"candidate_id": other, "kind": "merged", "merged_into": canonical,
                                   "anomaly_ids": sorted(g["anomaly_ids"]), "fields": {}, "gaps": [], "audit": {}})

        prior = mode_b_prior_by_id.get(canonical)
        prior_state = prior.state if prior else "WATCH"
        state_changed = decision["state"] != prior_state
        fields_changed = prior is None or _dims_key(prior.rearchitecture or {}) != _dims_key(field_dicts)
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
                    "rearchitecture": field_dicts, "merged_from": others,
                },
                analyst_version=config["analyst_version"],
            )
            events_to_append.append(ev)
            group_reports.append({"candidate_id": canonical, "kind": "state_changed", "from_state": prior_state,
                                   "state": decision["state"], "anomaly_ids": sorted(g["anomaly_ids"]),
                                   "fields": field_dicts, "gaps": gaps, "audit": decision["audit"]})
        elif fields_changed or membership_changed or others:
            ev = CandidateEvent(
                event_id=make_event_id("evidence_reassessed", canonical,
                                        {"observation_ids": sorted(g["observation_ids"]), "fields": _dims_key(field_dicts)}),
                event_type="evidence_reassessed", candidate_id=canonical, recorded_at=now,
                reason=f"re-assessed with current evidence; state remains {decision['state']}: {decision['reason']}",
                derived_from=sorted(g["anomaly_ids"] | g["observation_ids"]),
                payload={
                    "anomaly_ids": sorted(g["anomaly_ids"]), "observation_ids": sorted(g["observation_ids"]),
                    "rearchitecture": field_dicts, "merged_from": others,
                },
                analyst_version=config["analyst_version"],
            )
            events_to_append.append(ev)
            group_reports.append({"candidate_id": canonical, "kind": "evidence_reassessed", "state": decision["state"],
                                   "anomaly_ids": sorted(g["anomaly_ids"]), "fields": field_dicts, "gaps": gaps,
                                   "audit": decision["audit"]})
        else:
            group_reports.append({"candidate_id": canonical, "kind": "unchanged", "state": decision["state"],
                                   "anomaly_ids": sorted(g["anomaly_ids"]), "fields": field_dicts, "gaps": gaps,
                                   "audit": decision["audit"]})

    appended = registry.append_many(events_to_append)
    all_events = registry.all_events()
    all_candidates = rebuild_snapshot(all_events)
    persist_snapshot(snapshot_path, all_candidates)
    mode_b_candidates = [c for c in all_candidates if c.candidate_type == OLD_BUSINESS_REARCHITECTURE]

    return {
        "now": now,
        "config": config,
        "anomalies_considered": len(evidence.anomalies),
        "groups_formed": len(groups),
        "events_appended": appended,
        "group_reports": group_reports,
        "candidates": mode_b_candidates,
        "snapshot_path": snapshot_path,
        "events_path": events_path,
    }
