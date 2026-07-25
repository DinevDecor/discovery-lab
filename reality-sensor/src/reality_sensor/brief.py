"""Renders the two human-readable reports EXEC-008's Headquarters
Interface section names: the Daily AI Reality Brief (this run's
signals) and the Weekly AI Intelligence Brief (everything in the
registry last seen within the last 7 days). The registry itself -
signal-registry.json - is the machine-readable artifact; these two
briefs are read-only renderings of it, never a second source of truth.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from .models import Category, Signal

_CATEGORY_LABELS = {
    Category.FOUNDATION_MODEL_RELEASES: "Foundation Model Releases",
    Category.AGENT_INFRASTRUCTURE: "Agent Infrastructure",
    Category.DEVELOPER_PLATFORMS: "Developer Platforms",
    Category.RESEARCH: "Research",
}


def _render_signal(s: Signal) -> str:
    lines = [
        f"### {s.signal_id} — {s.affected_capability}",
        f"- Source: {s.source} ({s.source_trust})",
        f"- Category: {_CATEGORY_LABELS.get(s.category, s.category)}",
        f"- Affected projects: {', '.join(s.affected_projects)}",
        f"- Confidence: {s.confidence} · Urgency: {s.urgency}",
        f"- Summary: {s.summary}",
        f"- Practical impact: {s.practical_impact or 'INSUFFICIENT_EVIDENCE — not yet assessed'}",
        f"- Recommended action: {s.recommended_action}",
        "- Evidence:",
    ]
    for citation in s.evidence_citations():
        lines.append(f"  - {citation}")
    lines.append(f"- First seen: {s.first_seen} · Last seen: {s.last_seen} · Times seen: {s.times_seen}")
    return "\n".join(lines)


def _group_by_category(signals: list[Signal]) -> dict[str, list[Signal]]:
    grouped: dict[str, list[Signal]] = {}
    for s in signals:
        grouped.setdefault(s.category, []).append(s)
    return grouped


def render_daily_brief(run_timestamp: str, new_signals: list[Signal], updated_signals: list[Signal]) -> str:
    lines = [
        "# Daily AI Reality Brief",
        "",
        f"Run: {run_timestamp}",
        "",
        f"{len(new_signals)} new signal(s), {len(updated_signals)} updated signal(s) this run.",
        "",
        "This tool is a sensor, not a decision-maker. Every recommended "
        "action below is advisory only - see reality-sensor/CONTRACT.md.",
        "",
    ]
    if not new_signals and not updated_signals:
        lines.append("No signals this run.")
        return "\n".join(lines) + "\n"

    if new_signals:
        lines.append("## New Signals")
        lines.append("")
        for category, group in _group_by_category(new_signals).items():
            lines.append(f"#### {_CATEGORY_LABELS.get(category, category)}")
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


def render_weekly_brief(run_timestamp: str, registry: list[Signal], window_days: int = 7) -> str:
    now = datetime.fromisoformat(run_timestamp.replace("Z", "+00:00"))
    cutoff = now - timedelta(days=window_days)

    def _in_window(s: Signal) -> bool:
        try:
            last = datetime.fromisoformat(s.last_seen.replace("Z", "+00:00"))
        except ValueError:
            return False
        return last >= cutoff

    windowed = sorted(
        (s for s in registry if _in_window(s)),
        key=lambda s: (s.category, s.signal_id),
    )

    lines = [
        "# Weekly AI Intelligence Brief",
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

    for category, group in _group_by_category(windowed).items():
        lines.append(f"## {_CATEGORY_LABELS.get(category, category)}")
        lines.append("")
        for s in group:
            lines.append(_render_signal(s))
            lines.append("")

    watch_only = [s for s in windowed if s.affected_projects == ["WATCH"]]
    if watch_only:
        lines.append(f"## WATCH-only (no named project matched yet): {len(watch_only)} signal(s)")
        lines.append("")
        for s in watch_only:
            lines.append(f"- {s.signal_id}: {s.affected_capability}")

    return "\n".join(lines) + "\n"
