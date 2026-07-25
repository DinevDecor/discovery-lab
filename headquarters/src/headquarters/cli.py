"""Entry point. Orchestrates one full execution: collect -> drift ->
opportunities -> health -> portfolio -> prioritize -> assign HQ-ID ->
render brief -> write outputs. The only writes anywhere in this module
are the three files below, all inside this tool's own `reports/`
directory — never inside any observed repository. See
tests/test_safety.py."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

from .brief import render_brief
from .collector import collect
from .config import load_config
from .drift import detect_drift
from .history import RunSnapshot, load_history, previous_scores, save_history
from .inconsistency import classify_all
from .opportunity import detect_opportunities
from .portfolio import build_portfolio
from .health import compute_health
from .prioritizer import build_candidates, select_top, to_recommendation
from .recommendation import assign_id, evaluate, load_decisions, load_log, save_log


def run(config_path: Path, reports_dir: Path) -> dict:
    """Runs one full execution and returns a summary dict (also used
    directly by tests, independent of the CLI/file-writing layer)."""
    config = load_config(config_path)
    collected = collect(config)

    drift_findings = detect_drift(collected, config)
    opportunity_findings = detect_opportunities(collected, config)
    inconsistencies = classify_all(drift_findings)
    health = compute_health(collected, drift_findings, config.decision_backlog_threshold_days)

    history_path = reports_dir / "history.json"
    history = load_history(history_path)
    prev_scores = previous_scores(history)
    portfolio = build_portfolio(collected, drift_findings, prev_scores)

    candidates = build_candidates(collected, drift_findings, opportunity_findings)
    top = select_top(candidates)

    log_path = reports_dir / "recommendation-log.json"
    records = load_log(log_path)
    today = datetime.now(timezone.utc).date()

    top_recommendation = None
    other_candidates = candidates
    if top is not None:
        top_candidate, score_value, breakdown = top
        hq_id, records = assign_id(top_candidate, records, today)
        top_recommendation = to_recommendation(top_candidate, hq_id, score_value, breakdown)
        other_candidates = [c for c in candidates if c.key != top_candidate.key]

    decisions_path = reports_dir / "recommendation-decisions.json"
    evaluation = evaluate(records, load_decisions(decisions_path))

    previous_snapshot = history[-1] if history else None

    human_decisions = list(collected.observation.human_decisions)

    brief_text = render_brief(
        health=health,
        portfolio=portfolio,
        top_recommendation=top_recommendation,
        other_candidates=other_candidates,
        drift_findings=drift_findings,
        opportunity_findings=opportunity_findings,
        inconsistencies=inconsistencies,
        human_decisions_required=human_decisions,
        previous_snapshot=previous_snapshot,
        evaluation=evaluation,
        scanned_repos=collected.observation.scanned_repos,
        skipped_repos=collected.observation.skipped_repos,
    )

    overall_pct = None
    try:
        overall_pct = float(health["overall_health"].value.split("%")[0])
    except ValueError:
        overall_pct = None

    new_scores = {p.name: float(p.health_score.rstrip("%")) / 100 for p in portfolio}

    snapshot = RunSnapshot(
        timestamp=datetime.now(timezone.utc).isoformat(),
        overall_health_pct=overall_pct,
        recommendation_backlog=int(health["recommendation_backlog"].value),
        decision_backlog=int(health["decision_backlog"].value),
        project_health_scores=new_scores,
        top_recommendation_hq_id=top_recommendation.hq_id if top_recommendation else None,
    )
    history.append(snapshot)

    return {
        "brief_text": brief_text,
        "records": records,
        "history": history,
        "log_path": log_path,
        "history_path": history_path,
        "top_recommendation": top_recommendation,
        "health": health,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="headquarters")
    parser.add_argument(
        "--config",
        default=str(Path(__file__).resolve().parents[2] / "config.json"),
        help="Path to config.json",
    )
    parser.add_argument(
        "--reports-dir",
        default=str(Path(__file__).resolve().parents[2] / "reports"),
        help="Directory this tool's own outputs are written to (never any other directory)",
    )
    args = parser.parse_args(argv)

    reports_dir = Path(args.reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)  # this tool's own directory only

    result = run(Path(args.config), reports_dir)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    brief_path = reports_dir / f"executive-brief-{timestamp}.md"
    with open(brief_path, "w", encoding="utf-8") as f:
        f.write(result["brief_text"])

    save_log(result["log_path"], result["records"])
    save_history(result["history_path"], result["history"])

    top = result["top_recommendation"]
    print(f"Executive Brief written to: {brief_path}")
    print(f"Overall Health: {result['health']['overall_health'].value}")
    if top:
        print(f"Top recommendation: {top.hq_id} — {top.title} (score {top.score})")
    else:
        print("No candidate recommendation this run.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
