"""Data shapes for the CASE/CLAIM identity kernel.

Phase 0 (`docs/architecture/reality-observatory-v0.1.md` audit, see
`case-claim-kernel/README.md` for the pointer) found that every existing
identity in this repo - `anomaly_id`, `candidate_id`, `record_id`,
`panel_item_id` - is local to one package. Nothing spans packages. This
module adds exactly the two objects Phase 0 concluded were missing, and
nothing else:

  Case    the outer, stable container for one real-world situation a
          sensor already produced a record about (one Constraint
          Archaeology Anomaly, one Business Candidate Analyst Candidate).
  Claim   one atomic, independently-checkable assertion living inside a
          Case - directly modelled on `business_candidate_analyst.models
          .DimensionResult`, which Phase 0 identified as the existing
          precedent for exactly this shape (name/status/value/evidence).

A Case is not a Claim. A Claim is not an analysis (no analysis exists
yet - Stage 1 does not add one). Nothing here decides, judges, merges,
or infers identity across two different source records - see
`identity.py`'s docstring for why that stays out of scope by
construction, not just by convention.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

KERNEL_VERSION = "0.1.0"

# The only two source systems Stage 1 wraps - both already real, already
# running, already producing the exact records read here. Extending this
# tuple to a new source system is a Stage-1-shaped change (wrap, don't
# rewrite); it is not itself a reason to add a new kernel version.
SOURCE_SYSTEMS = ("constraint_archaeology_agents", "business_candidate_analyst")

CASE = "case"
CLAIM = "claim"
ARTIFACT_KINDS = (CASE, CLAIM)

# Mirrors findings_ledger.Finding.origin exactly, and for the same reason
# stated there: "Findings are derived; origin must be 'generated'. Raw
# evidence does not belong in this ledger." A Case/Claim wrapper is always
# a derived record (it is never itself a Capture or an Observation), so it
# is always "generated" - this is a statement about "derived vs raw", not
# about whether a model produced it. Stage 1 involves no model call at
# all; the kernel is a pure deterministic function of already-published
# CA/BCA data.
ORIGIN_GENERATED = "generated"


@dataclass(frozen=True)
class Case:
    """Wraps exactly one already-published source record - one CA
    Anomaly, or one BCA Candidate - unchanged. Never a merge of two
    source records; never inferred from similarity. See identity.py.
    """
    case_id: str
    source_system: str
    source_record_type: str
    source_record_id: str
    source_status: str
    # The identifier(s) this Case is directly derived from - here always
    # exactly [source_record_id], matching findings_ledger's own
    # derived_from discipline: "references records actually used."
    derived_from: List[str]
    # Read-through copy of whatever evidence/observation ids the source
    # record itself already lists (Anomaly.observation_ids /
    # Candidate.observation_ids) - copied verbatim, never re-interpreted,
    # so the provenance chain back to the original Capture/Observation
    # stays inspectable without re-opening the source file.
    source_evidence_ids: List[str] = field(default_factory=list)
    kernel_version: str = KERNEL_VERSION

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Claim:
    """One atomic assertion inside a Case. Directly modelled on
    `DimensionResult` (BCA) / `RearchitectureField` (BCA Mode B): a named
    field, a status, a value, and the evidence actually consulted for it
    - nothing added, nothing collapsed.

    `claim_id` is a function of (case_id, name) only - never of `status`/
    `value`/`evidence` - so a Claim's identity survives a later re-run
    seeing revised content for the same named dimension. Content drift is
    expected and tracked by the ledger's append-only history, not by a
    changing id (case_claim_kernel/ledger.py).
    """
    claim_id: str
    case_id: str
    name: str
    status: str
    value: Any
    evidence: List[str] = field(default_factory=list)
    note: str = ""
    kernel_version: str = KERNEL_VERSION

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ArtifactEnvelope:
    """The one neutral wire shape every Case and every Claim is persisted
    through. Deliberately mirrors `ca_agents.findings_ledger.Finding`'s
    envelope (`finding_id, kind, recorded_at, derived_from, analyst,
    analyst_version, origin, payload`) field-for-field, because Phase 0
    found that shape already proven across four independent ledgers in
    this repo - but this module does not import findings_ledger.py: every
    package in this repo reads every other package's *data*, never its
    *code* (see `constraint_change_observatory/CONTRACT.md`'s "Zero
    import dependency" rule, which this package holds itself to as well -
    enforced here by tests/test_safety.py). This is a parallel, separately
    -owned adoption of the same envelope discipline, not a dependency on
    it - the same relationship `constraint_change_observatory/schema.py`
    already documents for its own `supersedes` field.

    `producer.provider` / `producer.model` (named in the Phase 0 report,
    section 6, as necessary future fields) are deliberately NOT present
    here. Stage 1 makes no model call and dispatches no analysis - adding
    those fields now would be exactly the "invent a field because it
    looks architecturally elegant" mistake the task instructions forbid.
    `analyst` names the deterministic tool that produced this envelope,
    the same way `Finding.analyst` already does for `same_mechanism_gate`
    or `anomaly_clusterer` - a tool identity, not a model identity.
    """
    artifact_id: str
    kind: str
    recorded_at: str
    derived_from: List[str]
    analyst: str
    analyst_version: str
    payload: Dict[str, Any]
    origin: str = ORIGIN_GENERATED

    def to_dict(self) -> Dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "kind": self.kind,
            "recorded_at": self.recorded_at,
            "derived_from": list(self.derived_from),
            "analyst": self.analyst,
            "analyst_version": self.analyst_version,
            "origin": self.origin,
            "payload": self.payload,
        }
