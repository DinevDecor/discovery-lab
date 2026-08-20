"""CLI entrypoint for one bounded X Signal Probe run.

Entirely separate from run_daily_pipeline.py - never invoked by it,
never invokes it. Prints only a one-line JSON summary (counts and the
automated_signal label); never prints the bearer token or any post
text, so a workflow log can never leak either even if something upstream
mishandles output.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from x_signal_probe import client, probe  # noqa: E402

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(ROOT)

DEFAULT_EXISTING_SOURCES = [
    os.path.join(REPO_ROOT, "constraint-archaeology-agents", "data", "observations.jsonl"),
    os.path.join(REPO_ROOT, "capability-observatory", "data", "observations.jsonl"),
]


def main() -> None:
    p = argparse.ArgumentParser(description="X Signal Probe - bounded, read-only, probe-only run.")
    p.add_argument("--queries", default=os.path.join(ROOT, "config", "queries.json"))
    p.add_argument("--data-dir", default=os.path.join(ROOT, "data"))
    p.add_argument("--reports-dir", default=os.path.join(ROOT, "reports"))
    p.add_argument("--max-results-per-query", type=int, default=client.DEFAULT_MAX_RESULTS_PER_QUERY)
    p.add_argument("--max-pages-per-query", type=int, default=client.DEFAULT_MAX_PAGES_PER_QUERY)
    p.add_argument("--max-posts-per-run", type=int, default=200)
    p.add_argument("--max-retries", type=int, default=client.DEFAULT_MAX_RETRIES)
    p.add_argument("--cost-per-post-usd", type=float, default=None)
    args = p.parse_args()

    try:
        bearer_token = client.get_bearer_token()
    except client.MissingSecretError as e:
        print(json.dumps({"status": "MISSING_SECRET", "error": str(e)}))
        sys.exit(1)

    result = probe.run_probe(
        queries_path=args.queries,
        bearer_token=bearer_token,
        data_dir=args.data_dir,
        reports_dir=args.reports_dir,
        existing_source_paths=DEFAULT_EXISTING_SOURCES,
        max_results_per_query=args.max_results_per_query,
        max_pages_per_query=args.max_pages_per_query,
        max_posts_per_run=args.max_posts_per_run,
        max_retries=args.max_retries,
        cost_per_post_usd=args.cost_per_post_usd,
    )
    m = result["metrics"]
    print(
        json.dumps(
            {
                "status": "OK",
                "posts_fetched": m.posts_fetched,
                "unique_posts": m.unique_posts,
                "cross_run_duplicates": m.cross_run_duplicates,
                "candidates_incremental": m.candidates_incremental,
                "automated_signal": m.automated_signal,
                "errors": len(result["errors"]),
                "report_path": result["report_path"],
            }
        )
    )


if __name__ == "__main__":
    main()
