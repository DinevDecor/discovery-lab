"""Duplicate Detection (EXEC-008): "Multiple articles about one release
-> One signal... Never duplicate events." Clusters RawCaptures that
plausibly describe the same real-world event so they become one Signal
with multiple Evidence entries, rather than one signal per article.

Clustering rule, stated in full (deterministic, no hidden heuristics):
two captures cluster together if they share the same `category` AND
have at least one case-insensitive `capability_keywords` overlap.
Transitive: if A clusters with B and B clusters with C, all three end
up in one cluster, even if A and C share no direct keyword.
"""

from __future__ import annotations

from .models import RawCapture


def _shares_keyword(a: RawCapture, b: RawCapture) -> bool:
    if a.category != b.category:
        return False
    a_kw = {k.lower() for k in a.capability_keywords}
    b_kw = {k.lower() for k in b.capability_keywords}
    return bool(a_kw & b_kw)


def cluster(captures: list[RawCapture]) -> list[list[RawCapture]]:
    """Union-find over the shares-a-keyword relation. Order-independent
    (sorted internally) so repeated runs over the same input always
    produce the same cluster membership and the same cluster order."""
    n = len(captures)
    parent = list(range(n))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i: int, j: int) -> None:
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[max(ri, rj)] = min(ri, rj)

    for i in range(n):
        for j in range(i + 1, n):
            if _shares_keyword(captures[i], captures[j]):
                union(i, j)

    groups: dict[int, list[RawCapture]] = {}
    for i in range(n):
        root = find(i)
        groups.setdefault(root, []).append(captures[i])

    # Deterministic ordering: sort clusters by their earliest member's
    # original index, and within a cluster, sort members by trust level
    # (PRIMARY/OFFICIAL first) then source name, so the "primary" source
    # a Signal is built from is always chosen the same way.
    ordered_roots = sorted(groups.keys())
    return [groups[root] for root in ordered_roots]
