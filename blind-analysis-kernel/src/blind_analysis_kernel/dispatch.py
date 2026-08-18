"""The ONLY module in this package that imports `ca_agents`,
`gpt_mechanism_judge`, or `case_claim_kernel`. Every other module here
(models.py, identity.py, packet.py, validator.py, ledger.py) is a
standalone, zero-cross-package-dependency library, matching the
discipline `case-claim-kernel` and `gpt-mechanism-judge` already
established.

This module IS the blind-dispatch boundary: `build_packet` reuses Stage
1's identity minting and Stage 2's/CA's existing prompt template;
`run_claude_analysis`/`run_gpt_analysis` reuse the real, unmodified
`ca_agents.same_mechanism_gate.profile_anomaly` with the real, unmodified
`ClaudeMechanismJudge`/`OpenAIMechanismJudge` - no third provider
abstraction is introduced; this is orchestration, not a new Judge type.

CREDENTIAL DISCIPLINE (task §5)
    Neither `run_claude_analysis` nor `run_gpt_analysis` catches
    `LLMError`/`OpenAIError`. A missing key or a transport failure
    propagates straight out of `profile_anomaly()` uncaught - the caller
    (run_stage3_job.py) is expected to let that crash the process with a
    non-zero exit, exactly what task §5 requires ("that provider job must
    fail loudly... Do not convert missing credentials into
    INSUFFICIENT_DATA"). Only a genuinely malformed model response
    degrades to INSUFFICIENT_DATA, and that degradation already lives
    inside `ClaudeMechanismJudge`/`OpenAIMechanismJudge` themselves (both
    unmodified) - this module adds no new error handling of its own.
"""

from __future__ import annotations

import os
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Dict, Optional

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
for _rel in ("constraint-archaeology-agents/src", "gpt-mechanism-judge/src", "case-claim-kernel/src"):
    _p = os.path.join(_REPO_ROOT, *_rel.split("/"))
    if _p not in sys.path:
        sys.path.insert(0, _p)

from ca_agents.mechanism_judge import ClaudeMechanismJudge  # noqa: E402
from ca_agents.same_mechanism_gate import GateAnomaly, profile_anomaly, PROFILE_PROMPT  # noqa: E402
from ca_agents.llm import DEFAULT_MODEL as CLAUDE_DEFAULT_MODEL  # noqa: E402
from case_claim_kernel.identity import make_case_id  # noqa: E402
from gpt_mechanism_judge.judge import OpenAIMechanismJudge, PROVIDER as GPT_PROVIDER  # noqa: E402
from gpt_mechanism_judge.openai_client import DEFAULT_MODEL as GPT_DEFAULT_MODEL  # noqa: E402

from .identity import make_analysis_artifact_id
from .models import PROTOCOL_VERSION, PROVIDER_ANTHROPIC, IndependentAnalysisArtifact
from .packet import EvidencePacket, packet_sha256

CA_SOURCE_SYSTEM = "constraint_archaeology_agents"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_packet(anomaly: Dict[str, Any], observations: Dict[str, Dict[str, Any]],
                  run_id: str, protocol_version: str = PROTOCOL_VERSION) -> EvidencePacket:
    """Builds the one immutable packet both provider jobs will consume,
    from a real, already-published CA anomaly + its representative
    observation - same read-only, `json.load`-only sourcing
    `case_claim_kernel.wrap` already uses, plus the real Stage-1 case_id
    for that same anomaly (via `make_case_id`, not re-derived here).
    """
    anomaly_id = anomaly["anomaly_id"]
    rep_observation_id = anomaly["observation_ids"][0]
    obs = observations[rep_observation_id]

    gate_anomaly_fields = {
        "id": obs["observation_id"],
        "source": obs["source"],
        "process": obs["process"],
        "pain": obs["pain"],
        "current_carrier": obs["current_carrier"],
        "failure_mode": obs["failure_mode"],
        "evidence_count": len(anomaly["observation_ids"]),
        "confidence": obs["confidence"],
    }

    case_id = make_case_id(CA_SOURCE_SYSTEM, "anomaly", anomaly_id)

    return EvidencePacket(
        run_id=run_id,
        protocol_version=protocol_version,
        source_case_ids=[case_id],
        source_artifact_ids=[gate_anomaly_fields["id"]],
        anomaly=gate_anomaly_fields,
        profile_prompt_template=PROFILE_PROMPT,
        system_prompt_note=(
            "Shared task framing for both providers: independently profile the "
            "single reported failure named in `anomaly` using `profile_prompt_template`. "
            "Neither provider is shown the other's output at any point before both "
            "analyses are complete - see blind_analysis_kernel/CONTRACT.md."
        ),
        created_at=utc_now_iso(),
    )


def _run_analysis(packet: EvidencePacket, *, provider: str, model: str,
                   judge, model_version: Optional[str] = None) -> IndependentAnalysisArtifact:
    anomaly = GateAnomaly(**packet.anomaly)
    profile = profile_anomaly(anomaly, judge)  # LLMError/OpenAIError propagate uncaught - see module docstring
    return IndependentAnalysisArtifact(
        artifact_id=make_analysis_artifact_id(packet.run_id, provider),
        run_id=packet.run_id,
        source_case_ids=list(packet.source_case_ids),
        source_artifact_ids=list(packet.source_artifact_ids),
        provider=provider,
        model=model,
        model_version=model_version,
        created_at=utc_now_iso(),
        input_packet_sha256=packet_sha256(packet),
        analysis=asdict(profile),
    )


def run_claude_analysis(packet: EvidencePacket) -> IndependentAnalysisArtifact:
    """Consumes ONLY `packet` - no other module-level or process state
    that could carry a GPT result in. Uses the real, unmodified
    `ClaudeMechanismJudge` (constraint-archaeology-agents' own production
    judge, already used by `run_daily.py`)."""
    return _run_analysis(packet, provider=PROVIDER_ANTHROPIC, model=CLAUDE_DEFAULT_MODEL,
                          judge=ClaudeMechanismJudge())


def run_gpt_analysis(packet: EvidencePacket) -> IndependentAnalysisArtifact:
    """Consumes ONLY `packet` - no other module-level or process state
    that could carry a Claude result in. Uses Stage 2's
    `OpenAIMechanismJudge` unmodified."""
    return _run_analysis(packet, provider=GPT_PROVIDER, model=GPT_DEFAULT_MODEL,
                          judge=OpenAIMechanismJudge())
