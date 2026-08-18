"""Wraps one already-published CA Anomaly record or one already-published
BCA Candidate record into a Case plus its Claims. Reads plain JSON - never
imports `ca_agents` or `business_candidate_analyst` (see CONTRACT.md and
models.py's ArtifactEnvelope docstring for why: every package in this repo
reads every other package's *data*, never its *code*). This is the same
pattern `business_candidate_analyst/evidence_reader.py` already uses to
read Constraint Archaeology's own files.

READ-ONLY, ALWAYS
    Every function in this module takes an already-loaded dict (or a path
    to open in read mode) and returns new objects. Nothing here ever opens
    a CA or BCA file in a writing mode, and nothing here ever calls back
    into either package's own code. tests/test_safety.py enforces this
    statically, the same way it is already enforced for
    `evidence_reader.py`, `x_signal_probe`, and `constraint_change_
    observatory`.

WRAP, NOT REWRITE
    Every field taken from the source record is either copied through
    verbatim (`source_record_id`, `source_status`, `source_evidence_ids`)
    or reproduced from an existing sibling shape with no new
    interpretation (`Claim` from `DimensionResult`). Nothing is
    recomputed, re-scored, or re-classified.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional, Tuple

from .identity import make_case_id, make_claim_id, stable_evidence_ids
from .models import Case, Claim

CA_SOURCE_SYSTEM = "constraint_archaeology_agents"
CA_RECORD_TYPE = "anomaly"
BCA_SOURCE_SYSTEM = "business_candidate_analyst"
BCA_RECORD_TYPE = "candidate"


def _read_json_list(path: str) -> List[Dict[str, Any]]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"{path} does not contain a JSON list")
    return data


def load_ca_anomalies(anomalies_path: str) -> List[Dict[str, Any]]:
    """Read-only load of Constraint Archaeology's own published snapshot.
    Opens exactly the one file the caller names, in read mode only."""
    return _read_json_list(anomalies_path)


def load_bca_candidates(candidates_path: str) -> List[Dict[str, Any]]:
    """Read-only load of Business Candidate Analyst's own published
    snapshot. Opens exactly the one file the caller names, in read mode
    only."""
    return _read_json_list(candidates_path)


def find_by_id(records: List[Dict[str, Any]], id_field: str, record_id: str) -> Optional[Dict[str, Any]]:
    for r in records:
        if r.get(id_field) == record_id:
            return r
    return None


def wrap_ca_anomaly(anomaly: Dict[str, Any]) -> Tuple[Case, List[Claim]]:
    """Wraps one Constraint Archaeology Anomaly dict (as published in
    `constraint-archaeology-agents/data/anomalies.json`, matching
    `ca_agents.models.Anomaly.to_dict()`'s shape).

    Anomaly carries no per-dimension evidence-status breakdown of its own
    - unlike a BCA Candidate's `dimensions`, an Anomaly's own fields
    (`canonical_pattern`, `hidden_function_class`) are plain descriptive
    strings, not named claims each with their own status/evidence. The
    one place Constraint Archaeology *does* produce that shape is a
    per-anomaly Evaluation (`k1`..`k6`, `mechanism_verdict`,
    `capture_verdict` - `ca_agents.models.Evaluation`), read from
    `latest-evaluations.json` when the caller supplies one. Claims are
    empty when no Evaluation exists yet for this anomaly - that is a
    correct, honest result (an unevaluated anomaly has no claims to wrap
    yet), not a defect to work around by inventing one from descriptive
    fields that were never asserted with their own evidence.
    """
    source_record_id = anomaly["anomaly_id"]
    case_id = make_case_id(CA_SOURCE_SYSTEM, CA_RECORD_TYPE, source_record_id)
    source_evidence_ids = stable_evidence_ids(anomaly.get("observation_ids", []))
    case = Case(
        case_id=case_id,
        source_system=CA_SOURCE_SYSTEM,
        source_record_type=CA_RECORD_TYPE,
        source_record_id=source_record_id,
        source_status=anomaly.get("status", ""),
        derived_from=[source_record_id],
        source_evidence_ids=source_evidence_ids,
    )
    return case, []


_EVALUATION_CLAIM_FIELDS = ("mechanism_verdict", "capture_verdict", "k1", "k2", "k3", "k4", "k5", "k6")


def wrap_ca_evaluation_claims(case_id: str, evaluation: Dict[str, Any]) -> List[Claim]:
    """When a matching `ca_agents.models.Evaluation` exists for this
    anomaly, its `mechanism_verdict`/`capture_verdict`/`k1`..`k6` fields
    are the anomaly's real per-criterion claims (the K1-K6 criteria are
    the Operating Contract's own named checklist -
    `constraint-archaeology-agents/method/OPERATING-CONTRACT.md`). Each
    becomes one Claim, `status` fixed to `"EVALUATED"` (the field's plain
    presence in a published Evaluation - CA's own evaluation step has
    already decided this value, nothing here re-derives it), `evidence`
    copied from the Evaluation's own `evidence_used` list unchanged.
    """
    evidence = stable_evidence_ids(evaluation.get("evidence_used", []))
    claims: List[Claim] = []
    for field_name in _EVALUATION_CLAIM_FIELDS:
        if field_name not in evaluation:
            continue
        claims.append(Claim(
            claim_id=make_claim_id(case_id, field_name),
            case_id=case_id,
            name=field_name,
            status="EVALUATED",
            value=evaluation[field_name],
            evidence=evidence,
            note="from ca_agents.models.Evaluation, evidence_used copied through unchanged",
        ))
    return claims


def wrap_bca_candidate(candidate: Dict[str, Any]) -> Tuple[Case, List[Claim]]:
    """Wraps one Business Candidate Analyst Candidate dict (as published
    in `business-candidate-analyst/data/candidates.json`, matching
    `business_candidate_analyst.models.Candidate.to_dict()`'s shape).

    `dimensions` is already exactly Claim-shaped
    (`DimensionResult.name/status/value/evidence/note`) - each entry
    becomes one Claim with no reinterpretation. An entry with empty
    `evidence` and an empty `note` (both fields absent of content) gets a
    generated `note` stating that fact plainly, so the eventual ledger
    write (validator.py) always has a truthful reason for empty
    provenance to point to - it never fabricates *evidence*, only records,
    honestly, that the source record itself supplied none.
    """
    source_record_id = candidate["candidate_id"]
    case_id = make_case_id(BCA_SOURCE_SYSTEM, BCA_RECORD_TYPE, source_record_id)
    source_evidence_ids = stable_evidence_ids(candidate.get("observation_ids", []))
    case = Case(
        case_id=case_id,
        source_system=BCA_SOURCE_SYSTEM,
        source_record_type=BCA_RECORD_TYPE,
        source_record_id=source_record_id,
        source_status=candidate.get("state", ""),
        derived_from=[source_record_id],
        source_evidence_ids=source_evidence_ids,
    )

    claims: List[Claim] = []
    dimensions = candidate.get("dimensions") or {}
    for name in sorted(dimensions.keys()):
        dim = dimensions[name]
        evidence = stable_evidence_ids(dim.get("evidence", []))
        note = dim.get("note", "") or ""
        if not evidence and not note:
            note = "source DimensionResult carried no evidence and no note"
        claims.append(Claim(
            claim_id=make_claim_id(case_id, name),
            case_id=case_id,
            name=name,
            status=dim.get("status", ""),
            value=dim.get("value"),
            evidence=evidence,
            note=note,
        ))
    return case, claims
