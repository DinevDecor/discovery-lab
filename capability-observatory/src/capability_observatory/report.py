"""Renders C3's own honest run summary.

Deliberately NOT a Sensor Horizon Monitor (that would be cross-sensor
infrastructure spanning every future sensor, out of scope for this slice)
-- just this one sensor's own metrics, in both a machine-readable dict and
a short human-readable markdown report. Both are always regenerable from
the append-only logs; neither is ever treated as a second source of truth.
"""

from __future__ import annotations

from typing import Any, Dict, List

from . import metrics
from .canonical import utc_now_iso


def build_summary(
    panel_item_ids: List[str],
    captures: List[Dict[str, Any]],
    observations: List[Dict[str, Any]],
    identity_breaks: List[Dict[str, Any]],
) -> Dict[str, Any]:
    obs_result = metrics.observability(panel_item_ids, observations)
    success_result = metrics.capture_success(captures)
    changes_result = metrics.state_changes(observations, identity_breaks)
    backlog_result = metrics.identity_backlog(identity_breaks)
    parse_failure_result = metrics.provider_parse_failure_rate(captures)
    stop_rules_result = metrics.evaluate_stop_rules(obs_result, success_result, backlog_result)

    return {
        "generated_at": utc_now_iso(),
        "observability": obs_result,
        "capture_success": success_result,
        "state_changes": changes_result,
        "identity_backlog": backlog_result,
        "provider_parse_failure": parse_failure_result,
        "stop_rules": stop_rules_result,
        "totals": {
            "captures": len(captures),
            "observations": len(observations),
            "identity_breaks": len(identity_breaks),
        },
    }


def render_markdown(summary: Dict[str, Any]) -> str:
    obs = summary["observability"]
    success = summary["capture_success"]
    changes = summary["state_changes"]
    backlog = summary["identity_backlog"]
    parse_failure = summary["provider_parse_failure"]
    stop_rules = summary["stop_rules"]

    lines = [
        f"# C3 Capability Observatory -- run summary ({summary['generated_at']})",
        "",
        "## Totals",
        f"- Captures: {summary['totals']['captures']}",
        f"- Observations: {summary['totals']['observations']}",
        f"- Identity breaks: {summary['totals']['identity_breaks']}",
        "",
        "## Observability",
        f"- {obs['observed_count']}/{obs['panel_size']} panel items have >=1 Observation "
        f"(target >= {metrics.MIN_OBSERVABILITY_COUNT}) -- "
        f"{'MEETS TARGET' if obs['meets_target'] else 'BELOW TARGET'}",
    ]
    if obs["unobserved_panel_item_ids"]:
        lines.append(f"- Unobserved: {', '.join(obs['unobserved_panel_item_ids'])}")

    lines += [
        "",
        "## Capture success",
        f"- {success['ok_count']}/{success['total_attempted']} captures ok "
        f"({success['rate']:.0%}, target >= {metrics.MIN_CAPTURE_SUCCESS_RATE:.0%}) -- "
        f"{'MEETS TARGET' if success['meets_target'] else 'BELOW TARGET'}",
        "",
        "## State changes (raw, unfiltered -- see limitation note)",
        f"- Raw field changes: {changes['raw_field_changes']}",
        f"- Identity breaks: {changes['identity_breaks']}",
        f"- Total: {changes['total_raw_state_changes']}",
        f"- Limitation: {changes['limitation']}",
        "",
        "## Identity backlog",
        f"- {backlog['unresolved_item_count']} panel item(s) with an unresolved identity break "
        f"(trigger > {metrics.MAX_IDENTITY_BACKLOG}) -- "
        f"{'EXCEEDS TRIGGER' if backlog['exceeds_trigger'] else 'within tolerance'}",
    ]
    if backlog["unresolved_panel_item_ids"]:
        lines.append(f"- Items: {', '.join(backlog['unresolved_panel_item_ids'])}")

    lines += ["", "## Provider parse-failure rate"]
    if parse_failure["per_provider"]:
        for provider, row in sorted(parse_failure["per_provider"].items()):
            flag = " -- EXCEEDS ALERT THRESHOLD" if row["exceeds_alert_threshold"] else ""
            lines.append(
                f"- {provider}: {row['parse_error_count']}/{row['total']} "
                f"({row['rate']:.0%}){flag}"
            )
    else:
        lines.append("- No captures recorded yet.")

    lines += [
        "",
        "## Stop-rule evaluation",
        f"- Rule A (capture mechanism failing): {stop_rules['rule_a_capture_mechanism_failing']}",
        f"- Rule B (identity design failing): {stop_rules['rule_b_identity_design_failing']}",
        f"- **Kill or redesign: {stop_rules['kill_or_redesign']}**",
        f"- {stop_rules['note']}",
        "",
    ]
    return "\n".join(lines)
