"""Deterministic, stratified selection of the Run-1 Human Quality Audit
sample. Pure function over already-persisted candidate_incremental
metadata (post_id, query_family, query_id, canonical_url, timestamps) -
never touches post text (there is none in this data to begin with),
never calls the X API, never reads config/queries.json. See
tests/test_audit_safety.py, which makes all three of those a build
failure rather than a promise.
"""

from __future__ import annotations

import math
import random

from .audit_models import AuditSampleEntry

SELECTION_ALGORITHM_VERSION = "0.1"
TARGET_SAMPLE_SIZE = 20
MAX_PER_FAMILY = 3


def compute_effective_cap(family_counts: dict, target: int, base_cap: int) -> int:
    """The per-family cap actually used this run. Equal to `base_cap`
    unless too few families hold any candidates for `base_cap` to reach
    `target` at all - in that case the cap rises just enough to make
    `target` reachable (ceil(target / n_families)), still fully
    deterministic and computed only from family counts, before any draw
    happens. Recorded in the frozen sample file alongside `base_cap` so
    a reader never has to re-derive it."""
    n_families = len(family_counts)
    if n_families == 0:
        return 0
    return max(base_cap, math.ceil(target / n_families))


def _apportion(family_counts: dict, target: int, cap: int) -> dict:
    """Largest-remainder apportionment of `target` slots across
    families, proportional to each family's actual candidate count,
    capped at `cap` per family and at each family's own count.
    Deterministic: families are always processed in name-sorted order
    and remainder ties break alphabetically - never dict iteration
    order, never wall-clock time."""
    families = sorted(family_counts)
    total = sum(family_counts.values())
    if total == 0:
        return {}

    raw = {f: target * family_counts[f] / total for f in families}
    ceiling = {f: min(family_counts[f], cap) for f in families}
    base = {f: min(int(raw[f]), ceiling[f]) for f in families}
    remainder = {f: raw[f] - int(raw[f]) for f in families}

    allocated = sum(base.values())
    order = sorted(families, key=lambda f: (-remainder[f], f))
    max_reachable = sum(ceiling.values())
    idx = 0
    guard = 0
    while allocated < min(target, max_reachable) and guard < len(order) * (target + 1):
        f = order[idx % len(order)]
        if base[f] < ceiling[f]:
            base[f] += 1
            allocated += 1
        idx += 1
        guard += 1
    return base


def select_audit_sample(
    candidates: list,
    *,
    seed: str,
    target: int = TARGET_SAMPLE_SIZE,
    base_max_per_family: int = MAX_PER_FAMILY,
) -> list[AuditSampleEntry]:
    """`candidates` is Run 1's persisted rows already filtered by the
    caller to classification == "candidate_incremental" (dicts or
    objects exposing post_id/query_family/query_id/canonical_url/
    created_at/retrieved_at). Same `candidates` + same `seed` always
    yields the same entries in the same order - this function reads no
    wall-clock time, no environment state, and no post content (there is
    none in the input rows).

    Fewer than `target` may come back if the candidate pool itself is
    smaller than `target` after capping - never filled by relaxing the
    cap silently mid-run; `compute_effective_cap` already decided the
    cap deterministically before any draw."""

    def _get(row, key):
        return row[key] if isinstance(row, dict) else getattr(row, key)

    by_family: dict[str, list] = {}
    for row in candidates:
        by_family.setdefault(_get(row, "query_family"), []).append(row)
    for fam in by_family:
        by_family[fam] = sorted(by_family[fam], key=lambda r: _get(r, "post_id"))

    family_counts = {f: len(rows) for f, rows in by_family.items()}
    cap = compute_effective_cap(family_counts, target, base_max_per_family)
    quota = _apportion(family_counts, target, cap)

    selected: list[AuditSampleEntry] = []
    for fam in sorted(quota):
        q = quota[fam]
        if q <= 0:
            continue
        rng = random.Random(f"{seed}|{fam}")
        drawn = rng.sample(by_family[fam], q)
        for row in drawn:
            selected.append(
                AuditSampleEntry(
                    post_id=_get(row, "post_id"),
                    query_family=_get(row, "query_family"),
                    query_id=_get(row, "query_id"),
                    canonical_url=_get(row, "canonical_url"),
                    created_at=_get(row, "created_at"),
                    retrieved_at=_get(row, "retrieved_at"),
                )
            )

    selected.sort(key=lambda e: e.post_id)
    return selected
