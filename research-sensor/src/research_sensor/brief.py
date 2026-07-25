"""Renders the Daily Research Brief and Weekly Research Intelligence
Report EXEC-010's Headquarters Integration section names. The Research
Signal Registry (research-registry.json) is the machine-readable
artifact; these two briefs are read-only renderings of it.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from .models import Domain, ResearchSignal

_DOMAIN_LABELS = {
    Domain.AI_FOR_SCIENTIFIC_DISCOVERY: "AI for Scientific Discovery",
    Domain.MULTI_AGENT_RESEARCH: "Multi-Agent Research",
    Domain.KNOWLEDGE_SYSTEMS: "Knowledge Systems",
    Domain.VALIDATION_METHODOLOGY: "Validation Methodology",
    Domain.COGNITIVE_ARCHITECTURES: "Cognitive Architectures",
}


def _render_experiment(e, index: int) -> list[str]:
    return [
        f"  - Experiment {index}: {e.description}",
        f"    - Expected benefit: {e.expected_benefit}",
        f"    - Uncertainty: {e.uncertainty}",
        f"    - Prerequisites: {e.prerequisites}",
        f"    - Validation idea: {e.validation_idea}",
    ]


def _render_signal(s: ResearchSignal) -> str:
    lines = [
        f"### {s.research_id} — {s.title}",
        f"- Authors: {', '.join(s.authors) if s.authors else 'unknown'}",
        f"- Publication: {s.publication} ({s.date})",
        f"- Domain: {_DOMAIN_LABELS.get(s.domain, s.domain)}",
        f"- Evidence level: {s.evidence_level} · Confidence: {s.confidence}",
        f"- Affected projects: {', '.join(s.affected_projects)}",
        f"- Problem addressed: {s.problem_addressed}",
        f"- Main contribution: {s.main_contribution}",
        f"- Architectural relevance: {s.architectural_relevance}",
    ]
    if s.possible_experiments:
        lines.append("- Possible experiments:")
        for i, e in enumerate(s.possible_experiments, start=1):
            lines.extend(_render_experiment(e, i))
    else:
        lines.append("- Possible experiments: none captured")
    lines.append(f"- Recommended action: {s.recommended_action}")
    lines.append("- Evidence:")
    for citation in s.evidence_citations():
        lines.append(f"  - {citation}")
    lines.append(f"- First seen: {s.first_seen} · Last seen: {s.last_seen} · Times seen: {s.times_seen}")
    return "\n".join(lines)


def _group_by_domain(signals: list[ResearchSignal]) -> dict[str, list[ResearchSignal]]:
    grouped: dict[str, list[ResearchSignal]] = {}
    for s in signals:
        grouped.setdefault(s.domain, []).append(s)
    return grouped


def render_daily_brief(
    run_timestamp: str,
    new_signals: list[ResearchSignal],
    updated_signals: list[ResearchSignal],
    discovery_hints_skipped: int = 0,
) -> str:
    lines = [
        "# Daily Research Brief",
        "",
        f"Run: {run_timestamp}",
        "",
        f"{len(new_signals)} new signal(s), {len(updated_signals)} updated signal(s) this run"
        + (f", {discovery_hints_skipped} community discovery hint(s) not registered" if discovery_hints_skipped else "")
        + ".",
        "",
        "This tool is a research opportunity detector, not a literature "
        "summarizer, and not a decision-maker. Every recommended action "
        "below is advisory only - see research-sensor/CONTRACT.md.",
        "",
    ]
    if not new_signals and not updated_signals:
        lines.append("No signals this run.")
        return "\n".join(lines) + "\n"

    if new_signals:
        lines.append("## New Signals")
        lines.append("")
        for domain, group in _group_by_domain(new_signals).items():
            lines.append(f"#### {_DOMAIN_LABELS.get(domain, domain)}")
            lines.append("")
            for s in group:
                lines.append(_render_signal(s))
                lines.append("")

    if updated_signals:
        lines.append("## Updated Signals (new corroborating evidence)")
        lines.append("")
        for s in updated_signals:
            lines.append(_render_signal(s))
            lines.append("")

    return "\n".join(lines) + "\n"


def render_weekly_brief(run_timestamp: str, registry: list[ResearchSignal], window_days: int = 7) -> str:
    now = datetime.fromisoformat(run_timestamp.replace("Z", "+00:00"))
    cutoff = now - timedelta(days=window_days)

    def _in_window(s: ResearchSignal) -> bool:
        try:
            last = datetime.fromisoformat(s.last_seen.replace("Z", "+00:00"))
        except ValueError:
            return False
        return last >= cutoff

    windowed = sorted(
        (s for s in registry if _in_window(s)),
        key=lambda s: (s.domain, s.research_id),
    )

    lines = [
        "# Weekly Research Intelligence Report",
        "",
        f"Run: {run_timestamp} · Window: last {window_days} days",
        "",
        f"{len(windowed)} signal(s) active in this window, across "
        f"{len(registry)} total signal(s) in the registry.",
        "",
    ]
    if not windowed:
        lines.append("No signals active in this window.")
        return "\n".join(lines) + "\n"

    named = [s for s in windowed if s.affected_projects != ["WATCH"]]
    if named:
        top = max(named, key=lambda s: ({"HIGH": 3, "MEDIUM": 2, "LOW": 1, "INSUFFICIENT_EVIDENCE": 0}[s.confidence], len(s.possible_experiments)))
        lines.append(
            f"## Top Research Opportunity this window (for Headquarters to surface, if it chooses)"
        )
        lines.append("")
        lines.append(
            f"{top.research_id} — {top.title} (confidence {top.confidence}, "
            f"{len(top.possible_experiments)} possible experiment(s)). Not an automatic "
            "prioritization - one candidate among the signals below, shown for visibility only."
        )
        lines.append("")

    for domain, group in _group_by_domain(windowed).items():
        lines.append(f"## {_DOMAIN_LABELS.get(domain, domain)}")
        lines.append("")
        for s in group:
            lines.append(_render_signal(s))
            lines.append("")

    watch_only = [s for s in windowed if s.affected_projects == ["WATCH"]]
    if watch_only:
        lines.append(f"## WATCH-only (no named project matched yet): {len(watch_only)} signal(s)")
        lines.append("")
        for s in watch_only:
            lines.append(f"- {s.research_id}: {s.title}")

    return "\n".join(lines) + "\n"
