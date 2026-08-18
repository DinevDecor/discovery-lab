"""Tier 1 of the probe's dedupe: duplicate retrieval - the same X post
found by more than one pre-registered query within a single run.

Deliberately separate from existing_sources.py (tier 2: the same
underlying problem already present in Discovery Lab via a different
source/URL) and from "genuinely incremental" classification (tier 3).
Conflating these tiers is exactly what CLAUDE.md's "similarity is not
same mechanism" / "different text is not independent evidence" rules
exist to prevent - so they stay three separate, explicit outcomes.
"""

from __future__ import annotations


def mark_retrieval_duplicates(raw_posts: list) -> dict[int, bool]:
    """Returns {index: True} for every raw_post whose post_id already
    appeared earlier in `raw_posts`, regardless of which query found it.
    The first occurrence of a post_id is never marked - it stays
    eligible for the downstream filters/existing-source checks; only
    later repeats of the same post_id are retrieval duplicates."""
    seen: set[str] = set()
    dup: dict[int, bool] = {}
    for i, p in enumerate(raw_posts):
        if p.post_id in seen:
            dup[i] = True
        else:
            seen.add(p.post_id)
    return dup
