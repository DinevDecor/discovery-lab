"""Orchestrates one bounded X Signal Probe run: fetch -> cross-run
identity check -> mechanical filters -> three-tier dedupe/classification
-> persist ProbeObservations (reference/provenance only, no post text)
-> render report.

`probe-observations.jsonl` is a durable, append-only ledger keyed by the
real X post_id: `_load_ledgered_post_ids` reads every post_id already
recorded there before this run writes anything, and any post fetched
again in a later run - the same real X post_id, exact string match,
never a fuzzy/title-based match - is counted as a cross-run duplicate
and never gets a second row. One X post has exactly one row in the
ledger, ever, across every run that has ever found it.

This module and report.py are the only ones in this package that open a
file in a writing mode (enforced by tests/test_safety.py). This module
is the only one that ever holds a RawPost's `text` field - it is read
here for classification and
then discarded; it is never written to `probe-observations.jsonl`, the
report, or anywhere else (tests/test_secret_never_persisted.py proves
this dynamically for both the bearer token and post text).
"""

from __future__ import annotations

import datetime as dt
import json
import os

from . import client, dedupe, evaluator, existing_sources, filters, report
from .models import ProbeObservation, RawPost, canonical_url, text_hash, to_dict

PROBE_VERSION = "0.1"


def _load_queries(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        cfg = json.load(f)
    return cfg["queries"]


def _load_ledgered_post_ids(obs_path: str) -> set[str]:
    """Every post_id already recorded in the durable ledger, from any
    previous run. Exact string match only on the real X post_id - never
    fuzzy, never based on text/title similarity. A post_id in this set
    is never written to the ledger again, regardless of what this run's
    filters/classification would otherwise call it: the ledger holds at
    most one row per distinct post_id, ever."""
    if not os.path.exists(obs_path):
        return set()
    ids: set[str] = set()
    with open(obs_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            pid = row.get("post_id")
            if pid:
                ids.add(pid)
    return ids


def run_probe(
    *,
    queries_path: str,
    bearer_token: str,
    data_dir: str,
    reports_dir: str,
    existing_source_paths: list[str],
    max_results_per_query: int = client.DEFAULT_MAX_RESULTS_PER_QUERY,
    max_pages_per_query: int = client.DEFAULT_MAX_PAGES_PER_QUERY,
    max_posts_per_run: int = 200,
    max_retries: int = client.DEFAULT_MAX_RETRIES,
    cost_per_post_usd: float | None = None,
    now: dt.datetime | None = None,
    transport=None,
    sleep_fn=None,
) -> dict:
    queries = _load_queries(queries_path)
    now_dt = now or dt.datetime.now(dt.timezone.utc)
    now_ts = now_dt.isoformat()

    fetch_kwargs = {}
    if transport is not None:
        fetch_kwargs["transport"] = transport
    if sleep_fn is not None:
        fetch_kwargs["sleep_fn"] = sleep_fn

    raw_posts: list[RawPost] = []
    errors: list[str] = []

    for q in queries:
        if len(raw_posts) >= max_posts_per_run:
            break
        try:
            items = client.search_recent(
                q["query"],
                bearer_token,
                max_results=max_results_per_query,
                max_pages=max_pages_per_query,
                max_retries=max_retries,
                **fetch_kwargs,
            )
        except client.XApiError as e:
            errors.append(f"{q['query_id']}: {e}")
            continue

        for item in items:
            if len(raw_posts) >= max_posts_per_run:
                break
            ref_types = tuple(r.get("type", "") for r in (item.get("referenced_tweets") or []))
            text = item.get("text", "")
            raw_posts.append(
                RawPost(
                    post_id=str(item.get("id", "")),
                    text=text,
                    created_at=item.get("created_at", ""),
                    retrieved_at=now_ts,
                    query_id=q["query_id"],
                    query_family=q["family"],
                    is_retweet=filters.is_retweet(text, ref_types),
                )
            )

    posts_fetched = len(raw_posts)
    obs_path = os.path.join(data_dir, "probe-observations.jsonl")
    already_ledgered = _load_ledgered_post_ids(obs_path)
    retrieval_dups = dedupe.mark_retrieval_duplicates(raw_posts)
    existing = existing_sources.load_existing_pain_texts(existing_source_paths)

    observations: list[ProbeObservation] = []
    cross_run_duplicates = 0
    for i, p in enumerate(raw_posts):
        if p.post_id in already_ledgered:
            # Already has exactly one row in the durable ledger from a
            # prior run - never re-recorded, regardless of what this
            # run's filters would otherwise classify it as.
            cross_run_duplicates += 1
            continue

        matched = ""
        if i in retrieval_dups:
            classification = "retrieval_duplicate"
        elif p.is_retweet:
            classification = "filtered_retweet"
        elif filters.is_marketing_like(p.text):
            classification = "filtered_marketing"
        else:
            matched = existing_sources.find_existing_match(p.text, existing)
            classification = "existing_source_duplicate" if matched else "candidate_incremental"

        observations.append(
            ProbeObservation(
                source="x",
                post_id=p.post_id,
                canonical_url=canonical_url(p.post_id),
                created_at=p.created_at,
                retrieved_at=p.retrieved_at,
                query_id=p.query_id,
                query_family=p.query_family,
                text_hash=text_hash(p.text),
                probe_version=PROBE_VERSION,
                api_version=client.API_VERSION,
                classification=classification,
                matched_existing_observation_id=matched,
            )
        )

    os.makedirs(data_dir, exist_ok=True)
    with open(obs_path, "a", encoding="utf-8") as f:
        for o in observations:
            f.write(json.dumps(to_dict(o), ensure_ascii=False) + "\n")

    metrics = evaluator.evaluate_run(
        observations, posts_fetched, len(errors), cost_per_post_usd,
        cross_run_duplicates=cross_run_duplicates,
    )

    bounds = {
        "queries_configured": len(queries),
        "max_results_per_query": max_results_per_query,
        "max_pages_per_query": max_pages_per_query,
        "max_posts_per_run": max_posts_per_run,
        "max_retries_per_query": max_retries,
    }

    stamp = now_dt.date().isoformat()
    report_path = os.path.join(reports_dir, f"x-signal-probe-{stamp}.md")
    report.render(report_path, metrics, observations, errors, bounds)

    return {
        "observations": observations,
        "metrics": metrics,
        "errors": errors,
        "obs_path": obs_path,
        "report_path": report_path,
        "bounds": bounds,
    }
