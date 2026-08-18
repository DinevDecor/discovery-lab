"""Orchestration for the local, human-interactive rehydration/review
step. Contains no direct file I/O (see audit_io.py) and no network call
of its own beyond delegating to audit_client.get_posts_by_ids exactly
once - never search_recent, never a second lookup, never a fallback
search. None of the functions below accept a `text`/`post_text`/`quote`
parameter (tests/test_audit_safety.py checks this by signature, not
just by reading the code): rehydrated text lives only in the caller's
(review_audit_sample.py's) local loop variable for one iteration and is
never passed into anything that persists it.
"""

from __future__ import annotations

import datetime as dt

from .audit_client import get_posts_by_ids
from .audit_models import AuditSampleEntry, AuditVerdict, unavailable_verdict


def rehydrate_selected(entries: list[dict], bearer_token: str, *, get_posts_fn=get_posts_by_ids):
    """Exactly one call to the ID-lookup endpoint for every selected id
    - never split, never retried with a different batch, never a second
    endpoint. Returns (found, unavailable) - see audit_client.get_posts_by_ids."""
    ids = [e["post_id"] for e in entries]
    return get_posts_fn(ids, bearer_token)


def record_unavailable(entry: dict, audit_id: str, run_id: str, selection_algorithm_version: str) -> AuditVerdict:
    sample_entry = AuditSampleEntry(
        post_id=entry["post_id"],
        query_family=entry["query_family"],
        query_id=entry["query_id"],
        canonical_url=entry["canonical_url"],
        created_at=entry.get("created_at", ""),
        retrieved_at=entry.get("retrieved_at", ""),
    )
    return unavailable_verdict(
        sample_entry, audit_id, run_id, selection_algorithm_version,
        dt.datetime.now(dt.timezone.utc).isoformat(),
    )


def record_available(
    entry: dict,
    audit_id: str,
    run_id: str,
    selection_algorithm_version: str,
    reviewer: str,
    a: str,
    b: str,
    c: str,
    d: str,
    e: str,
    notes: str,
) -> AuditVerdict:
    return AuditVerdict(
        audit_id=audit_id,
        run_id=run_id,
        post_id=entry["post_id"],
        query_family=entry["query_family"],
        canonical_url=entry["canonical_url"],
        selection_algorithm_version=selection_algorithm_version,
        availability="AVAILABLE",
        reviewer=reviewer,
        review_timestamp=dt.datetime.now(dt.timezone.utc).isoformat(),
        a_genuine_problem_report=a,
        b_operational_economic_consequence=b,
        c_noise=c,
        d_incremental_vs_discovery_lab=d,
        e_corroboration_worthy=e,
        notes=notes,
    )
