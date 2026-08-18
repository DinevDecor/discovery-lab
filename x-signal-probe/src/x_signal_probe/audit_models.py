"""Data shapes for the Run-1 Human Quality Audit.

AuditSampleEntry is the frozen, pre-registered selection - metadata only
(post_id, query_family, query_id, canonical_url, timestamps), the same
fields Run 1's own ProbeObservation already carries minus `classification`
and `text_hash`. `classification` is deliberately dropped here even
though every entry is "candidate_incremental" by construction (that's
how the sample was filtered) - never give the reviewer a field to peek
at, on principle, so this shape stays correct if it's ever reused where
dropping it wouldn't be a no-op.

AuditVerdict is the only thing the review step ever persists - no post
text, no quote, no author identifier, matching Run-1's own
ProbeObservation data-minimization rule. `notes` is documented, not
enforced, as "your own words only" - see audit/README.md.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

RUBRIC_ABCD_VALUES = ("YES", "NO", "UNCLEAR", "UNAVAILABLE")
RUBRIC_E_VALUES = ("YES", "NO", "UNAVAILABLE")


@dataclass
class AuditSampleEntry:
    post_id: str
    query_family: str
    query_id: str
    canonical_url: str
    created_at: str
    retrieved_at: str


@dataclass
class AuditVerdict:
    audit_id: str
    run_id: str
    post_id: str
    query_family: str
    canonical_url: str
    selection_algorithm_version: str
    availability: str  # "AVAILABLE" | "UNAVAILABLE"
    reviewer: str
    review_timestamp: str
    a_genuine_problem_report: str
    b_operational_economic_consequence: str
    c_noise: str
    d_incremental_vs_discovery_lab: str
    e_corroboration_worthy: str
    notes: str = ""


def to_dict(obj) -> dict:
    return asdict(obj)


def unavailable_verdict(
    sample_entry: AuditSampleEntry,
    audit_id: str,
    run_id: str,
    selection_algorithm_version: str,
    timestamp: str,
) -> AuditVerdict:
    """The pre-registered treatment (fixed before any rehydration) of a
    selected post the X API ID-lookup does not return: recorded once,
    immediately, as UNAVAILABLE across every rubric field - never
    silently dropped, never replaced with another post. audit_report.py
    treats UNAVAILABLE as not-YES for every rate calculation, so an
    unavailable post drags rates down rather than shrinking the fixed
    20-post denominator."""
    return AuditVerdict(
        audit_id=audit_id,
        run_id=run_id,
        post_id=sample_entry.post_id,
        query_family=sample_entry.query_family,
        canonical_url=sample_entry.canonical_url,
        selection_algorithm_version=selection_algorithm_version,
        availability="UNAVAILABLE",
        reviewer="",
        review_timestamp=timestamp,
        a_genuine_problem_report="UNAVAILABLE",
        b_operational_economic_consequence="UNAVAILABLE",
        c_noise="UNAVAILABLE",
        d_incremental_vs_discovery_lab="UNAVAILABLE",
        e_corroboration_worthy="UNAVAILABLE",
        notes=(
            "post not returned by the X API ID lookup (deleted/suspended/protected/not found) - "
            "recorded as unavailable, not replaced, per the pre-registered rule in audit/README.md"
        ),
    )
