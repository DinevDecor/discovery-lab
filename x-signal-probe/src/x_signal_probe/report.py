"""Renders the run's markdown report. Deliberately contains no X post
text or quote anywhere - only counts, canonical URLs, and other
already-persisted, text-free ProbeObservation fields - so the report
carries the same data-minimization guarantee as probe-observations.jsonl."""

from __future__ import annotations

import os


def render(path: str, metrics, observations: list, errors: list, bounds: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lines = [
        "# X Signal Probe run",
        "",
        "Probe-only observations. Not read by, and never promoted into, Constraint "
        "Archaeology, Business Candidate Analyst, or any Claim Ledger - see CONTRACT.md.",
        "",
        "## Bounds used this run",
    ]
    for k, v in bounds.items():
        lines.append(f"- {k}: {v}")

    lines += [
        "",
        "## Metrics",
        f"- posts fetched: {metrics.posts_fetched}",
        f"- unique posts (newly admitted this run): {metrics.unique_posts}",
        f"- cross-run duplicates (already in the ledger from a prior run): {metrics.cross_run_duplicates}",
        f"- retrieval duplicates (repeated within this run): {metrics.retrieval_duplicates}",
        f"- filtered (retweet): {metrics.filtered_retweet}",
        f"- filtered (marketing/spam-like): {metrics.filtered_marketing}",
        f"- already represented by existing sources: {metrics.existing_source_duplicates}",
        f"- genuinely incremental candidates: {metrics.candidates_incremental}",
        f"- API errors: {metrics.api_errors}",
        "- estimated cost (USD): "
        + (
            f"{metrics.estimated_cost_usd}"
            if metrics.estimated_cost_usd is not None
            else "not computed - no cost-per-post configured for this run"
        ),
        "- cost per usable observation (USD): "
        + (
            f"{metrics.cost_per_usable_observation_usd}"
            if metrics.cost_per_usable_observation_usd is not None
            else "n/a"
        ),
        "- cost per incremental observation (USD): "
        + (
            f"{metrics.cost_per_incremental_observation_usd}"
            if metrics.cost_per_incremental_observation_usd is not None
            else "n/a"
        ),
        "",
        f"## Automated signal: {metrics.automated_signal}",
        metrics.automated_signal_reason,
        "",
        "**This is a mechanical label, not a final PASS/FAIL/INSUFFICIENT DATA "
        "verdict.** A genuine conclusion requires a human to review the incremental "
        "candidates below against their live canonical URLs, including whether X was "
        "actually earlier than another independent public source or just more visible.",
        "",
        "## Candidates for independent corroboration",
        "",
        "No post text is stored or shown here by design (data-minimization rule, "
        "CONTRACT.md) - open each canonical URL directly to review the post.",
        "",
    ]

    incremental = [o for o in observations if o.classification == "candidate_incremental"]
    if not incremental:
        lines.append("(none this run)")
    else:
        lines.append("| post_id | canonical_url | query_family | created_at | retrieved_at |")
        lines.append("|---|---|---|---|---|")
        for o in incremental:
            lines.append(
                f"| {o.post_id} | {o.canonical_url} | {o.query_family} | "
                f"{o.created_at} | {o.retrieved_at} |"
            )

    if errors:
        lines += ["", "## Errors"]
        lines += [f"- {e}" for e in errors]

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
