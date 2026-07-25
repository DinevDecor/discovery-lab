"""Executive Brief Generator. One human-readable Markdown report per
run, matching EXEC-004's requested structure. Never prints more than
one recommendation as "the" recommendation — everything else the
Prioritizer scored is listed separately, clearly labeled as not
selected, per the "never Top 10" rule."""

from __future__ import annotations

from .history import RunSnapshot, trend_line
from .models import HealthMetric, PortfolioEntry, Recommendation
from .prioritizer import Candidate


def _confidence_note(value: str) -> str:
    return value


def render_brief(
    health: dict[str, HealthMetric],
    portfolio: list[PortfolioEntry],
    top_recommendation: Recommendation | None,
    other_candidates: list[Candidate],
    drift_findings: list,
    opportunity_findings: list,
    human_decisions_required: list[str],
    previous_snapshot: RunSnapshot | None,
    evaluation: dict,
    scanned_repos: list[str],
    skipped_repos: list[str],
) -> str:
    lines: list[str] = []
    lines.append("# Ecosystem Headquarters — Executive Brief")
    lines.append("")
    lines.append(f"## Overall Health")
    lines.append(f"**{health['overall_health'].value}**")
    lines.append(f"_Formula: {health['overall_health'].formula}_")
    lines.append("")

    lines.append("## Projects")
    for p in portfolio:
        lines.append(f"### {p.name}")
        lines.append(f"- Trend: {p.trend}")
        lines.append(f"- Current State: {p.current_state}")
        lines.append(f"- Purpose: {p.purpose}")
        lines.append(f"- Health Score: {p.health_score}")
        lines.append(f"- Risk Level: {p.risk_level}")
        lines.append(f"- Confidence: {p.confidence}")
        lines.append(f"- Dependencies: {p.dependencies}")
        lines.append(f"- Last Meaningful Progress: {p.last_meaningful_progress}")
        lines.append("")

    lines.append("## Most Important Recommendation")
    if top_recommendation is None:
        lines.append("No candidate recommendation exists this run (no Ledger entries, drift findings, or opportunities were found).")
    else:
        r = top_recommendation
        lines.append(f"**{r.hq_id}**: {r.title}")
        lines.append("")
        lines.append("### Reason")
        lines.append(r.reason)
        lines.append("")
        lines.append("### Evidence")
        if r.evidence:
            for e in r.evidence:
                lines.append(f"- {e.citation()}")
        else:
            lines.append("- (see the source Ledger entry / finding citation above)")
        lines.append("")
        lines.append("### Reasoning (score breakdown)")
        for b in r.score_breakdown:
            lines.append(f"- {b}")
        lines.append(f"- **Total score: {r.score}**")
        lines.append("")
        lines.append("### Expected Impact")
        lines.append(r.expected_impact)
        lines.append("")
        lines.append("### Dependencies")
        lines.append(r.dependencies)
        lines.append("")
        lines.append("### Estimated Confidence")
        lines.append(_confidence_note(r.estimated_confidence))
        lines.append("")
        lines.append("### Estimated Risk")
        lines.append(r.estimated_risk)
    lines.append("")

    lines.append(
        "## Other Candidates Considered (not selected this run — "
        "shown for transparency, not as a second priority list)"
    )
    if other_candidates:
        for c in sorted(other_candidates, key=lambda c: c.key)[:10]:
            lines.append(f"- `{c.key}` — {c.title} ({c.confidence}{', DRAFT opportunity' if c.is_opportunity else ''})")
        if len(other_candidates) > 10:
            lines.append(f"- ... and {len(other_candidates) - 10} more")
    else:
        lines.append("(none — the recommendation above was the only candidate)")
    lines.append("")

    lines.append("## Critical Risks")
    critical = [f for f in drift_findings if getattr(f, "confidence", None) == "MISMATCH"]
    if critical:
        for f in critical:
            lines.append(f"- **{f.title}** ({', '.join(f.affected)}) — {f.description}")
    else:
        lines.append("(none at MISMATCH confidence this run)")
    lines.append("")

    lines.append("## Opportunities (DRAFT — none self-approved)")
    if opportunity_findings:
        for f in opportunity_findings:
            lines.append(f"- **{f.title}** ({', '.join(f.affected)}) — {f.description}")
    else:
        lines.append("(none detected this run)")
    lines.append("")

    lines.append("## Human Decisions Required")
    combined = list(human_decisions_required)
    if top_recommendation is not None:
        combined.append(f"{top_recommendation.hq_id}: {top_recommendation.title}")
    if combined:
        for d in combined:
            lines.append(f"- {d}")
    else:
        lines.append("(none this run)")
    lines.append("")

    lines.append("## Trend (vs previous execution)")
    prev_overall = previous_snapshot.overall_health_pct if previous_snapshot else None
    cur_overall_metric = health["overall_health"].value
    try:
        cur_overall = float(cur_overall_metric.split("%")[0])
    except ValueError:
        cur_overall = None
    lines.append(f"- {trend_line(cur_overall, prev_overall, 'Overall Health')}")
    lines.append("")

    lines.append("## Recommendation Evaluation")
    lines.append(f"- {evaluation['status']}")
    lines.append(f"- Total tracked recommendations: {evaluation['total_recommendations']}")
    if evaluation.get("decisions_recorded"):
        lines.append(f"- Decisions recorded: {evaluation['decisions_recorded']}")
        lines.append(f"- Accepted: {evaluation.get('accepted', 0)} · Implemented: {evaluation.get('implemented', 0)} · Useful: {evaluation.get('useful', 0)} · Obsolete: {evaluation.get('obsolete', 0)} · Incorrect: {evaluation.get('incorrect', 0)}")
    lines.append("")

    lines.append("## Observation Agent Coverage")
    lines.append(f"- Scanned: {', '.join(scanned_repos) if scanned_repos else '(none)'}")
    lines.append(f"- Skipped: {', '.join(skipped_repos) if skipped_repos else '(none)'}")
    lines.append("")

    lines.append(
        "## Metrics"
    )
    for key, m in health.items():
        if key == "overall_health":
            continue
        lines.append(f"- **{m.name}**: {m.value} — _{m.formula}_")
    lines.append("")

    lines.append(
        '_Guiding principle: "The ecosystem grows by finishing high-value '
        'work, not by maximizing the number of active ideas." Headquarters '
        "is advisory only — see CONTRACT.md. It has not modified any "
        "repository._"
    )
    return "\n".join(lines) + "\n"
