"""Deterministic assessors for the fourteen required evaluation dimensions.

Every function takes the list of raw observation dicts backing one
candidate group and returns a DimensionResult. A dimension is EVIDENCED
only when the underlying observation text (fields already extracted by the
upstream Sensor Agent - process, pain, current_carrier, failure_mode,
evidence_quote, confidence) actually supports a value; otherwise it stays
INSUFFICIENT_DATA. Nothing here invents evidence, calls a model, or
touches the network - see tests/test_safety.py.

`potential_product_function` is the one dimension explicitly marked as
framing, not evidence (see its docstring) - lifecycle.py must never gate a
state transition on it alone.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from .models import DimensionResult, EVIDENCED, INSUFFICIENT_DATA
from .signature import buyer_bucket, tokens


def _obs_id(o: Dict[str, Any]) -> str:
    return o.get("observation_id", "")


def _marker_hits(observations: List[Dict[str, Any]], fields: Tuple[str, ...],
                  markers: List[str]) -> List[Tuple[str, str]]:
    """Returns (observation_id, marker) pairs for every marker actually
    found in that observation's own text - the evidence trail for every
    marker-based dimension below."""
    hits = []
    for o in observations:
        text = " ".join(str(o.get(f, "") or "") for f in fields).lower()
        for m in markers:
            if m in text:
                hits.append((_obs_id(o), m))
    return hits


def underlying_job_or_problem(observations: List[Dict[str, Any]]) -> DimensionResult:
    phrasings = sorted({o.get("hidden_function_hint", "") for o in observations if o.get("hidden_function_hint")})
    evidence = [_obs_id(o) for o in observations if o.get("hidden_function_hint")]
    if not phrasings:
        return DimensionResult("underlying_job_or_problem", INSUFFICIENT_DATA, None, [],
                                "no hidden_function_hint text in any grouped observation")
    return DimensionResult("underlying_job_or_problem", EVIDENCED, phrasings, evidence,
                            "verbatim hidden_function_hint phrasings extracted upstream by the Sensor Agent")


def pain_severity(observations: List[Dict[str, Any]], thresholds: Dict[str, Any]) -> DimensionResult:
    fields = ("pain", "failure_mode")
    strong = _marker_hits(observations, fields, thresholds["severity_strong_markers"])
    if strong:
        return DimensionResult("pain_severity", EVIDENCED, "SEVERE",
                                sorted({i for i, _ in strong}),
                                f"strong severity markers found: {sorted({m for _, m in strong})}")
    moderate = _marker_hits(observations, fields, thresholds["severity_moderate_markers"])
    if moderate:
        return DimensionResult("pain_severity", EVIDENCED, "MODERATE",
                                sorted({i for i, _ in moderate}),
                                f"moderate severity markers found: {sorted({m for _, m in moderate})}")
    nonempty = [o for o in observations if (o.get("pain") or "").strip()]
    if nonempty:
        return DimensionResult("pain_severity", EVIDENCED, "LOW",
                                [_obs_id(o) for o in nonempty],
                                "pain text present but no severity marker matched")
    return DimensionResult("pain_severity", INSUFFICIENT_DATA, None, [], "no pain text in any grouped observation")


def economic_consequence(observations: List[Dict[str, Any]], thresholds: Dict[str, Any]) -> DimensionResult:
    hits = _marker_hits(observations, ("pain", "failure_mode", "evidence_quote"), thresholds["economic_markers"])
    if not hits:
        return DimensionResult("economic_consequence", INSUFFICIENT_DATA, None, [],
                                "no cost/billing/spend language found in grouped evidence")
    return DimensionResult("economic_consequence", EVIDENCED, sorted({m for _, m in hits}),
                            sorted({i for i, _ in hits}))


def frequency(observations: List[Dict[str, Any]], thresholds: Dict[str, Any]) -> DimensionResult:
    hits = _marker_hits(observations, ("pain", "failure_mode", "process"), thresholds["frequency_markers"])
    if not hits:
        return DimensionResult("frequency", INSUFFICIENT_DATA, None, [],
                                "no repetition language found; a single reported incident is not evidence of "
                                "recurrence")
    return DimensionResult("frequency", EVIDENCED, sorted({m for _, m in hits}), sorted({i for i, _ in hits}))


def identifiable_buyer(observations: List[Dict[str, Any]], thresholds: Dict[str, Any]) -> DimensionResult:
    bucket = buyer_bucket(observations, thresholds)
    if bucket == "unknown":
        return DimensionResult("identifiable_buyer", INSUFFICIENT_DATA, None, [],
                                "no buyer/persona vocabulary matched in process or current_carrier text")
    per_obs = [o for o in observations if buyer_bucket([o], thresholds) == bucket]
    return DimensionResult("identifiable_buyer", EVIDENCED, bucket, [_obs_id(o) for o in per_obs])


def current_workaround(observations: List[Dict[str, Any]]) -> DimensionResult:
    withc = [o for o in observations if (o.get("current_carrier") or "").strip()]
    if not withc:
        return DimensionResult("current_workaround", INSUFFICIENT_DATA, None, [],
                                "no current_carrier text in any grouped observation")
    value = sorted({o["current_carrier"] for o in withc})
    return DimensionResult("current_workaround", EVIDENCED, value, [_obs_id(o) for o in withc],
                            "verbatim current_carrier extracted upstream by the Sensor Agent")


def why_solutions_fail(observations: List[Dict[str, Any]]) -> DimensionResult:
    withf = [o for o in observations if (o.get("failure_mode") or "").strip()]
    if not withf:
        return DimensionResult("why_solutions_fail", INSUFFICIENT_DATA, None, [],
                                "no failure_mode text in any grouped observation")
    value = sorted({o["failure_mode"] for o in withf})
    return DimensionResult("why_solutions_fail", EVIDENCED, value, [_obs_id(o) for o in withf],
                            "verbatim failure_mode extracted upstream by the Sensor Agent")


def potential_product_function(observations: List[Dict[str, Any]]) -> DimensionResult:
    """This is deliberately framing, not evidence: a paraphrase of the
    already-extracted hidden_function_hint text, never an invented pitch.
    lifecycle.py must never advance a state on this dimension alone -
    doing so would be exactly the "promoted because it sounds like a good
    startup idea" failure mode the task forbids."""
    phrasings = sorted({o.get("hidden_function_hint", "") for o in observations if o.get("hidden_function_hint")})
    if not phrasings:
        return DimensionResult("potential_product_function", INSUFFICIENT_DATA, None, [],
                                "no hidden_function_hint text to frame a candidate function from")
    return DimensionResult("potential_product_function", EVIDENCED, phrasings,
                            [_obs_id(o) for o in observations if o.get("hidden_function_hint")],
                            "FRAMING ONLY - not evidence, must never by itself justify a state transition")


