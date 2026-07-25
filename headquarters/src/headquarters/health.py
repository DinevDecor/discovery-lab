"""Ecosystem Health Engine. Every metric below has one formula, stated
in its own docstring and echoed into the HealthMetric it returns —
per EXEC-004's own requirement, nothing here is allowed to exist
without a documented, reproducible calculation."""

from __future__ import annotations

import re
from datetime import date, datetime, timezone

from .collector import Collected
from .models import Evidence, HealthMetric


def _parse_date(value: str) -> date | None:
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", value)
    if not m:
        return None
    try:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def state_visibility(collected: Collected) -> tuple[HealthMetric, float]:
    """(# repos with at least 2 parsed state fields) / (# configured
    repos). A repo with no state file, or one this tool's tolerant
    parsers could not extract anything meaningful from, counts as not
    visible — matching the honest INSUFFICIENT_EVIDENCE stance used
    throughout this ecosystem's tooling rather than assuming health."""
    total = len(collected.repos)
    visible = [r for r in collected.repos.values() if len(r.state_fields) >= 2]
    score = len(visible) / total if total else 0.0
    evidence = [
        Evidence(r.name, f"state file: {r.state_file_path or 'none configured/found'}")
        for r in collected.repos.values()
    ]
    return HealthMetric(
        name="State Visibility",
        value=f"{len(visible)}/{total} repos ({round(score * 100)}%)",
        formula="(# configured repos with >=2 parsed state fields) / (# configured repos)",
        evidence=evidence,
    ), score


def observation_cleanliness(collected: Collected) -> tuple[HealthMetric, float | None]:
    """1 - (MISMATCH / total observations) from the Observation
    Agent's own latest report — Headquarters reads this number, it
    does not recompute it. None (excluded from Overall Health) if no
    report exists yet."""
    c = collected.observation.confidence_counts
    total = sum(c.values())
    if not c or total == 0:
        return HealthMetric(
            name="Observation Cleanliness",
            value="INSUFFICIENT_EVIDENCE (no Observation Agent report found)",
            formula="1 - (MISMATCH / total observations) from the latest Observation Agent report",
            evidence=[],
        ), None
    score = 1 - (c.get("MISMATCH", 0) / total)
    return HealthMetric(
        name="Observation Cleanliness",
        value=f"{round(score * 100)}% ({c.get('MISMATCH', 0)} MISMATCH of {total})",
        formula="1 - (MISMATCH / total observations) from the latest Observation Agent report",
        evidence=[Evidence("observation-agent", collected.observation.report_path or "")],
    ), max(0.0, min(1.0, score))


def decision_currency(collected: Collected, threshold_days: int, now: date) -> tuple[HealthMetric, float]:
    """1 - (# PROPOSED Ledger entries older than threshold_days /
    total Ledger entries). An empty Ledger scores 1.0 (nothing
    overdue) with that stated explicitly, not silently."""
    entries = collected.ledger_entries
    if not entries:
        return HealthMetric(
            name="Decision Currency",
            value="100% (Recommendation Ledger has no entries yet)",
            formula="1 - (# PROPOSED entries older than threshold / total entries)",
            evidence=[],
        ), 1.0

    overdue = 0
    for e in entries:
        if e.fields.get("status") != "PROPOSED":
            continue
        d = _parse_date(e.fields.get("date_proposed", ""))
        if d and (now - d).days > threshold_days:
            overdue += 1
    score = 1 - (overdue / len(entries))
    return HealthMetric(
        name="Decision Currency",
        value=f"{round(score * 100)}% ({overdue}/{len(entries)} entries overdue for a decision)",
        formula=f"1 - (# PROPOSED entries older than {threshold_days}d / total entries)",
        evidence=[Evidence("RECOMMENDATION-LEDGER.md", f"{len(entries)} entries")],
    ), max(0.0, score)


def governance_integrity(drift_findings: list) -> tuple[HealthMetric, float]:
    """1 - (# MISMATCH-confidence drift findings / # drift checks
    run). Every drift check that ran and found nothing counts toward
    the denominator, so a repo with zero findings genuinely scores
    higher than one this tool never checked."""
    from .models import Confidence

    total_checks = max(len(drift_findings), 1)
    mismatches = sum(1 for f in drift_findings if f.confidence == Confidence.MISMATCH)
    score = 1 - (mismatches / total_checks) if drift_findings else 1.0
    return HealthMetric(
        name="Governance Integrity",
        value=f"{round(score * 100)}% ({mismatches} confirmed governance findings)",
        formula="1 - (# MISMATCH-confidence drift findings / # drift findings surfaced this run)",
        evidence=[Evidence("drift-detector", f"{len(drift_findings)} findings this run")],
    ), max(0.0, score)


