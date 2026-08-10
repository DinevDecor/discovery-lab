"""Mode B lifecycle: WATCH -> VALIDATING -> INVESTIGATE -> PROMISING, plus
REJECTED - same five states as Mode A (models.STATES), reused rather than
inventing a parallel enum, but with Mode B's own, much stricter
requirements at every rung, because the evidence this mode reasons about
(a historical causal claim) is inherently harder to confirm than Mode A's
(a present-tense reported pain).

The no-AI-bias rule lives here, not in dimensions.py, because it is a
LIFECYCLE decision, not an evidence-quality one: `why_now` can legitimately
be OBSERVED with "ai" as the only enabler found in the text - that is an
honest reading of the evidence. What must not happen is treating that
alone as sufficient to advance past WATCH. See
_validating_requirements/_investigate_requirements below - both refuse to
advance when the only enabler identified is "ai", regardless of how strong
every other field is.

REJECTED reuses ..lifecycle.rejection_trigger verbatim - a CA `KILL`
evaluation is exactly as disqualifying for a Mode B candidate as for a
Mode A one, and that function has no Mode A-specific shape to it.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from ..lifecycle import rejection_trigger
from ..models import INFERRED, INSUFFICIENT_DATA, OBSERVED
from .taxonomy import enabler_hits, group_text_for_change, is_ai_only

STATE_LADDER = ("WATCH", "VALIDATING", "INVESTIGATE", "PROMISING")


def meets_watch_bar(fields: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """The entry bar: some structural-pattern hypothesis exists
    (historical_constraint is at least INFERRED) and the legacy structure
    itself is OBSERVED (current_carrier is non-empty) - both already
    grounded in extracted fields, nothing invented here."""
    missing = []
    if fields["historical_constraint"].status == INSUFFICIENT_DATA:
        missing.append("historical_constraint OBSERVED-or-INFERRED")
    if fields["legacy_structure"].status != OBSERVED:
        missing.append("legacy_structure OBSERVED")
    return (not missing, missing)


def _enablers_for(observations: List[Dict[str, Any]], config: Dict[str, Any]) -> Dict[str, Any]:
    return enabler_hits(group_text_for_change(observations), config)


def _validating_requirements(fields: Dict[str, Any], observations: List[Dict[str, Any]],
                              config: Dict[str, Any]) -> Dict[str, Any]:
    satisfied, missing = [], []
    if fields["historical_constraint"].status == OBSERVED:
        satisfied.append("historical_constraint OBSERVED")
    else:
        missing.append("historical_constraint OBSERVED (currently INFERRED or INSUFFICIENT_DATA)")

    if fields["evidence_constraint_weakened"].status in (OBSERVED, INFERRED):
        satisfied.append("evidence_constraint_weakened OBSERVED-or-INFERRED")
    else:
        missing.append("evidence_constraint_weakened OBSERVED-or-INFERRED (currently INSUFFICIENT_DATA)")

    enablers = _enablers_for(observations, config)
    if enablers and not is_ai_only(enablers):
        satisfied.append("at least one non-AI enabler identified")
    elif is_ai_only(enablers):
        missing.append("no-AI-bias rule: the only enabler found is 'ai' - AI-only evidence can never by itself "
                        "justify advancing past WATCH")
    else:
        missing.append("no enabler (technological, economic, legal, social, or infrastructural) identified")
    return {"met": not missing, "satisfied": satisfied, "missing": missing}


def _investigate_requirements(fields: Dict[str, Any], observations: List[Dict[str, Any]],
                               config: Dict[str, Any]) -> Dict[str, Any]:
    satisfied, missing = [], []
    checks = [
        ("evidence_constraint_weakened OBSERVED (not just INFERRED)",
         fields["evidence_constraint_weakened"].status == OBSERVED),
        ("why_now OBSERVED", fields["why_now"].status == OBSERVED),
        ("potential_economic_effect OBSERVED", fields["potential_economic_effect"].status == OBSERVED),
    ]
    for label, ok in checks:
        (satisfied if ok else missing).append(label)

    enablers = _enablers_for(observations, config)
    if enablers and not is_ai_only(enablers):
        satisfied.append("at least one non-AI enabler identified")
    else:
        missing.append("no-AI-bias rule: need at least one non-AI enabler")
    return {"met": not missing, "satisfied": satisfied, "missing": missing}


def _promising_requirements(fields: Dict[str, Any], distinct_sources: int) -> Dict[str, Any]:
    satisfied, missing = [], []
    chain = ("historical_constraint", "evidence_constraint_existed", "evidence_constraint_weakened",
             "why_now", "potential_economic_effect")
    all_observed = all(fields[k].status == OBSERVED for k in chain)
    label = "entire evidence chain OBSERVED (none merely INFERRED)"
    (satisfied if all_observed else missing).append(label)
    label = f"distinct_sources>=2 (have {distinct_sources})"
    (satisfied if distinct_sources >= 2 else missing).append(label)
    return {"met": not missing, "satisfied": satisfied, "missing": missing}


def compute_ladder_state(fields: Dict[str, Any], observations: List[Dict[str, Any]], distinct_sources: int,
                          config: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    audit: Dict[str, Any] = {}
    watch_ok, watch_missing = meets_watch_bar(fields)
    audit["WATCH"] = {"met": watch_ok,
                       "satisfied": [] if not watch_ok else ["historical_constraint OBSERVED-or-INFERRED",
                                                              "legacy_structure OBSERVED"],
                       "missing": watch_missing}
    if not watch_ok:
        return "WATCH", audit

    state = "WATCH"
    val = _validating_requirements(fields, observations, config)
    audit["VALIDATING"] = val
    if not val["met"]:
        return state, audit
    state = "VALIDATING"

    inv = _investigate_requirements(fields, observations, config)
    audit["INVESTIGATE"] = inv
    if not inv["met"]:
        return state, audit
    state = "INVESTIGATE"

    prom = _promising_requirements(fields, distinct_sources)
    audit["PROMISING"] = prom
    if not prom["met"]:
        return state, audit
    state = "PROMISING"
    return state, audit


def decide_state(fields: Dict[str, Any], observations: List[Dict[str, Any]], distinct_sources: int,
                  ca_evaluations_for_group: List[Dict[str, Any]], config: Dict[str, Any]) -> Dict[str, Any]:
    rejected = rejection_trigger(ca_evaluations_for_group)
    if rejected:
        reason, derived_from = rejected
        return {"state": "REJECTED", "reason": reason, "audit": {}, "rejected_derived_from": derived_from}

    state, audit = compute_ladder_state(fields, observations, distinct_sources, config)
    idx = STATE_LADDER.index(state)
    if idx == 0:
        reason = "meets the WATCH bar" if audit["WATCH"]["met"] else \
            f"does not meet the WATCH bar: missing {audit['WATCH']['missing']}"
    else:
        reason = f"reached {state}: " + "; ".join(audit[STATE_LADDER[idx]]["satisfied"])
    return {"state": state, "reason": reason, "audit": audit, "rejected_derived_from": []}
