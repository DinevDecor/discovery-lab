"""Data shapes for Stage 3: blind two-provider dispatch.

Two objects only - deliberately not a competing envelope system.
`EvidencePacket` (see packet.py) is the one immutable input both provider
jobs consume. `IndependentAnalysisArtifact` is the one output shape each
provider job produces - one artifact per (run_id, provider), never a
comparison, merge, or combined conclusion (that is explicitly Stage 4's
job, not this one - see CONTRACT.md).

Field set matches the task's own minimum list exactly:

    artifact_id, artifact_type, run_id, source_case_ids, source_artifact_ids,
    provider, model, created_at, protocol_version, analysis

plus two additions the task's own later sections require to be provable:
`input_packet_sha256` (§7/§8: "report the SHA-256 of the exact common
evidence packet"; "input_packet_sha256_claude == input_packet_sha256_gpt")
and `model_version` (optional, same precedent as
`gpt_mechanism_judge.attribution.AttributedAnalysis`).

This is derived from Stage 1's `case_claim_kernel.models.ArtifactEnvelope`
shape where the fields genuinely correspond
(`artifact_id`/`created_at`/`analysis` payload) but is its own dataclass,
not a subclass or an extension of it: an independent analysis is not a
Case and not a Claim, it has different identity rules (see identity.py -
content-independent for Case/Claim, but run_id-and-provider-scoped here,
because a rerun must produce a NEW artifact, never silently overwrite an
old one), and Stage 1's `ArtifactEnvelope.kind` is deliberately closed to
`{"case", "claim"}` (case_claim_kernel/models.py's own `ARTIFACT_KINDS`) -
widening that closed set to fit an unrelated object would be modifying
Stage 1 semantics for no proven incompatibility, which the task
instructions forbid.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

PROTOCOL_VERSION = "0.1.0"

ARTIFACT_TYPE_INDEPENDENT_ANALYSIS = "independent_analysis"

PROVIDER_ANTHROPIC = "anthropic"
PROVIDER_OPENAI = "openai"
KNOWN_PROVIDERS = (PROVIDER_ANTHROPIC, PROVIDER_OPENAI)


@dataclass(frozen=True)
class IndependentAnalysisArtifact:
    artifact_id: str
    run_id: str
    source_case_ids: List[str]
    source_artifact_ids: List[str]
    provider: str
    model: str
    created_at: str
    input_packet_sha256: str
    analysis: Dict[str, Any]
    artifact_type: str = ARTIFACT_TYPE_INDEPENDENT_ANALYSIS
    protocol_version: str = PROTOCOL_VERSION
    model_version: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
