"""Evidence-driven lifecycle state machine: WATCH -> VALIDATING ->
INVESTIGATE -> PROMISING, plus REJECTED.

Deliberately NOT a ratchet. State is recomputed from the current evidence
on every run by walking the ladder from WATCH upward and stopping at the
first unmet rung - so a candidate can rise (strengthened) or fall
(weakened) as new observations arrive or as Constraint Archaeology's own
anomaly membership changes, and both directions are equally legitimate,
auditable outcomes. What must never happen (and does not, by construction
here) is silently losing the record of why an earlier run reached a higher
state - that record lives in the append-only event log built by
registry.py, never in this module.

Every requirement below cites a specific dimension result or distinct-
source count - never "the model liked this pattern". `potential_product_
function` never appears as a requirement anywhere in this file.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from .models import EVIDENCED

STATE_LADDER = ("WATCH", "VALIDATING", "INVESTIGATE", "PROMISING")


def meets_watch_bar(dimensions: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """The entry bar for even proposing a candidate: we can name who hurts
    (identifiable_buyer), what they do instead (current_workaround), and
    why that fails (why_solutions_fail) - all three already extracted
    upstream, nothing invented here."""
    required = ["identifiable_buyer", "current_workaround", "why_solutions_fail"]
    missing = [r for r in required if dimensions[r].status != EVIDENCED]
    return (not missing, missing)


def _validating_requirements(dimensions: Dict[str, Any], distinct_sources: int,
                              thresholds: Dict[str, Any]) -> Dict[str, Any]:
    satisfied, missing = [], []
    need = thresholds["min_sources_validating"]
    label = f"distinct_sources>={need}"
    (satisfied if distinct_sources >= need else missing).append(f"{label} (have {distinct_sources})")
    label = "economic_consequence EVIDENCED"
    (satisfied if dimensions["economic_consequence"].status == EVIDENCED else missing).append(label)
    return {"met": not missing, "satisfied": satisfied, "missing": missing}


def _investigate_requirements(dimensions: Dict[str, Any], distinct_sources: int,
                               thresholds: Dict[str, Any]) -> Dict[str, Any]:
    satisfied, missing = [], []
    need = thresholds["min_sources_investigate"]
    label = f"distinct_sources>={need}"
    (satisfied if distinct_sources >= need else missing).append(f"{label} (have {distinct_sources})")
    label = "willingness_to_pay EVIDENCED"
    (satisfied if dimensions["willingness_to_pay"].status == EVIDENCED else missing).append(label)
    label = "contradictory_evidence == none_observed"
    ok = dimensions["contradictory_evidence"].value == "none_observed"
    (satisfied if ok else missing).append(label)
    return {"met": not missing, "satisfied": satisfied, "missing": missing}


def _promising_requirements(dimensions: Dict[str, Any]) -> Dict[str, Any]:
    satisfied, missing = [], []
    checks = [
        ("willingness_to_pay EVIDENCED", dimensions["willingness_to_pay"].status == EVIDENCED),
        ("economic_consequence EVIDENCED", dimensions["economic_consequence"].status == EVIDENCED),
        ("scalability EVIDENCED", dimensions["scalability"].status == EVIDENCED),
        ("pain_severity == SEVERE", dimensions["pain_severity"].value == "SEVERE"),
    ]
    for label, ok in checks:
        (satisfied if ok else missing).append(label)
    return {"met": not missing, "satisfied": satisfied, "missing": missing}


def compute_ladder_state(dimensions: Dict[str, Any], distinct_sources: int,
                          thresholds: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    audit: Dict[str, Any] = {}
    watch_ok, watch_missing = meets_watch_bar(dimensions)
    audit["WATCH"] = {"met": watch_ok, "satisfied": [] if not watch_ok else
                       ["identifiable_buyer EVIDENCED", "current_workaround EVIDENCED",
                        "why_solutions_fail EVIDENCED"], "missing": watch_missing}
    if not watch_ok:
        return "WATCH", audit

    state = "WATCH"
    val = _validating_requirements(dimensions, distinct_sources, thresholds)
    audit["VALIDATING"] = val
    if not val["met"]:
        return state, audit
    state = "VALIDATING"

    inv = _investigate_requirements(dimensions, distinct_sources, thresholds)
    audit["INVESTIGATE"] = inv
    if not inv["met"]:
        return state, audit
    state = "INVESTIGATE"

    prom = _promising_requirements(dimensions)
    audit["PROMISING"] = prom
    if not prom["met"]:
        return state, audit
    state = "PROMISING"
    return state, audit


def rejection_trigger(ca_evaluations_for_group: List[Dict[str, Any]]) -> Optional[Tuple[str, List[str]]]:
    """The only REJECTED trigger implemented: every Constraint Archaeology
    anomaly formally evaluated (>=3 independent sources, evaluated under
    the frozen v0.5 method) backing this candidate returned KILL, and at
    least one anomaly has actually been evaluated. Heuristic contradiction
    markers deliberately do NOT auto-reject - they are surfaced in the
    report instead, because a keyword-based contradiction check is too
    weak a signal to justify a rejection on its own."""
    if not ca_evaluations_for_group:
        return None
    kills = [e for e in ca_evaluations_for_group if e.get("action") == "KILL"]
    if len(kills) == len(ca_evaluations_for_group):
        return (
            f"Constraint Archaeology KILLed all {len(kills)} evaluated anomaly(ies) backing this candidate",
            sorted({e["anomaly_id"] for e in kills}),
        )
    return None


def decide_state(dimensions: Dict[str, Any], distinct_sources: int,
                  ca_evaluations_for_group: List[Dict[str, Any]],
                  thresholds: Dict[str, Any]) -> Dict[str, Any]:
    rejected = rejection_trigger(ca_evaluations_for_group)
    if rejected:
        reason, derived_from = rejected
        return {"state": "REJECTED", "reason": reason, "audit": {}, "rejected_derived_from": derived_from}

    state, audit = compute_ladder_state(dimensions, distinct_sources, thresholds)
    idx = STATE_LADDER.index(state)
    if idx == 0:
        reason = "meets the WATCH bar" if audit["WATCH"]["met"] else \
            f"does not meet the WATCH bar: missing {audit['WATCH']['missing']}"
    else:
        reason = f"reached {state}: " + "; ".join(audit[STATE_LADDER[idx]]["satisfied"])
    return {"state": state, "reason": reason, "audit": audit, "rejected_derived_from": []}