def willingness_to_pay(observations: List[Dict[str, Any]], thresholds: Dict[str, Any]) -> DimensionResult:
    hits = _marker_hits(observations, ("pain", "failure_mode", "evidence_quote"),
                         thresholds["willingness_to_pay_markers"])
    if not hits:
        return DimensionResult("willingness_to_pay", INSUFFICIENT_DATA, None, [],
                                "no evidence of money already committed by the buyer (purchase, subscription, "
                                "paid credits); presence of cost alone is not willingness-to-pay evidence")
    return DimensionResult("willingness_to_pay", EVIDENCED, sorted({m for _, m in hits}),
                            sorted({i for i, _ in hits}))


def scalability(observations: List[Dict[str, Any]], thresholds: Dict[str, Any]) -> DimensionResult:
    distinct_sources = {o.get("source", "") for o in observations}
    vendor_hits = _marker_hits(observations, ("process", "pain", "hidden_function_hint", "failure_mode"),
                                thresholds["vendor_mentions"])
    distinct_vendors = {m for _, m in vendor_hits}
    if len(distinct_sources) >= 2 and len(distinct_vendors) >= 2:
        return DimensionResult("scalability", EVIDENCED, "weak_signal_multi_platform",
                                sorted({i for i, _ in vendor_hits}),
                                f"multiple sources ({sorted(distinct_sources)}) and multiple named vendors "
                                f"({sorted(distinct_vendors)}) mentioned - weak signal only, not proof the "
                                "underlying job generalizes beyond these contexts")
    return DimensionResult("scalability", INSUFFICIENT_DATA, None, [],
                            "evidence confined to a single source/vendor context; scalability beyond it is "
                            "not evidenced")