def observation_coverage(collected: Collected, total_repos: int) -> HealthMetric:
    """(# repos SCANned by the Observation Agent's latest run) /
    (# configured repos). Read directly from the execution log, not
    recomputed."""
    scanned = len(collected.observation.scanned_repos)
    if not collected.observation.log_path:
        return HealthMetric(
            name="Observation Coverage",
            value="INSUFFICIENT_EVIDENCE (no Observation Agent execution log found)",
            formula="(# repos SCANned in the latest execution log) / (# configured repos)",
            evidence=[],
        )
    return HealthMetric(
        name="Observation Coverage",
        value=f"{scanned}/{total_repos} repos ({round(100 * scanned / total_repos) if total_repos else 0}%)",
        formula="(# repos SCANned in the latest execution log) / (# configured repos)",
        evidence=[Evidence("observation-agent", collected.observation.log_path)],
    )


def recommendation_backlog(collected: Collected) -> HealthMetric:
    """Count of Recommendation Ledger entries with status PROPOSED."""
    n = sum(1 for e in collected.ledger_entries if e.fields.get("status") == "PROPOSED")
    return HealthMetric(
        name="Recommendation Backlog",
        value=str(n),
        formula="count of RECOMMENDATION-LEDGER.md entries with status: PROPOSED",
        evidence=[Evidence("RECOMMENDATION-LEDGER.md", f"{n} PROPOSED of {len(collected.ledger_entries)} total")],
    )


def decision_backlog(collected: Collected, threshold_days: int, now: date) -> HealthMetric:
    """Stricter subset of Recommendation Backlog: PROPOSED entries
    older than threshold_days with no status change — genuinely
    overdue for a human decision, not merely unreviewed yet."""
    overdue = []
    for e in collected.ledger_entries:
        if e.fields.get("status") != "PROPOSED":
            continue
        d = _parse_date(e.fields.get("date_proposed", ""))
        if d and (now - d).days > threshold_days:
            overdue.append(e.fields.get("recommendation_id", "?"))
    return HealthMetric(
        name="Decision Backlog",
        value=str(len(overdue)),
        formula=f"count of PROPOSED entries with date_proposed more than {threshold_days} day(s) before this run",
        evidence=[Evidence("RECOMMENDATION-LEDGER.md", ", ".join(overdue) or "none overdue")],
    )


def overall_health(sub_scores: list[float | None]) -> HealthMetric:
    """Simple mean of every sub-score that could actually be computed
    this run (None entries — insufficient evidence — are excluded
    from the average, not treated as zero, so a missing report lowers
    confidence in the number rather than silently crashing the
    ecosystem's apparent health)."""
    usable = [s for s in sub_scores if s is not None]
    if not usable:
        return HealthMetric(
            name="Overall Health",
            value="INSUFFICIENT_EVIDENCE",
            formula="mean of State Visibility, Observation Cleanliness, Decision Currency, Governance Integrity (each in 0..1; unavailable sub-scores excluded, not zeroed)",
            evidence=[],
        )
    mean = sum(usable) / len(usable)
    note = "" if len(usable) == len(sub_scores) else f" ({len(usable)}/{len(sub_scores)} sub-scores available)"
    return HealthMetric(
        name="Overall Health",
        value=f"{round(mean * 100)}%{note}",
        formula="mean of State Visibility, Observation Cleanliness, Decision Currency, Governance Integrity (each in 0..1; unavailable sub-scores excluded, not zeroed)",
        evidence=[],
    )


def compute_health(collected: Collected, drift_findings: list, threshold_days: int, now: date | None = None) -> dict[str, HealthMetric]:
    now = now or datetime.now(timezone.utc).date()
    metrics: dict[str, HealthMetric] = {}

    sv_metric, sv_score = state_visibility(collected)
    oc_metric, oc_score = observation_cleanliness(collected)
    dc_metric, dc_score = decision_currency(collected, threshold_days, now)
    gi_metric, gi_score = governance_integrity(drift_findings)

    metrics["state_visibility"] = sv_metric
    metrics["observation_cleanliness"] = oc_metric
    metrics["decision_currency"] = dc_metric
    metrics["governance_integrity"] = gi_metric
    metrics["overall_health"] = overall_health([sv_score, oc_score, dc_score, gi_score])
    metrics["observation_coverage"] = observation_coverage(collected, len(collected.repos))
    metrics["recommendation_backlog"] = recommendation_backlog(collected)
    metrics["decision_backlog"] = decision_backlog(collected, threshold_days, now)
    return metrics
