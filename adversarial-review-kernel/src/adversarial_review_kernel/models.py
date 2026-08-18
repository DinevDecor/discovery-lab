"""Data shapes for Stage 4: deterministic disagreement extraction,
cross-falsification, and deterministic judgment.

Four objects, each doing exactly one job:

  Disagreement           one field where two IndependentAnalysisArtifacts
                          differ - produced by disagree.py, a pure diff,
                          never a semantic judgment (§3).
  FalsificationFinding    one Falsifier's classification of one field of
                          the ANALYSIS IT WAS SHOWN (never its own prior
                          analysis - see falsify.py) against the source
                          evidence only (§5).
  FalsificationArtifact   one Falsifier run's full output - one critic
                          provider, one target analysis, many findings.
  JudgmentArtifact        the one deterministic decision, computed from
                          the above three - see judgment.py. Never
                          produced by a model call.

Compared fields are exactly the task's own minimum list (§3) -
`anomaly_id` and `evidence_count` are excluded: `anomaly_id` is identity,
not content, and `evidence_count` is copied from the shared
EvidencePacket by both providers by construction, so it can never differ.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

PROTOCOL_VERSION = "0.1.0"

COMPARED_FIELDS = (
    "hidden_function", "inputs", "outputs", "carrier",
    "failure_class", "failure_mechanism", "repair", "confidence",
)

# --- Falsifier classification vocabulary (task §5/§6) ---
SUPPORTED_BY_SOURCE = "SUPPORTED_BY_SOURCE"
CHALLENGED_BY_SOURCE = "CHALLENGED_BY_SOURCE"
INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
SCHEMA_AMBIGUITY = "SCHEMA_AMBIGUITY"
CLASSIFICATIONS = (SUPPORTED_BY_SOURCE, CHALLENGED_BY_SOURCE, INSUFFICIENT_DATA, SCHEMA_AMBIGUITY)

# --- Judgment status vocabulary (task §7) ---
ADVANCE = "ADVANCE"
WATCH = "WATCH"
REJECT = "REJECT"
JUDGMENT_STATUSES = (ADVANCE, WATCH, REJECT)

ARTIFACT_TYPE_FALSIFICATION = "falsification"
ARTIFACT_TYPE_JUDGMENT = "judgment"

PROVIDER_ANTHROPIC = "anthropic"
PROVIDER_OPENAI = "openai"


@dataclass(frozen=True)
class Disagreement:
    """One field where the two independent analyses differ. Pure fact,
    not a verdict - see disagree.py's own docstring for why this
    dataclass has no `material`/`classification` field at all."""
    field: str
    claude_value: Any
    gpt_value: Any
    claude_artifact_id: str
    gpt_artifact_id: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class FalsificationFinding:
    field: str
    target_analysis_artifact_id: str
    classification: str
    reason: str
    source_artifact_ids: List[str]
    material: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class FalsificationArtifact:
    artifact_id: str
    run_id: str
    critic_provider: str
    critic_model: str
    target_artifact_id: str
    source_case_ids: List[str]
    input_packet_sha256: str
    findings: List[FalsificationFinding]
    created_at: str
    artifact_type: str = ARTIFACT_TYPE_FALSIFICATION
    protocol_version: str = PROTOCOL_VERSION

    def to_dict(self) -> Dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "run_id": self.run_id,
            "critic_provider": self.critic_provider,
            "critic_model": self.critic_model,
            "target_artifact_id": self.target_artifact_id,
            "source_case_ids": list(self.source_case_ids),
            "input_packet_sha256": self.input_packet_sha256,
            "findings": [f.to_dict() if isinstance(f, FalsificationFinding) else f for f in self.findings],
            "created_at": self.created_at,
            "artifact_type": self.artifact_type,
            "protocol_version": self.protocol_version,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "FalsificationArtifact":
        findings = [FalsificationFinding(**f) if not isinstance(f, FalsificationFinding) else f
                    for f in data.get("findings", [])]
        return FalsificationArtifact(
            artifact_id=data["artifact_id"], run_id=data["run_id"],
            critic_provider=data["critic_provider"], critic_model=data["critic_model"],
            target_artifact_id=data["target_artifact_id"],
            source_case_ids=list(data["source_case_ids"]),
            input_packet_sha256=data["input_packet_sha256"],
            findings=findings, created_at=data["created_at"],
            artifact_type=data.get("artifact_type", ARTIFACT_TYPE_FALSIFICATION),
            protocol_version=data.get("protocol_version", PROTOCOL_VERSION),
        )


@dataclass(frozen=True)
class JudgmentArtifact:
    judgment_id: str
    case_id: str
    source_run_id: str
    source_analysis_artifact_ids: List[str]
    source_falsification_artifact_ids: List[str]
    status: str
    reasons: List[str]
    material_disagreements: List[str]
    schema_ambiguities: List[str]
    created_at: str
    artifact_type: str = ARTIFACT_TYPE_JUDGMENT
    protocol_version: str = PROTOCOL_VERSION

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "JudgmentArtifact":
        return JudgmentArtifact(**{k: v for k, v in data.items()})
