"""Deterministic "same underlying business opportunity" gate.

Constraint Archaeology's anomaly clustering already groups observations by
*same technical mechanism* (same-mechanism gate). That is a narrower
question than the one this module answers: two anomalies with genuinely
different failure mechanisms can still be the same underlying business
opportunity if they share the same buyer and the same missing function -
e.g. "no real-time cost telemetry during an API call" and "quota reset
overwrites unused paid allocation" are different mechanisms but the same
buyer (API consumer) chasing the same missing function (resource
visibility/control).

Conversely, two anomalies can read as thematically similar prose and still
not be the same opportunity - the point of this gate is to keep that
distinction auditable and keyword-based rather than "the wording sounds
alike", per the task's explicit instruction not to merge on similarity
alone.

Nothing here calls a model. Buyer/function classification is a keyword
vote over a small, fixed, domain-generic taxonomy (config/thresholds.json)
- the same style as ca_agents.memory.classify_function, but independently
implemented so this package has zero import dependency on ca_agents.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple

from .models import OpportunitySignature

_TOKEN_RE = re.compile(r"[a-zA-Z0-9_]+")

UNKNOWN_BUYER = "unknown"
UNCLASSIFIED_FUNCTION = "unclassified"


def tokens(text: str, min_len: int = 4) -> set:
    return {t for t in _TOKEN_RE.findall((text or "").lower()) if len(t) >= min_len}


def jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 0.0
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


def _vote(text: str, taxonomy: Dict[str, List[str]], fallback: str) -> str:
    text_l = (text or "").lower()
    scores = {bucket: sum(1 for kw in kws if kw in text_l) for bucket, kws in taxonomy.items()}
    best = max(scores, key=scores.get) if scores else fallback
    return best if scores.get(best, 0) > 0 else fallback


def buyer_bucket(observations: List[Dict[str, Any]], thresholds: Dict[str, Any]) -> str:
    text = " ".join(f"{o.get('process', '')} {o.get('current_carrier', '')}" for o in observations)
    return _vote(text, thresholds["buyer_taxonomy"], UNKNOWN_BUYER)


def function_class(observations: List[Dict[str, Any]], thresholds: Dict[str, Any]) -> str:
    text = " ".join(
        f"{o.get('hidden_function_hint', '')} {o.get('pain', '')} {o.get('failure_mode', '')}"
        for o in observations
    )
    return _vote(text, thresholds["function_taxonomy"], UNCLASSIFIED_FUNCTION)


def signature_for_group(observations: List[Dict[str, Any]], thresholds: Dict[str, Any]) -> OpportunitySignature:
    return OpportunitySignature(
        buyer_bucket=buyer_bucket(observations, thresholds),
        function_class=function_class(observations, thresholds),
    )


def _workaround_tokens(observations: List[Dict[str, Any]], thresholds: Dict[str, Any]) -> set:
    min_len = thresholds.get("job_term_min_len", 4)
    text = " ".join(o.get("current_carrier", "") for o in observations)
    return tokens(text, min_len)


def _failure_tokens(observations: List[Dict[str, Any]], thresholds: Dict[str, Any]) -> set:
    min_len = thresholds.get("job_term_min_len", 4)
    text = " ".join(o.get("failure_mode", "") for o in observations)
    return tokens(text, min_len)


def _function_field_text(observations: List[Dict[str, Any]]) -> str:
    return " ".join(
        f"{o.get('hidden_function_hint', '')} {o.get('pain', '')} {o.get('failure_mode', '')}"
        for o in observations
    ).lower()


def _bucket_keyword_hits(text: str, keywords: List[str]) -> set:
    return {kw for kw in keywords if kw in text}


def same_opportunity(
    sig_a: OpportunitySignature, obs_a: List[Dict[str, Any]],
    sig_b: OpportunitySignature, obs_b: List[Dict[str, Any]],
    thresholds: Dict[str, Any],
) -> Tuple[bool, List[str]]:
    """Symmetric gate. Both groups' buyer bucket AND function class must
    match (neither may be the "unknown"/"unclassified" fallback) - that
    alone is two independent controlled-vocabulary votes agreeing, not
    "the wording sounds similar". On top of that, at least one of two
    corroborating signals must hold:

      1. the two groups' text hits at least `min_shared_function_keywords`
         (default 2) of the SAME specific keywords from the matched
         function_class's own list (e.g. both mention "consumption" AND
         "billing", not just both landing in the resource_visibility
         bucket) - the strongest, most literal evidence that the missing
         function is materially the same. A floor of 1 was tried first and
         rejected: single generic words like "cost" or "budget" recur
         across unrelated topics (hardware procurement, grid curtailment)
         often enough that a lone shared keyword is coincidence, not
         corroboration - see business-candidate-analyst/README.md's
         "false-positive controls" section for the real run that caught
         this;
      2. failing that, generic workaround/failure wording overlap above a
         floor (same fallback CA's own dedup-adjacent code uses) - BUT,
         and this is the fix for a second real-corpus false-positive class
         (see README's false-positive controls section, "single-field
         Jaccard coincidence"), BOTH the workaround_jaccard AND the
         failure_jaccard must independently clear that floor, not either
         alone. A same-day human review of the real corpus found that
         every merge relying on this fallback with only one of the two
         fields passing (the other sitting at exactly 0.0 shared tokens)
         was a false merge: e.g. "keeping a livestream broadcasting on
         game-store pages" merged into a financial-transaction-
         reconciliation candidate purely because both failure_mode texts
         happened to contain the generic phrase "requiring manual
         intervention" (failure_jaccard 0.148, workaround_jaccard 0.0 -
         the actual workaround context, accounting reconciliation vs.
         local streaming software, shared nothing). Requiring both fields
         is the direct structural analogue of requiring 2 shared keywords
         instead of 1 above: a single field's overlap is exactly as prone
         to generic-phrase coincidence as a single shared keyword is: the
         workaround and failure_mode fields describe different aspects of
         the opportunity (what the buyer currently does vs. how it
         breaks), so genuine corroboration should show up in both, not
         survive on a coincidental phrase in only one.

    A whole-document token Jaccard was tried and rejected here: two
    genuinely related real-world reports about the same missing function
    routinely share only a handful of tokens once names, numbers and
    incidental wording are included, so a whole-document ratio requirement
    refuses almost every real merge. Scoping the keyword check to the
    taxonomy that already produced the function_class match keeps the
    signal specific without being that fragile.

    Any failed condition is enough to refuse the merge - refusing is
    itself information, mirrored in the reasons list for audit.

    One short-circuit precedes all of the above: if any observation in
    either group shares its source `url` with an observation in the other
    group, they are not two pieces of evidence at all - they are the same
    capture extracted twice (the Sensor Agent sometimes emits more than one
    Observation per Capture). Refusing that "merge" on a taxonomy technicality
    would be wrong in the other direction: two extractions of one article
    are certain to be about the same opportunity, not merely likely."""
    reasons = []

    urls_a = {o.get("url") for o in obs_a if o.get("url")}
    urls_b = {o.get("url") for o in obs_b if o.get("url")}
    shared_urls = urls_a & urls_b
    if shared_urls:
        reasons.append(f"shared source URL {sorted(shared_urls)} - same capture extracted more than once, "
                        "not independent evidence of a distinct opportunity")
        return True, reasons

    if sig_a.buyer_bucket == UNKNOWN_BUYER or sig_b.buyer_bucket == UNKNOWN_BUYER:
        reasons.append("buyer bucket unknown for at least one group - refusing merge")
        return False, reasons
    if sig_a.buyer_bucket != sig_b.buyer_bucket:
        reasons.append(f"buyer bucket differs: {sig_a.buyer_bucket} vs {sig_b.buyer_bucket}")
        return False, reasons

    if sig_a.function_class == UNCLASSIFIED_FUNCTION or sig_b.function_class == UNCLASSIFIED_FUNCTION:
        reasons.append("function class unclassified for at least one group - refusing merge")
        return False, reasons
    if sig_a.function_class != sig_b.function_class:
        reasons.append(f"function class differs: {sig_a.function_class} vs {sig_b.function_class}")
        return False, reasons

    function_keywords = thresholds["function_taxonomy"][sig_a.function_class]
    hits_a = _bucket_keyword_hits(_function_field_text(obs_a), function_keywords)
    hits_b = _bucket_keyword_hits(_function_field_text(obs_b), function_keywords)
    shared_keywords = sorted(hits_a & hits_b)
    min_shared = thresholds.get("min_shared_function_keywords", 2)

    w_j = jaccard(_workaround_tokens(obs_a, thresholds), _workaround_tokens(obs_b, thresholds))
    f_j = jaccard(_failure_tokens(obs_a, thresholds), _failure_tokens(obs_b, thresholds))
    w_min = thresholds.get("workaround_jaccard_min", 0.12)
    f_min = thresholds.get("failure_jaccard_min", 0.12)

    jaccard_fallback_ok = w_j >= w_min and f_j >= f_min
    if len(shared_keywords) < min_shared and not jaccard_fallback_ok:
        reasons.append(
            f"buyer/function bucket match ({sig_a.buyer_bucket}/{sig_a.function_class}) but only "
            f"{len(shared_keywords)} shared {sig_a.function_class} keyword(s) {shared_keywords} "
            f"(<{min_shared} required) and workaround_jaccard={w_j:.2f}, failure_jaccard={f_j:.2f} "
            f"(need >={w_min} on BOTH, not either alone) - same bucket, not evidenced as same missing function"
        )
        return False, reasons

    reasons.append(f"buyer_bucket={sig_a.buyer_bucket}, function_class={sig_a.function_class}, "
                    f"shared_keywords={shared_keywords}, workaround_jaccard={w_j:.2f}, failure_jaccard={f_j:.2f}")
    return True, reasons
