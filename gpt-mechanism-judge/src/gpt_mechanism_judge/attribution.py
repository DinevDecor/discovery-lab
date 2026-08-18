"""Provider attribution wrapper. NOT a ledger, NOT a new envelope system,
NOT a generic provider framework - Stage 2 does not persist anything.
This is one small, frozen dataclass plus two builder functions, wrapping
whatever `MechanismProfile`/`GateDecision` a judge run already produced
with the minimum attribution fields the task requires:

  provider, model, created_at, source_case_ids, source_artifact_ids

`source_case_ids` is a `List[str]`, never a single concatenated string.
An earlier revision of this module passed `gate_pair()`'s two Case ids
through as one synthetic `"<left>|<right>"` string - that is not a valid
Case identity under `case_claim_kernel.identity` (Stage 1 mints exactly
one `case_id` per real source record; nothing anywhere mints a pipe-
joined pseudo-id for a pair), so it has been corrected here: each real
Stage-1 `case_id` is preserved separately, in a sorted (deterministic)
list, never concatenated into a new string that looks like but is not an
identity.

`AttributedAnalysis` deliberately does NOT touch `case_id`/`claim_id`
identity (case_claim_kernel.identity, Stage 1, unmodified) - provider
identity lives entirely on the analysis wrapper, never inside the
semantic identity of the thing being analyzed. Two different providers
analyzing the same real anomaly therefore produce two
`AttributedAnalysis` records that both carry the SAME `source_case_ids`
(proving the claim/case did not change) and DIFFERENT `provider`/`model`
(proving the two analyses are genuinely distinct artifacts) - see
tests/test_attribution.py.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass(frozen=True)
class AttributedAnalysis:
    provider: str
    model: str
    created_at: str
    source_case_ids: List[str]
    source_artifact_ids: List[str]
    analysis_kind: str  # "mechanism_profile" | "same_mechanism_decision"
    analysis: Dict[str, Any]
    model_version: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def attribute_mechanism_profile(profile, *, provider: str, model: str,
                                 source_case_ids: List[str], source_artifact_ids: List[str],
                                 model_version: Optional[str] = None,
                                 created_at: Optional[str] = None) -> AttributedAnalysis:
    """`profile` is a `ca_agents.same_mechanism_gate.MechanismProfile`
    (or anything with the same `.anomaly_id`/dataclass shape) - this
    function does not import that module; it only calls `dataclasses
    .asdict`-compatible access via the object the caller already has,
    keeping this package's only dependency on ca_agents at the call site
    (the acceptance script), never inside this library code.

    `source_case_ids` is sorted here (not by the caller) so identical
    inputs in any order always produce an identical, deterministic list -
    the same discipline `case_claim_kernel.identity.stable_evidence_ids`
    already applies to evidence-id lists.
    """
    from dataclasses import asdict as _asdict
    return AttributedAnalysis(
        provider=provider,
        model=model,
        model_version=model_version,
        created_at=created_at or utc_now_iso(),
        source_case_ids=sorted(dict.fromkeys(source_case_ids)),
        source_artifact_ids=list(source_artifact_ids),
        analysis_kind="mechanism_profile",
        analysis=_asdict(profile),
    )


def attribute_gate_decision(decision, *, provider: str, model: str,
                             source_case_ids: List[str], source_artifact_ids: List[str],
                             model_version: Optional[str] = None,
                             created_at: Optional[str] = None) -> AttributedAnalysis:
    """`decision` is a `ca_agents.same_mechanism_gate.GateDecision`
    (or anything exposing `.to_dict()`), same import-boundary note as
    `attribute_mechanism_profile` above."""
    return AttributedAnalysis(
        provider=provider,
        model=model,
        model_version=model_version,
        created_at=created_at or utc_now_iso(),
        source_case_ids=sorted(dict.fromkeys(source_case_ids)),
        source_artifact_ids=list(source_artifact_ids),
        analysis_kind="same_mechanism_decision",
        analysis=decision.to_dict(),
    )
