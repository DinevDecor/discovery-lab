"""Orchestration: Constraint Archaeology evidence -> opportunity groups ->
dimension assessment -> lifecycle decision -> registry events.

Candidate identity is stable across runs the same way Constraint
Archaeology's own anomalies are stable across runs: not by re-hashing
current membership (which changes as evidence accumulates), but by
tracking which observation_ids a candidate already owns and looking up
overlap on each new run. A brand-new observation set with no overlap
becomes a new candidate; overlap with exactly one existing candidate
continues it; overlap with more than one existing candidate means this
run's evidence has bridged two previously-separate candidates, which is
recorded as an explicit `candidates_merged` event, never a silent
overwrite.

Identity is keyed on observation_id, not anomaly_id. Constraint
Archaeology's anomaly_id is assigned positionally during its own
non-append-only rebuild of anomalies.json (`ANOM-{len(anomalies)+1:04d}`
in ca_agents.memory.rebuild_anomalies) and is not a stable identifier
across CA runs - the same real observations can land under a different
ANOM-#### label as the corpus grows or CA's clustering reorders. A
reverse lookup keyed on anomaly_id would silently fail to find a
candidate's own evidence after a CA rebuild reshuffles its numbering,
risking a duplicate candidate for evidence this tool has already seen.
observation_id, assigned once by the Sensor Agent and referenced
append-only in observations.jsonl, does not have this problem, so it is
the identity bridge; anomaly_id remains present on candidates purely as
current-snapshot grouping metadata (still useful to correlate against
this run's own CA evaluations, which are loaded from the same snapshot
and so share its numbering for this run only).

The one non-obvious ordering rule: grouping (signature.py's gate) always
runs first, purely from current CA evidence, before any comparison
against registry history - so the gate itself is never biased by what
this tool has decided before. History only decides IDENTITY, never
whether a merge is evidence-warranted.

Identity lookup is scoped to this mode's own NEW_MARKET candidates only,
mirroring rearchitecture/analyst.py's identical scoping to
OLD_BUSINESS_REARCHITECTURE - the same observation_id can legitimately
seed both a NEW_MARKET and an OLD_BUSINESS_REARCHITECTURE candidate (two
different candidates, two different lenses on the same evidence), and
`rebuild_snapshot` returns candidates sorted by candidate_id, so an
unscoped lookup would silently resolve a shared observation_id to
whichever mode happens to hold the higher candidate_id - overwriting the
other mode's candidate with this mode's dimensions/lifecycle logic and
losing track of its own. That bug shipped and was caught on the real
corpus (see git history); this scoping is the fix, preserved here.

A candidate is reassessed AT MOST ONCE per run, from its full unioned
evidence for this run - never once per fresh group that happens to touch
it. `_build_groups` deliberately compares each anomaly only against a
group's fixed anchor (see its own docstring), so a candidate that
accumulated anomaly_ids across several past `candidates_merged` events can
easily fragment back into two or more disjoint fresh groups this run (the
anchor of one no longer matches the anchor of the other, even though both
still resolve to the same registered candidate). Processing each such
fresh group independently - the original design - reassessed the
candidate from whichever PARTIAL slice of its evidence one group
happened to carry, repeatedly, sometimes with contradictory conclusions
in the same run, and was never a true fixed point: re-running against
unchanged evidence kept re-fragmenting and re-emitting events for several
runs before stabilizing. The fix is a resolve-then-union step between
grouping and processing: every fresh group is first resolved to the
candidate_id(s) it touches, groups that resolve to overlapping candidate
identities (directly or transitively, through a chain of shared ids) are
merged into one cluster, and each cluster is processed exactly once from
the union of its anomaly_ids/observation_ids - so `RUN(state, corpus)`
is now a true fixed point of itself.
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


def _resolve_and_union_groups(groups: List[Dict[str, Any]],
                               observation_to_candidate: Dict[str, str]) -> List[Dict[str, Any]]:
    """Resolves every fresh group to the candidate_id(s) it touches, then
    unions any groups that resolve to overlapping candidate identities
    (directly or transitively) into one combined group, so a candidate
    that fragments into several disjoint fresh groups this run is still
    reassessed exactly once, from the union of all of them. Groups that
    resolve to no existing candidate at all (brand-new evidence) are
    returned unchanged, one per group, since `_build_groups` has already
    decided they are not the same opportunity as each other.

    Resolution is keyed on observation_id, not anomaly_id (see module
    docstring): CA's anomaly_id is reassigned positionally on every CA
    rebuild, so looking a fresh group's own anomaly_ids up in a map built
    from a candidate's PAST anomaly_ids can silently miss a match after CA
    renumbers - observation_id doesn't move."""
    resolved = [{"group": g, "existing_ids": sorted({observation_to_candidate[oid] for oid in g["observation_ids"]
                                                       if oid in observation_to_candidate})}
                for g in groups]

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
            # Deterministic root: the numerically/lexically lower candidate_id
            # wins, matching the existing "canonical = lowest sorted id" rule.
            if ra < rb:
                parent[rb] = ra
            else:
                parent[ra] = rb

    for r in resolved:
        for other in r["existing_ids"][1:]:
            union(r["existing_ids"][0], other)

    clusters: Dict[str, Dict[str, Any]] = {}
    unresolved: List[Dict[str, Any]] = []
    for r in resolved:
        if not r["existing_ids"]:
            unresolved.append(r["group"])
            continue
        root = find(r["existing_ids"][0])
        g = r["group"]
        if root not in clusters:
            clusters[root] = {
                "anomaly_ids": set(g["anomaly_ids"]), "observation_ids": set(g["observation_ids"]),
                "merge_reasons": list(g["merge_reasons"]), "existing_ids": set(r["existing_ids"]),
            }
        else:
            c = clusters[root]
            c["anomaly_ids"] |= g["anomaly_ids"]
            c["observation_ids"] |= g["observation_ids"]
            c["merge_reasons"].extend(g["merge_reasons"])
            c["existing_ids"] |= set(r["existing_ids"])

    unioned = [{"anomaly_ids": c["anomaly_ids"], "observation_ids": c["observation_ids"],
                "merge_reasons": c["merge_reasons"], "existing_ids": sorted(c["existing_ids"])}
               for c in clusters.values()]
    for g in unresolved:
        unioned.append({"anomaly_ids": g["anomaly_ids"], "observation_ids": g["observation_ids"],
                         "merge_reasons": g["merge_reasons"], "existing_ids": []})
    return unioned


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
    mode_a_prior = [c for c in prior_candidates if c.candidate_type == NEW_MARKET]
    mode_a_prior_by_id = {c.candidate_id: c for c in mode_a_prior}

    observation_to_candidate: Dict[str, str] = {}
    for c in mode_a_prior:
        target, seen = c.candidate_id, set()
        while mode_a_prior_by_id.get(target) and mode_a_prior_by_id[target].merged_into and target not in seen:
            seen.add(target)
            target = mode_a_prior_by_id[target].merged_into
        for oid in c.observation_ids:
            observation_to_candidate[oid] = target

    groups = _build_groups(evidence.anomalies, obs_by_id, thresholds)
    unioned_groups = _resolve_and_union_groups(groups, observation_to_candidate)

    events_to_append: List[CandidateEvent] = []
    absorbed_this_run: set = set()
    next_seq = len(prior_by_id) + 1
    group_reports: List[Dict[str, Any]] = []

    def new_candidate_id() -> str:
        nonlocal next_seq
        cid = f"BC-{next_seq:04d}"
        next_seq += 1
        return cid

    for g in unioned_groups:
        obs = [obs_by_id[oid] for oid in sorted(g["observation_ids"]) if oid in obs_by_id]
        dims = assess_all(obs, thresholds)
        distinct_sources = dims["evidence_diversity"].value["distinct_sources"]
        ca_evals = [evals_by_anomaly[aid] for aid in sorted(g["anomaly_ids"]) if aid in evals_by_anomaly]
        decision = decide_state(dims, distinct_sources, ca_evals, thresholds)
        dims_dicts = _dims_dicts(dims)

        existing_ids = g["existing_ids"]

        if not existing_ids:
            watch_ok, watch_missing = meets_watch_bar(dims)
            if not watch_ok and decision["state"] != "REJECTED":
                group_reports.append({"candidate_id": None, "kind": "not_yet_watch", "state": None,
                                       "anomaly_ids": sorted(g["anomaly_ids"]), "watch_missing": watch_missing,
                                       "dims": dims_dicts, "audit": {}})
                continue
            cid = new_candidate_id()
            derived_from = sorted(g["anomaly_ids"] | g["observation_ids"])
            group_signature = signature_for_group(obs, thresholds)
            ev = CandidateEvent(
                event_id=make_event_id("candidate_created", cid, {"anomaly_ids": sorted(g["anomaly_ids"])}),
                event_type="candidate_created", candidate_id=cid, recorded_at=now,
                reason=f"created at {decision['state']}: {decision['reason']}",
                derived_from=derived_from,
                payload={
                    "state": decision["state"], "candidate_type": NEW_MARKET,
                    "anomaly_ids": sorted(g["anomaly_ids"]),
                    "observation_ids": sorted(g["observation_ids"]), "signature": group_signature.to_dict(),
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

        prior = mode_a_prior_by_id.get(canonical)
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
    all_candidates = rebuild_snapshot(all_events)
    persist_snapshot(snapshot_path, all_candidates)
    mode_a_candidates = [c for c in all_candidates if c.candidate_type == NEW_MARKET]

    return {
        "now": now,
        "thresholds": thresholds,
        "anomalies_considered": len(evidence.anomalies),
        "groups_formed": len(groups),
        "events_appended": appended,
        "group_reports": group_reports,
        "candidates": mode_a_candidates,
        "prior_candidates_by_id": prior_by_id,
        "snapshot_path": snapshot_path,
        "events_path": events_path,
    }
