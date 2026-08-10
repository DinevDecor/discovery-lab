"""Mode B's eight-item checklist, each answered as a RearchitectureField
with status OBSERVED / INFERRED / INSUFFICIENT_DATA - never invented past
what the text and the deterministic taxonomy in taxonomy.py support.

Two dimensions deserve explicit attention because they are the ones most
at risk of a false positive:

  - `evidence_constraint_weakened` must NOT fire just because the text
    mentions the old constraint - see taxonomy.py's still_binding_markers.
    A text arguing the constraint is STILL binding (e.g. "the batteries
    everyone suggests aren't free") is exactly as informative as one
    arguing it has weakened, and reporting it as INSUFFICIENT_DATA with an
    explicit note is the honest outcome, not a failure of the heuristic.
  - `proposed_rearchitecture` is FRAMING ONLY, exactly like Mode A's
    potential_product_function - a templated hypothesis built from the
    other fields, never itself evidence, and lifecycle.py never gates a
    transition on it.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ..models import INFERRED, INSUFFICIENT_DATA, OBSERVED, RearchitectureField
from .taxonomy import (
    best_constraint_category, economic_effect_hits, enabler_hits, group_text_for_change,
    group_text_for_constraint, legacy_structure_text, still_binding_hits, weakening_hits,
    UNCLASSIFIED_CONSTRAINT,
)

_HUMAN_LABEL = {
    "buffer_inventory": "a buffer/inventory/storage margin held against unreliable supply",
    "payment_or_market_access": "a workaround revenue model held against absent payment access",
    "intermediation_trust": "an intermediary held against expensive trust/verification",
    "physical_presence": "a physical-presence requirement held against remote identity/signature verification",
    "continuous_oversight": "manual monitoring held against a lack of continuous/remote observability",
    "vertical_integration": "in-house/vertically integrated operations held against missing external standards",
    "capacity_lead_time": "production capacity and lead time held against volatile demand",
    "manual_dispute_resolution": "manual verification/reconciliation held against unavailable automated records",
}


def _obs_ids(observations: List[Dict[str, Any]]) -> List[str]:
    return [o.get("observation_id", "") for o in observations]


def existing_business_or_jtbd(observations: List[Dict[str, Any]]) -> RearchitectureField:
    phrasings = sorted({o.get("process", "") for o in observations if (o.get("process") or "").strip()})
    if not phrasings:
        return RearchitectureField("existing_business_or_jtbd", INSUFFICIENT_DATA, None, [],
                                    "no process text in any grouped observation")
    return RearchitectureField("existing_business_or_jtbd", OBSERVED, phrasings, _obs_ids(observations),
                                "verbatim `process` extracted upstream by the Sensor Agent")


def historical_constraint(observations: List[Dict[str, Any]], config: Dict[str, Any]) -> RearchitectureField:
    text = group_text_for_constraint(observations)
    category, legacy_hits, reason_hits = best_constraint_category(text, config)
    if category == UNCLASSIFIED_CONSTRAINT:
        return RearchitectureField("historical_constraint", INSUFFICIENT_DATA, None, [],
                                    "no structural-pattern keyword matched any constraint_taxonomy bucket")
    status = OBSERVED if reason_hits else INFERRED
    note = ("legacy structure and an explicit reason for it both found in text" if reason_hits else
            "legacy structure pattern matched, but no explicit causal language found - a hypothesis, not a "
            "confirmed historical fact")
    return RearchitectureField("historical_constraint", status, category, _obs_ids(observations), note)


def evidence_constraint_existed(observations: List[Dict[str, Any]], config: Dict[str, Any]) -> RearchitectureField:
    text = group_text_for_constraint(observations)
    category, legacy_hits, reason_hits = best_constraint_category(text, config)
    if category == UNCLASSIFIED_CONSTRAINT:
        return RearchitectureField("evidence_constraint_existed", INSUFFICIENT_DATA, None, [],
                                    "no constraint category identified to find evidence for")
    if reason_hits:
        return RearchitectureField("evidence_constraint_existed", OBSERVED, sorted(reason_hits),
                                    _obs_ids(observations),
                                    "explicit reasoning language found connecting the legacy structure to a cause")
    return RearchitectureField("evidence_constraint_existed", INFERRED, sorted(legacy_hits), _obs_ids(observations),
                                "only the legacy structure itself was found, not an explicit stated reason for it")


def evidence_constraint_weakened(observations: List[Dict[str, Any]], config: Dict[str, Any]) -> RearchitectureField:
    text = group_text_for_change(observations)
    weak = weakening_hits(text, config)
    still = still_binding_hits(text, config)
    enablers = enabler_hits(text, config)
    if weak and enablers:
        return RearchitectureField("evidence_constraint_weakened", OBSERVED,
                                    {"weakening_language": sorted(weak), "enablers": sorted(enablers)},
                                    _obs_ids(observations),
                                    "explicit change language co-occurs with a named enabler")
    if weak:
        return RearchitectureField("evidence_constraint_weakened", INFERRED, {"weakening_language": sorted(weak)},
                                    _obs_ids(observations),
                                    "change language found but no specific enabler could be identified")
    if still:
        return RearchitectureField("evidence_constraint_weakened", INSUFFICIENT_DATA,
                                    {"still_binding_language": sorted(still)}, _obs_ids(observations),
                                    "text argues the constraint is STILL binding, not weakened - this is not a "
                                    "gap to fill, it is evidence against the candidate")
    return RearchitectureField("evidence_constraint_weakened", INSUFFICIENT_DATA, None, [],
                                "no weakening language found in the grouped evidence")


def legacy_structure(observations: List[Dict[str, Any]]) -> RearchitectureField:
    structures = legacy_structure_text(observations)
    if not structures:
        return RearchitectureField("legacy_structure", INSUFFICIENT_DATA, None, [],
                                    "no current_carrier text in any grouped observation")
    return RearchitectureField("legacy_structure", OBSERVED, structures, _obs_ids(observations),
                                "verbatim current_carrier extracted upstream by the Sensor Agent")


def proposed_rearchitecture(observations: List[Dict[str, Any]], config: Dict[str, Any]) -> RearchitectureField:
    """FRAMING ONLY - see module docstring. Never a gating condition."""
    ctext = group_text_for_constraint(observations)
    category, _, _ = best_constraint_category(ctext, config)
    if category == UNCLASSIFIED_CONSTRAINT:
        return RearchitectureField("proposed_rearchitecture", INSUFFICIENT_DATA, None, [],
                                    "no constraint category to build a hypothesis from")
    change_text = group_text_for_change(observations)
    enablers = enabler_hits(change_text, config)
    structures = legacy_structure_text(observations)
    label = _HUMAN_LABEL.get(category, category)
    enabler_phrase = ", ".join(sorted(enablers)) if enablers else "an unidentified structural change"
    structure_phrase = "; ".join(structures) if structures else "the current legacy structure"
    hypothesis = (f"If {enabler_phrase} has genuinely weakened {label}, then {structure_phrase} may no longer be "
                  "structurally necessary and could be rebuilt from zero around today's constraints instead.")
    return RearchitectureField("proposed_rearchitecture", INFERRED, hypothesis, _obs_ids(observations),
                                "FRAMING ONLY - a templated hypothesis, not evidence; must never by itself "
                                "justify a state transition")


def why_now(observations: List[Dict[str, Any]], config: Dict[str, Any]) -> RearchitectureField:
    text = group_text_for_change(observations)
    enablers = enabler_hits(text, config)
    if not enablers:
        return RearchitectureField("why_now", INSUFFICIENT_DATA, None, [],
                                    "no enabler (technological, economic, legal, social, or infrastructural) "
                                    "named in the grouped evidence")
    return RearchitectureField("why_now", OBSERVED, {k: sorted(v) for k, v in enablers.items()},
                                _obs_ids(observations),
                                "specific enabler categories named in the text, not defaulted to AI")


def potential_economic_effect(observations: List[Dict[str, Any]], config: Dict[str, Any]) -> RearchitectureField:
    text = group_text_for_change(observations)
    hits = economic_effect_hits(text, config)
    if not hits:
        return RearchitectureField("potential_economic_effect", INSUFFICIENT_DATA, None, [],
                                    "no cost/speed/margin/capital/quality/convenience/trust/accessibility/"
                                    "scalability language found")
    return RearchitectureField("potential_economic_effect", OBSERVED, sorted(hits), _obs_ids(observations))


def assess_all(observations: List[Dict[str, Any]], config: Dict[str, Any]) -> Dict[str, RearchitectureField]:
    return {
        "existing_business_or_jtbd": existing_business_or_jtbd(observations),
        "historical_constraint": historical_constraint(observations, config),
        "evidence_constraint_existed": evidence_constraint_existed(observations, config),
        "evidence_constraint_weakened": evidence_constraint_weakened(observations, config),
        "legacy_structure": legacy_structure(observations),
        "proposed_rearchitecture": proposed_rearchitecture(observations, config),
        "why_now": why_now(observations, config),
        "potential_economic_effect": potential_economic_effect(observations, config),
    }


def evidence_gaps(fields: Dict[str, Any]) -> List[str]:
    """Accepts either RearchitectureField objects (analyst.py's own use) or
    their .to_dict() form (report.py, reading candidates back out of the
    registry) - same dual-shape tolerance _dims_key uses elsewhere."""
    gaps = []
    for name, f in fields.items():
        if name == "proposed_rearchitecture":
            continue  # framing-only, not a claim that can have an evidence gap
        status = f.status if hasattr(f, "status") else f.get("status")
        note = f.note if hasattr(f, "note") else f.get("note", "")
        if status == INSUFFICIENT_DATA:
            gaps.append(f"{name}: {note}" if note else f"{name}: no evidence found")
        elif status == INFERRED:
            gaps.append(f"{name}: INFERRED only, not OBSERVED - {note}")
    return gaps
