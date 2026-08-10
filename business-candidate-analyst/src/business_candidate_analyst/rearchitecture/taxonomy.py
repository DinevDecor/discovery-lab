"""Mode B: Legacy Business Rearchitecture - deterministic classification.

Core question this whole mode exists to answer, per observation group:
"What historical constraint shaped this business, and does that constraint
still exist today?" AI is deliberately just one of sixteen possible
enablers in config/rearchitecture_thresholds.json's enabler_taxonomy - see
that file's comment for why, and see lifecycle.py for the hard rule that
an AI-only enabler hit can never by itself justify VALIDATING.

Every taxonomy here is a GENERIC REASONING CATEGORY (buffer_inventory,
intermediation_trust, physical_presence, ...), generalized from the task's
own worked examples (warehouse inventory, intermediaries, branch networks,
manual coordination, vertical integration, safety buffers) without hard-
coding those specific industries - a new industry that happens to fit one
of these shapes is classified the same way a hard-coded example would be,
without ever having been named in the taxonomy.

Nothing here calls a model or the network - same discipline as Mode A's
signature.py.
"""

from __future__ import annotations

from typing import Any, Dict, List, Set, Tuple

UNCLASSIFIED_CONSTRAINT = "unclassified"


def _lower_join(texts: List[str]) -> str:
    return " ".join(t or "" for t in texts).lower()


def _hits(text: str, markers: List[str]) -> Set[str]:
    """Lowercases defensively - callers normally pass already-lowered text
    (group_text_for_constraint/group_text_for_change), but every public
    marker-matching function here is safe to call with raw-cased text too."""
    text_l = (text or "").lower()
    return {m for m in markers if m in text_l}


def constraint_category_scores(text: str, config: Dict[str, Any]) -> Dict[str, Dict[str, Set[str]]]:
    """For every constraint_taxonomy bucket, the legacy_markers and
    reason_markers actually found in `text`. Every bucket is returned
    (possibly with empty hit sets) so callers can see what was checked,
    not just what matched."""
    out = {}
    for category, spec in config["constraint_taxonomy"].items():
        out[category] = {
            "legacy_hits": _hits(text, spec["legacy_markers"]),
            "reason_hits": _hits(text, spec["reason_markers"]),
        }
    return out


def best_constraint_category(text: str, config: Dict[str, Any]) -> Tuple[str, Set[str], Set[str]]:
    """The constraint_taxonomy bucket with the most legacy_marker hits.
    Returns (category, legacy_hits, reason_hits); category is
    UNCLASSIFIED_CONSTRAINT if nothing matched (never guessed)."""
    scores = constraint_category_scores(text, config)
    best_category, best_legacy, best_reason, best_count = UNCLASSIFIED_CONSTRAINT, set(), set(), 0
    for category, hits in scores.items():
        count = len(hits["legacy_hits"])
        if count > best_count:
            best_category, best_legacy, best_reason, best_count = category, hits["legacy_hits"], hits["reason_hits"], count
    return best_category, best_legacy, best_reason


def enabler_hits(text: str, config: Dict[str, Any]) -> Dict[str, Set[str]]:
    """Every enabler_taxonomy bucket with at least one hit in `text`. AI is
    structurally just another key in this dict - nothing here treats it
    specially."""
    hits = {}
    for bucket, markers in config["enabler_taxonomy"].items():
        found = _hits(text, markers)
        if found:
            hits[bucket] = found
    return hits


def is_ai_only(enablers: Dict[str, Set[str]]) -> bool:
    """True when the ONLY enabler evidence found is the 'ai' bucket - the
    exact condition lifecycle.py's no-AI-bias rule checks for."""
    return set(enablers.keys()) == {"ai"}


def still_binding_hits(text: str, config: Dict[str, Any]) -> Set[str]:
    return _hits(text, config["still_binding_markers"])


def weakening_hits(text: str, config: Dict[str, Any]) -> Set[str]:
    return _hits(text, config["weakening_markers"])


def economic_effect_hits(text: str, config: Dict[str, Any]) -> Set[str]:
    return _hits(text, config["economic_effect_markers"])


def group_text_for_constraint(observations: List[Dict[str, Any]]) -> str:
    """process + hidden_function_hint + pain + failure_mode - the fields
    most likely to narrate WHY a workaround exists."""
    return _lower_join([
        f"{o.get('process', '')} {o.get('hidden_function_hint', '')} {o.get('pain', '')} {o.get('failure_mode', '')}"
        for o in observations
    ])


def group_text_for_change(observations: List[Dict[str, Any]]) -> str:
    """pain + failure_mode + evidence_quote - where a change/weakening
    claim, if present at all, is most likely to be quoted verbatim."""
    return _lower_join([
        f"{o.get('pain', '')} {o.get('failure_mode', '')} {o.get('evidence_quote', '')}"
        for o in observations
    ])


def legacy_structure_text(observations: List[Dict[str, Any]]) -> List[str]:
    """The workaround itself - current_carrier is already exactly this
    field, extracted upstream by the Sensor Agent. Not re-derived here."""
    return sorted({o.get("current_carrier", "") for o in observations if (o.get("current_carrier") or "").strip()})
