"""Computes one run's report metrics from already-classified
ProbeObservations. Never re-classifies anything - classification
(mechanical filters + the three dedupe tiers) has already happened
upstream in probe.py; this module only counts and applies the
documented, deterministic verdict thresholds below.
"""

from __future__ import annotations

from dataclasses import dataclass

# A run with fewer fetched posts than this is treated as too small to
# support any signal judgment at all - INSUFFICIENT DATA is a fully
# valid outcome per CLAUDE.md, not a failure of the probe.
MIN_POSTS_FOR_VERDICT = 30

# PASS_CANDIDATE requires both an absolute floor and a minimum share of
# unique posts, so a single lucky match on a large-enough run cannot
# read as a pass.
MIN_INCREMENTAL_FOR_PASS_CANDIDATE = 3
MIN_INCREMENTAL_RATIO_FOR_PASS_CANDIDATE = 0.03


@dataclass
class RunMetrics:
    posts_fetched: int = 0
    unique_posts: int = 0
    retrieval_duplicates: int = 0
    filtered_retweet: int = 0
    filtered_marketing: int = 0
    existing_source_duplicates: int = 0
    candidates_incremental: int = 0
    cross_run_duplicates: int = 0
    api_errors: int = 0
    estimated_cost_usd: float | None = None
    cost_per_usable_observation_usd: float | None = None
    cost_per_incremental_observation_usd: float | None = None
    automated_signal: str = "INSUFFICIENT_DATA"
    automated_signal_reason: str = ""


def evaluate_run(
    observations: list,
    posts_fetched: int,
    api_errors: int,
    cost_per_post_usd: float | None = None,
    cross_run_duplicates: int = 0,
) -> RunMetrics:
    """`automated_signal` is a mechanical label only - PASS_CANDIDATE,
    FAIL_CANDIDATE, or INSUFFICIENT_DATA - never a final PASS/FAIL. A
    genuine conclusion requires a human to review the listed incremental
    candidates by their canonical_url (spam/marketing false negatives,
    and whether X was actually earlier than another independent public
    source or just more visible) - matching CLAUDE.md's rule that
    model/mechanically generated content is never itself evidence.

    `cross_run_duplicates` counts posts this run re-fetched that already
    had a row in the durable ledger from a prior run (probe.py computes
    this before building `observations`, since a cross-run duplicate
    never becomes a ProbeObservation at all) - never itself a criterion
    of `automated_signal`, purely a truthful count of ledger identity
    already holding.
    """
    m = RunMetrics(posts_fetched=posts_fetched, api_errors=api_errors, cross_run_duplicates=cross_run_duplicates)
    unique: set[str] = set()
    for o in observations:
        unique.add(o.post_id)
        if o.classification == "retrieval_duplicate":
            m.retrieval_duplicates += 1
        elif o.classification == "filtered_retweet":
            m.filtered_retweet += 1
        elif o.classification == "filtered_marketing":
            m.filtered_marketing += 1
        elif o.classification == "existing_source_duplicate":
            m.existing_source_duplicates += 1
        elif o.classification == "candidate_incremental":
            m.candidates_incremental += 1
    m.unique_posts = len(unique)

    usable = m.existing_source_duplicates + m.candidates_incremental
    if cost_per_post_usd is not None:
        m.estimated_cost_usd = round(posts_fetched * cost_per_post_usd, 4)
        if usable:
            m.cost_per_usable_observation_usd = round(m.estimated_cost_usd / usable, 4)
        if m.candidates_incremental:
            m.cost_per_incremental_observation_usd = round(
                m.estimated_cost_usd / m.candidates_incremental, 4
            )

    if posts_fetched < MIN_POSTS_FOR_VERDICT:
        m.automated_signal = "INSUFFICIENT_DATA"
        m.automated_signal_reason = (
            f"only {posts_fetched} posts fetched, below the {MIN_POSTS_FOR_VERDICT}-post "
            "minimum bounded sample this probe treats as large enough for any signal"
        )
    elif (
        m.candidates_incremental >= MIN_INCREMENTAL_FOR_PASS_CANDIDATE
        and m.candidates_incremental / max(1, m.unique_posts) >= MIN_INCREMENTAL_RATIO_FOR_PASS_CANDIDATE
    ):
        m.automated_signal = "PASS_CANDIDATE"
        m.automated_signal_reason = (
            f"{m.candidates_incremental} genuinely incremental candidates out of "
            f"{m.unique_posts} unique posts - requires human corroboration review, not a final PASS"
        )
    else:
        m.automated_signal = "FAIL_CANDIDATE"
        m.automated_signal_reason = (
            f"only {m.candidates_incremental} genuinely incremental candidates out of "
            f"{m.unique_posts} unique posts - mostly duplicate, noise, or already represented "
            "by an existing source"
        )
    return m
