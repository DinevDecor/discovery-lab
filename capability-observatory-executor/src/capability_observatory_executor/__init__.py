"""External Capture Executor for C3 (Reality Observatory Slice 03).

FETCH only. This package never analyzes prices, detects trends, creates
Findings, decides identity continuity, calls Constraint Archaeology, or
infers business opportunities -- that discipline is enforced by what this
package's modules are allowed to import, not just by convention (see
tests/test_safety.py).

Structurally separate from capability-observatory/src/capability_observatory/:
that package's own tests/test_safety.py forbids any network client inside
it, by design, so it can stay easy to reason about as pure
validate-and-record logic. Network calls belong here instead, in the one
place they are allowed to exist. This package writes nothing to
capability-observatory/data/*.jsonl directly -- every capture flows through
the existing, unmodified capability_observatory.capture_intake /
run_capability_observatory.py process path.
"""
