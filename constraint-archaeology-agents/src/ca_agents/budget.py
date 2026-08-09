"""Source-balanced capture-budget allocation.

The daily sensor budget is bounded (default 80 - see run_daily.py). Before
this module existed, that bound was applied by slicing the concatenated,
source-order list of every collector's output: `captures[:80]`. Sources are
collected in `config/sources.json` order (HN, Lobsters, DEV x3, Reddit x5,
Product Hunt, Discourse x5), and HN(40) + Lobsters(30) + one DEV tag(25)
alone already exceeds 80 - so every source listed after them, including
every run since Product Hunt and Discourse were added, never reached the
sensor at all, regardless of whether their own fetch succeeded. Their
historical zero-observation count was starvation, not a signal-quality
finding.

`allocate_by_source` replaces the slice with a round-robin draw across
sources: one capture from each source with remaining supply, in turn, until
the budget is spent or every source is drained. This guarantees no source
can consume the budget before every other reachable source has had an equal
number of turns - independent of fetch volume, config order, popularity, or
content. Order *within* a source is preserved exactly as its collector
returned it (newest-first for every collector in this package).
"""

from __future__ import annotations

from collections import deque
from typing import TypeVar

T = TypeVar("T")


def allocate_by_source(
    captures_by_source: "dict[str, list[T]]",
    budget: int,
) -> "list[T]":
    """Round-robin admission across sources, bounded by `budget`.

    Deterministic: with S sources holding items and budget >= S, every
    source is admitted at least floor(budget/S) items and at most one more
    than any other source at any point in the process - no source can ever
    be more than one turn ahead of another. If budget < S, the sources first
    in iteration order get one turn before the budget runs out; there is no
    way to give every source a turn when there are fewer slots than sources,
    but no single source can claim more than its own single turn's worth
    before the others have had theirs.
    """
    rotation = deque(
        (name, deque(items)) for name, items in captures_by_source.items() if items
    )
    admitted: list[T] = []
    while rotation and len(admitted) < budget:
        name, queue = rotation.popleft()
        admitted.append(queue.popleft())
        if queue:
            rotation.append((name, queue))
    return admitted