def evidence_diversity(observations: List[Dict[str, Any]]) -> DimensionResult:
    sources = sorted({o.get("source", "") for o in observations})
    return DimensionResult("evidence_diversity", EVIDENCED,
                            {"distinct_sources": len(sources), "sources": sources},
                            [_obs_id(o) for o in observations])


def independent_observation_count(observations: List[Dict[str, Any]]) -> DimensionResult:
    urls = [o.get("url", "") for o in observations if o.get("url")]
    distinct_urls = sorted(set(urls))
    note = ""
    if len(urls) > len(distinct_urls):
        note = ("some observations share the same source URL - they are multiple extractions from one "
                "capture, not independent corroboration; distinct_urls is the more conservative count")
    return DimensionResult(
        "independent_observation_count", EVIDENCED,
        {"observation_count": len(observations), "distinct_urls": len(distinct_urls),
         "distinct_sources": len({o.get("source", "") for o in observations})},
        [_obs_id(o) for o in observations], note,
    )


def contradictory_evidence(observations: List[Dict[str, Any]], thresholds: Dict[str, Any]) -> DimensionResult:
    hits = _marker_hits(observations, ("pain", "failure_mode", "evidence_quote"),
                         thresholds["contradiction_markers"])
    if hits:
        return DimensionResult("contradictory_evidence", EVIDENCED, "contradiction_present",
                                sorted({i for i, _ in hits}),
                                f"contradiction markers found: {sorted({m for _, m in hits})}")
    return DimensionResult("contradictory_evidence", EVIDENCED, "none_observed", [],
                            "checked grouped evidence for explicit contradiction markers; found none - this "
                            "is not proof of consistency, only that this heuristic found nothing")


def confidence_quality(observations: List[Dict[str, Any]]) -> DimensionResult:
    confidences = [float(o.get("confidence", 0.0) or 0.0) for o in observations]
    mean_c = sum(confidences) / len(confidences) if confidences else 0.0
    min_c = min(confidences) if confidences else 0.0
    bucket = "HIGH" if min_c >= 0.8 else "MODERATE" if min_c >= 0.5 else "LOW"
    return DimensionResult("confidence_quality", EVIDENCED,
                            {"mean": round(mean_c, 3), "min": round(min_c, 3), "bucket": bucket},
                            [_obs_id(o) for o in observations])


ASSESSORS_NO_THRESHOLDS = {
    "underlying_job_or_problem": underlying_job_or_problem,
    "current_workaround": current_workaround,
    "why_solutions_fail": why_solutions_fail,
    "potential_product_function": potential_product_function,
    "evidence_diversity": evidence_diversity,
    "independent_observation_count": independent_observation_count,
    "confidence_quality": confidence_quality,
}

ASSESSORS_WITH_THRESHOLDS = {
    "pain_severity": pain_severity,
    "economic_consequence": economic_consequence,
    "frequency": frequency,
    "identifiable_buyer": identifiable_buyer,
    "willingness_to_pay": willingness_to_pay,
    "scalability": scalability,
    "contradictory_evidence": contradictory_evidence,
}


def assess_all(observations: List[Dict[str, Any]], thresholds: Dict[str, Any]) -> Dict[str, DimensionResult]:
    results = {name: fn(observations) for name, fn in ASSESSORS_NO_THRESHOLDS.items()}
    results.update({name: fn(observations, thresholds) for name, fn in ASSESSORS_WITH_THRESHOLDS.items()})
    return results
