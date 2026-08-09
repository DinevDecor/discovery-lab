"""Cross-source / crosspost duplicate detection.

Product Hunt, individual Discourse forums, HN, DEV, Lobsters and Reddit must
never be counted as independent evidence just because their URLs differ - the
same product launch, announcement, or story reposted across communities is
ONE event, not several. This module groups Captures that are the same
underlying story so memory.py's independent-source counting can tell a
crosspost apart from a genuinely separate witness.

This is deliberately NOT the same-mechanism gate. The gate decides whether
two DIFFERENT reported failures share a repair; this module decides whether
two captures are the SAME reported event republished elsewhere. Neither one
substitutes for the other, and this module never merges anomalies or invokes
a judge - it is a pure, offline function over Capture.url/title/source.
"""

from __future__ import annotations

import hashlib
import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from .models import Capture

_TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "ref", "referrer", "source", "fbclid", "gclid", "mc_cid", "mc_eid",
}

_TITLE_TOKEN = re.compile(r"[a-z0-9]{3,}")

# Below this token-Jaccard similarity, two titles are not treated as the same
# story. Chosen high on purpose: this layer's false-positive cost (silently
# discarding a genuinely independent source) is worse than its false-negative
# cost (an occasional missed crosspost that same-source clustering may still
# catch later on pain-text similarity).
DEFAULT_TITLE_THRESHOLD = 0.72


def canonical_url(url: str) -> str:
    """Normalizes a URL so trivial differences (www., trailing slash,
    tracking params, http vs https) don't defeat duplicate detection."""
    if not url:
        return ""
    try:
        parts = urlsplit(url.strip())
    except ValueError:
        return url.strip().lower()
    if not parts.netloc:
        return url.strip().lower()
    netloc = parts.netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    path = parts.path.rstrip("/")
    kept = sorted(
        (k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
        if k.lower() not in _TRACKING_PARAMS
    )
    query = urlencode(kept)
    return urlunsplit(("https", netloc, path, query, ""))


def _title_tokens(title: str) -> set[str]:
    return set(_TITLE_TOKEN.findall((title or "").lower()))


def _title_similarity(a: str, b: str) -> float:
    ta, tb = _title_tokens(a), _title_tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def assign_story_groups(
    captures: list[Capture],
    title_threshold: float = DEFAULT_TITLE_THRESHOLD,
) -> dict[int, str]:
    """Returns {index_in_captures: group_id} for every capture that shares
    its story with at least one other capture in the list. Captures with no
    detected duplicate are omitted - callers should treat a missing entry as
    "unique story", never as an error.

    Two captures group together when:
      - their canonical URLs match (same page, any source), or
      - their titles are near-duplicate (token Jaccard >= title_threshold)
        AND they come from different sources.

    Same-source near-duplicate titles are deliberately left alone here - a
    forum legitimately having two similar threads is not a crosspost, and
    collapsing them is same-mechanism/clustering's job, not this layer's.

    Deterministic: group_id is a stable hash of the group's sorted
    canonical URLs/titles, independent of input order or wall-clock time.
    """
    n = len(captures)
    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)

    canon = [canonical_url(c.url) for c in captures]

    by_canon: dict[str, int] = {}
    for i, cu in enumerate(canon):
        if not cu:
            continue
        if cu in by_canon:
            union(i, by_canon[cu])
        else:
            by_canon[cu] = i

    for i in range(n):
        for j in range(i + 1, n):
            if captures[i].source == captures[j].source:
                continue
            if find(i) == find(j):
                continue
            if _title_similarity(captures[i].title, captures[j].title) >= title_threshold:
                union(i, j)

    groups: dict[int, list[int]] = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(i)

    result: dict[int, str] = {}
    for members in groups.values():
        if len(members) == 1:
            continue
        keys = sorted(canon[i] or captures[i].title.strip().lower() for i in members)
        group_id = "STORY-" + hashlib.sha256("|".join(keys).encode("utf-8")).hexdigest()[:12]
        for i in members:
            result[i] = group_id
    return result
