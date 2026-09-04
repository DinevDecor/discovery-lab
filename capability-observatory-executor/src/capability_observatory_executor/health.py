"""Executor health report: diagnostics ON TOP of C3's own report, never a
replacement for it and never a second stop-rule authority.

capability_observatory/metrics.py's stop rules (Rule A / Rule B) are
untouched by this package and remain the only kill-or-redesign decision.
This module answers a narrower, executor-specific question: did the
CAPTURE MECHANISM work this run, broken down by whether a failure was
infrastructure noise (executor-side) or a real signal about a provider
(provider-side) -- the distinction Slice 03 exists to make legible (see
docs/decisions/003-c3-capture-outcome-vocabulary-extended.md).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .outcomes import is_executor_side_failure, is_provider_side_failure, is_success


@dataclass
class ProviderAttempt:
    provider: str
    panel_item_id: str
    capture_method: str            # api | html | human
    classification: str            # AUTOMATED_OK | HUMAN_FALLBACK_REQUIRED | PROVIDER_BLOCKED | EXECUTOR_FAILURE
    outcome: str                    # C3 capture_outcome actually recorded
    filename: Optional[str] = None  # submission filename, for reconciling against C3's process output
    capture_written: bool = False
    observation_written: bool = False


def classify_attempt(capture_method: str, outcome: str) -> str:
    if is_success(outcome):
        return "AUTOMATED_OK" if capture_method != "human" else "HUMAN_FALLBACK_REQUIRED"
    if capture_method == "human":
        return "HUMAN_FALLBACK_REQUIRED"
    if is_executor_side_failure(outcome):
        return "EXECUTOR_FAILURE"
    if is_provider_side_failure(outcome):
        return "PROVIDER_BLOCKED"
    return "EXECUTOR_FAILURE"   # legacy/ambiguous outcomes default to the conservative bucket


def build_health_report(attempts: List[ProviderAttempt], process_summary: Dict[str, Any]) -> Dict[str, Any]:
    providers = sorted({a.provider for a in attempts})
    by_provider: Dict[str, Dict[str, Any]] = {}
    for provider in providers:
        provider_attempts = [a for a in attempts if a.provider == provider]
        by_provider[provider] = {
            "items_attempted": len(provider_attempts),
            "automated_ok": sum(1 for a in provider_attempts if a.classification == "AUTOMATED_OK"),
            "human_fallback_required": sum(1 for a in provider_attempts if a.classification == "HUMAN_FALLBACK_REQUIRED"),
            "provider_blocked": sum(1 for a in provider_attempts if a.classification == "PROVIDER_BLOCKED"),
            "executor_failure": sum(1 for a in provider_attempts if a.classification == "EXECUTOR_FAILURE"),
        }

    total = len(attempts)
    automated_ok = sum(1 for a in attempts if a.classification == "AUTOMATED_OK")
    executor_network_blocked = sum(1 for a in attempts if a.outcome == "executor_network_blocked")
    provider_access_blocked = sum(1 for a in attempts if a.outcome == "provider_access_blocked")
    api_errors = sum(1 for a in attempts if a.outcome in ("credentials_error", "api_quota_error"))
    successful_observations = sum(1 for a in attempts if a.observation_written)
    human_fallback_required = sum(1 for a in attempts if a.classification == "HUMAN_FALLBACK_REQUIRED")

    return {
        "providers_attempted": providers,
        "per_provider": by_provider,
        "items_attempted": total,
        "automated_captures_succeeded": automated_ok,
        "human_fallback_required": human_fallback_required,
        "executor_network_blocked": executor_network_blocked,
        "provider_access_blocked": provider_access_blocked,
        "api_errors": api_errors,
        "successful_observations": successful_observations,
        "automation_coverage_pct": round(100.0 * automated_ok / total, 1) if total else 0.0,
        "cost_note": (
            "GitHub-hosted Actions minutes on the free tier; DigiKey and Mouser API tiers "
            "used here are both free -- no measurable per-run cost for this executor as "
            "configured. Revisit if a metered service (e.g. a browser-automation vendor) "
            "is ever added for a specific provider."
        ),
        "infrastructure_failure_excluded_from_market_evidence": (
            executor_network_blocked == 0
            or all(not a.observation_written for a in attempts if a.outcome == "executor_network_blocked")
        ),
        "c3_process_summary": process_summary,
        "per_attempt": [
            {
                "provider": a.provider,
                "panel_item_id": a.panel_item_id,
                "capture_method": a.capture_method,
                "classification": a.classification,
                "outcome": a.outcome,
                "capture_written": a.capture_written,
                "observation_written": a.observation_written,
            }
            for a in attempts
        ],
    }


def render_markdown(report: Dict[str, Any], generated_at: str) -> str:
    lines = [f"# C3 Capture Executor -- health report ({generated_at})", ""]
    lines.append("## Coverage")
    lines.append(f"- Items attempted: {report['items_attempted']}")
    lines.append(f"- Automated captures succeeded: {report['automated_captures_succeeded']}")
    lines.append(f"- Automation coverage: {report['automation_coverage_pct']}%")
    lines.append(f"- Human fallback required: {report['human_fallback_required']}")
    lines.append("")
    lines.append("## Infrastructure vs. provider signal")
    lines.append(f"- executor_network_blocked: {report['executor_network_blocked']}")
    lines.append(f"- provider_access_blocked: {report['provider_access_blocked']}")
    lines.append(f"- API errors (credentials/quota): {report['api_errors']}")
    lines.append(f"- Successful observations: {report['successful_observations']}")
    lines.append(
        f"- Infrastructure failure counted as market evidence: "
        f"{'NO (correct)' if report['infrastructure_failure_excluded_from_market_evidence'] else 'YES -- BUG'}"
    )
    lines.append("")
    lines.append("## Per provider")
    for provider, stats in sorted(report["per_provider"].items()):
        lines.append(
            f"- {provider}: {stats['items_attempted']} attempted, "
            f"{stats['automated_ok']} automated_ok, "
            f"{stats['human_fallback_required']} human_fallback, "
            f"{stats['provider_blocked']} provider_blocked, "
            f"{stats['executor_failure']} executor_failure"
        )
    lines.append("")
    lines.append(f"## Cost\n{report['cost_note']}")
    lines.append("")
    lines.append("## C3 process summary (from run_capability_observatory.py process)")
    lines.append("```json")
    import json
    lines.append(json.dumps(report["c3_process_summary"], indent=2, sort_keys=True))
    lines.append("```")
    return "\n".join(lines) + "\n"
