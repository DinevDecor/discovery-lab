"""30-day evaluation metrics and the accepted stop-rule decision.

Every function here reads from the append-only stores; none of them write
anything. A materialized report (report.py) is allowed to cache these
numbers for humans to read, but this module is always the source of truth,
recomputed fresh from captures.jsonl / observations.jsonl /
identity_breaks.jsonl every time it runs.
"""

from __future__ import annotations

from typing import Any, Dict, List

#: Literal accepted thresholds for the 20-item panel (see
#: docs/architecture design review and README.md "30-day stop rules").
#: Not derived as a fraction of panel size on purpose -- these are the
#: exact numbers that were reviewed and accepted, not a formula that could
#: round differently if the panel size ever changes.
MIN_OBSERVABILITY_COUNT = 15
MIN_CAPTURE_SUCCESS_RATE = 0.60
MAX_IDENTITY_BACKLOG = 3
PARSE_FAILURE_ALERT_RATE = 0.20


def observability(panel_item_ids: List[str], observations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """How many of the panel items produced at least one Observation."""
    observed_items = {row["panel_item_id"] for row in observations if row.get("panel_item_id")}
    covered = [pid for pid in panel_item_ids if pid in observed_items]
    return {
        "panel_size": len(panel_item_ids),
        "observed_count": len(covered),
        "observed_panel_item_ids": sorted(covered),
        "unobserved_panel_item_ids": sorted(set(panel_item_ids) - observed_items),
        "meets_target": len(covered) >= MIN_OBSERVABILITY_COUNT,
    }


def capture_success(captures: List[Dict[str, Any]]) -> Dict[str, Any]:
    """capture_outcome == 'ok' divided by all attempted captures."""
    total = len(captures)
    ok = sum(1 for c in captures if c.get("capture_outcome") == "ok")
    rate = (ok / total) if total else 0.0
    return {
        "total_attempted": total,
        "ok_count": ok,
        "rate": rate,
        "meets_target": rate >= MIN_CAPTURE_SUCCESS_RATE,
    }


def state_changes(observations: List[Dict[str, Any]], identity_breaks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Count of raw observed changes.

    Deliberately NOT statistically filtered -- per instruction, this slice
    reports raw changes rather than engineering a "meaningful change"
    threshold (percentage bands, noise floors, etc). Any difference in
    price, availability, or lead_time_days between two chronologically
    adjacent Observations for the same panel item counts as one change,
    plus every identity break counts as one change. This will over-count
    relative to a human's intuitive sense of "meaningful" -- documented
    here as a known limitation, not hidden.
    """
    by_item: Dict[str, List[Dict[str, Any]]] = {}
    for row in observations:
        by_item.setdefault(row["panel_item_id"], []).append(row)

    raw_changes = 0
    per_item_changes: Dict[str, int] = {}
    for panel_item_id, rows in by_item.items():
        rows_sorted = sorted(rows, key=lambda r: (r.get("observed_at") or "", r.get("recorded_at") or ""))
        count = 0
        for prev, cur in zip(rows_sorted, rows_sorted[1:]):
            if prev.get("price") != cur.get("price"):
                count += 1
            if prev.get("availability") != cur.get("availability"):
                count += 1
            if prev.get("lead_time_days") != cur.get("lead_time_days"):
                count += 1
        per_item_changes[panel_item_id] = count
        raw_changes += count

    total = raw_changes + len(identity_breaks)
    return {
        "raw_field_changes": raw_changes,
        "identity_breaks": len(identity_breaks),
        "total_raw_state_changes": total,
        "per_panel_item": per_item_changes,
        "limitation": (
            "Raw, unfiltered change count -- any differing price, availability, "
            "or lead_time_days between chronologically adjacent observations for "
            "the same item counts as one change. Not adjusted for noise, "
            "measurement rounding, or economic significance."
        ),
    }


def identity_backlog(identity_breaks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Panel items (not break events) with at least one UNRESOLVED break."""
    unresolved_items = {
        row["panel_item_id"] for row in identity_breaks if row.get("status") == "UNRESOLVED"
    }
    return {
        "unresolved_item_count": len(unresolved_items),
        "unresolved_panel_item_ids": sorted(unresolved_items),
        "exceeds_trigger": len(unresolved_items) > MAX_IDENTITY_BACKLOG,
    }


def provider_parse_failure_rate(captures: List[Dict[str, Any]]) -> Dict[str, Any]:
    """parse_error rate per provider (source), and which providers exceed
    the 20% alert threshold."""
    by_provider: Dict[str, Dict[str, int]] = {}
    for c in captures:
        provider = c.get("source", "unknown")
        bucket = by_provider.setdefault(provider, {"total": 0, "parse_error": 0})
        bucket["total"] += 1
        if c.get("capture_outcome") == "parse_error":
            bucket["parse_error"] += 1

    per_provider = {}
    exceeding = []
    for provider, bucket in by_provider.items():
        rate = (bucket["parse_error"] / bucket["total"]) if bucket["total"] else 0.0
        per_provider[provider] = {
            "total": bucket["total"],
            "parse_error_count": bucket["parse_error"],
            "rate": rate,
            "exceeds_alert_threshold": rate > PARSE_FAILURE_ALERT_RATE,
        }
        if rate > PARSE_FAILURE_ALERT_RATE:
            exceeding.append(provider)

    return {"per_provider": per_provider, "providers_exceeding_threshold": sorted(exceeding)}


def evaluate_stop_rules(
    observability_result: Dict[str, Any],
    capture_success_result: Dict[str, Any],
    identity_backlog_result: Dict[str, Any],
) -> Dict[str, Any]:
    """The accepted combined 30-day decision.

    Rule A: capture success < 60% AND observability < 15/20 -- the capture
            mechanism itself doesn't work for this domain/provider set.
    Rule B: more than 3/20 panel items carry an unresolved identity break --
            the fingerprint design doesn't fit this domain's real pages.

    Zero state changes is NEVER part of this decision -- sparse-but-real
    evidence in month one is the expected, accepted shape of this
    experiment, not a failure signal. state_changes() is reported
    separately and is informative only.
    """
    rule_a = (
        not capture_success_result["meets_target"]
        and not observability_result["meets_target"]
    )
    rule_b = identity_backlog_result["exceeds_trigger"]
    return {
        "rule_a_capture_mechanism_failing": rule_a,
        "rule_b_identity_design_failing": rule_b,
        "kill_or_redesign": rule_a or rule_b,
        "note": (
            "state_changes is deliberately excluded from this decision. "
            "Zero interesting price/lead-time movement in the first 30 days "
            "does not, by itself, trigger kill or redesign."
        ),
    }
