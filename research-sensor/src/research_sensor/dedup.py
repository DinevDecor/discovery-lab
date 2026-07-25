"""Duplicate Policy (EXEC-010): "One research idea -> One research
signal. Multiple papers supporting the same idea become supporting
evidence." This differs in kind from reality-sensor's own duplicate
detection (which clusters papers/articles reporting the *same event*)
- here the predicate is "propose or support the same underlying
research idea," approximated the same deterministic way: same domain
plus at least one shared idea_keyword, transitive.

Independently reimplemented pattern, not shared code.
"""

from __future__ import annotations

from .models import RawPaperCapture


def _shares_idea(a: RawPaperCapture, b: RawPaperCapture) -> bool:
    if a.domain != b.domain:
        return False
    a_kw = {k.lower() for k in a.idea_keywords}
    b_kw = {k.lower() for k in b.idea_keywords}
    return bool(a_kw & b_kw)


def cluster(captures: list[RawPaperCapture]) -> list[list[RawPaperCapture]]:
    """Union-find over the shares-an-idea relation. Deterministic
    ordering so repeated runs over the same input always produce the
    same cluster membership and order."""
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
            if _shares_idea(captures[i], captures[j]):
                union(i, j)

    groups: dict[int, list[RawPaperCapture]] = {}
    for i in range(n):
        root = find(i)
        groups.setdefault(root, []).append(captures[i])

    ordered_roots = sorted(groups.keys())
    return [groups[root] for root in ordered_roots]
