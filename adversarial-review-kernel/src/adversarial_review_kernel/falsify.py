"""The ONLY module in this package that imports `ca_agents`,
`gpt_mechanism_judge`, or `blind_analysis_kernel` - matching the exact
"one dispatch module carries all cross-package imports, everything else
stays standalone" convention `blind_analysis_kernel.dispatch` already
established for Stage 3.

Reuses the two existing providers' raw TRANSPORT functions
(`ca_agents.llm.call_claude`, `gpt_mechanism_judge.openai_client
.call_openai`) directly - NOT `ClaudeMechanismJudge`/`OpenAIMechanismJudge`,
whose `SYSTEM` prompt is hardcoded to the mechanism-profiling task and
not swappable (see prompts.py's own docstring for why). This is not a
third provider abstraction; it is the same two providers, a different
task-specific prompt.

Reuses `blind_analysis_kernel.dispatch.build_packet` unmodified to
rebuild the raw evidence fields for Stage 4's own falsification run -
see this module's `build_falsifier_packet` docstring for why an exact
byte-identical replay of Stage 3's original packet (including its
wall-clock `created_at`) is neither obtainable nor necessary here.

BLINDNESS (task §4)
    `run_claude_falsifier` takes `(packet, gpt_artifact, disagreements)`
    - never `claude_artifact`. `run_gpt_falsifier` takes `(packet,
    claude_artifact, disagreements)` - never `gpt_artifact`. Neither
    function's signature has a parameter through which the other
    Falsifier's output, or the critic's own prior analysis, could arrive
    - checked structurally in tests/test_falsify_blindness.py, the same
    `inspect.signature` proof Stage 3 already used for
    `run_claude_analysis`/`run_gpt_analysis`. `redact.redact_for_critic`
    is the second half of the guarantee - see its own docstring.

CREDENTIAL DISCIPLINE
    Neither function catches `LLMError`/`OpenAIError` - a missing key or
    transport failure propagates uncaught, exactly like Stage 2/3's
    `ClaudeMechanismJudge`/`OpenAIMechanismJudge`/`run_claude_analysis`/
    `run_gpt_analysis`. Only a genuinely malformed/unparseable JSON
    response degrades - and it degrades to `INSUFFICIENT_DATA` with
    `material=True` (fail CONSERVATIVE, toward WATCH, never silently
    toward ADVANCE - a parse failure on a disputed field must never let
    the case advance unreviewed).
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
for _rel in ("constraint-archaeology-agents/src", "gpt-mechanism-judge/src", "blind-analysis-kernel/src"):
    _p = os.path.join(_REPO_ROOT, *_rel.split("/"))
    if _p not in sys.path:
        sys.path.insert(0, _p)

from ca_agents.llm import call_claude, parse_json_object as parse_json_object_claude  # noqa: E402
from ca_agents.llm import DEFAULT_MODEL as CLAUDE_DEFAULT_MODEL  # noqa: E402
from gpt_mechanism_judge.openai_client import call_openai, parse_json_object as parse_json_object_gpt  # noqa: E402
from gpt_mechanism_judge.openai_client import DEFAULT_MODEL as GPT_DEFAULT_MODEL  # noqa: E402
from blind_analysis_kernel.dispatch import build_packet  # noqa: E402
from blind_analysis_kernel.packet import EvidencePacket, packet_sha256  # noqa: E402

from .identity import make_falsification_artifact_id
from .models import CLASSIFICATIONS, INSUFFICIENT_DATA, PROVIDER_ANTHROPIC, PROVIDER_OPENAI
from .models import Disagreement, FalsificationArtifact, FalsificationFinding
from .prompts import FALSIFIER_PROMPT, FALSIFIER_SYSTEM
from .redact import redact_for_critic


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_falsifier_packet(anomaly: Dict[str, Any], observations: Dict[str, Dict[str, Any]],
                            run_id: str) -> EvidencePacket:
    """Rebuilds the raw evidence packet for a Stage 4 falsification run,
    from the same real, unchanged CA data Stage 3 itself reads.

    NOT a byte-identical replay of Stage 3's original packet: `packet
    _sha256` includes `created_at`, a wall-clock timestamp Stage 3 never
    persisted anywhere Stage 4 could recover it from (only the resulting
    hash was persisted, on the `IndependentAnalysisArtifact`s
    themselves - a one-way function, not reversible). What actually
    matters for Stage 4 - and what IS verified, see run_stage4_job.py's
    `disagree`/`claude-falsify`/`gpt-falsify` subcommands - is that this
    freshly-built packet's `source_case_ids`/`source_artifact_ids`/
    `anomaly` fields match what both original `IndependentAnalysisArtifact`
    records already recorded, i.e. the same real evidence, not a
    bit-identical historical packet object. The property Stage 4 needs
    and DOES guarantee is its own: both Falsifiers receive this ONE
    freshly-built packet, unmodified, and their two resulting
    `input_packet_sha256` values are checked to match each other -
    exactly the same "both providers, one immutable input" invariant
    Stage 3 established, applied fresh here.
    """
    return build_packet(anomaly, observations, run_id)


def _build_findings(raw: Any, redacted: List[Dict[str, Any]], *,
                     target_artifact_id: str, source_artifact_ids: List[str]) -> List[FalsificationFinding]:
    raw_by_field: Dict[str, Dict[str, Any]] = {}
    if isinstance(raw, dict) and isinstance(raw.get("findings"), list):
        for item in raw["findings"]:
            if isinstance(item, dict) and isinstance(item.get("field"), str):
                raw_by_field[item["field"]] = item

    findings: List[FalsificationFinding] = []
    for entry in redacted:
        field = entry["field"]
        item = raw_by_field.get(field)
        classification = item.get("classification") if item else None
        if classification not in CLASSIFICATIONS:
            # Degrade CONSERVATIVELY: material=True, so a parse failure or
            # a missing/invalid field can never silently permit ADVANCE.
            reason = ("falsifier response missing this field" if not item else
                      f"falsifier returned an unrecognized classification: {item.get('classification')!r}")
            findings.append(FalsificationFinding(
                field=field, target_analysis_artifact_id=target_artifact_id,
                classification=INSUFFICIENT_DATA, reason=reason,
                source_artifact_ids=list(source_artifact_ids), material=True,
            ))
            continue
        reason = item.get("reason") if isinstance(item.get("reason"), str) else ""
        material = item.get("material") if isinstance(item.get("material"), bool) else True
        findings.append(FalsificationFinding(
            field=field, target_analysis_artifact_id=target_artifact_id,
            classification=classification, reason=reason,
            source_artifact_ids=list(source_artifact_ids), material=material,
        ))
    return findings


def _format_prompt(packet: EvidencePacket, target_analysis: Dict[str, Any],
                    redacted: List[Dict[str, Any]]) -> str:
    return FALSIFIER_PROMPT.format(
        process=packet.anomaly["process"],
        pain=packet.anomaly["pain"],
        current_carrier=packet.anomaly["current_carrier"],
        failure_mode=packet.anomaly["failure_mode"],
        profile_prompt_template=packet.profile_prompt_template,
        target_analysis_json=json.dumps(target_analysis, sort_keys=True, ensure_ascii=False),
        disagreement_fields_json=json.dumps(redacted, sort_keys=True, ensure_ascii=False),
    )


def run_claude_falsifier(packet: EvidencePacket, gpt_analysis: Dict[str, Any], gpt_artifact_id: str,
                          disagreements: List[Disagreement]) -> FalsificationArtifact:
    """Claude reviewing GPT's analysis. Consumes ONLY the packet, GPT's
    analysis dict/id, and the disagreement list - no parameter carries
    Claude's own prior analysis or GPT's Falsifier output."""
    redacted = redact_for_critic(disagreements, critic_is_claude=True)
    prompt = _format_prompt(packet, gpt_analysis, redacted)
    text = call_claude(FALSIFIER_SYSTEM, prompt, 1400)  # LLMError propagates uncaught
    try:
        raw = parse_json_object_claude(text)
    except (ValueError, KeyError):
        raw = {}
    findings = _build_findings(raw, redacted, target_artifact_id=gpt_artifact_id,
                                source_artifact_ids=packet.source_artifact_ids)
    return FalsificationArtifact(
        artifact_id=make_falsification_artifact_id(packet.run_id, PROVIDER_ANTHROPIC),
        run_id=packet.run_id, critic_provider=PROVIDER_ANTHROPIC, critic_model=CLAUDE_DEFAULT_MODEL,
        target_artifact_id=gpt_artifact_id, source_case_ids=list(packet.source_case_ids),
        input_packet_sha256=packet_sha256(packet), findings=findings, created_at=utc_now_iso(),
    )


def run_gpt_falsifier(packet: EvidencePacket, claude_analysis: Dict[str, Any], claude_artifact_id: str,
                       disagreements: List[Disagreement]) -> FalsificationArtifact:
    """GPT reviewing Claude's analysis. Consumes ONLY the packet,
    Claude's analysis dict/id, and the disagreement list - no parameter
    carries GPT's own prior analysis or Claude's Falsifier output."""
    redacted = redact_for_critic(disagreements, critic_is_claude=False)
    prompt = _format_prompt(packet, claude_analysis, redacted)
    text = call_openai(FALSIFIER_SYSTEM, prompt, 1400)  # OpenAIError propagates uncaught
    try:
        raw = parse_json_object_gpt(text)
    except (ValueError, KeyError):
        raw = {}
    findings = _build_findings(raw, redacted, target_artifact_id=claude_artifact_id,
                                source_artifact_ids=packet.source_artifact_ids)
    return FalsificationArtifact(
        artifact_id=make_falsification_artifact_id(packet.run_id, PROVIDER_OPENAI),
        run_id=packet.run_id, critic_provider=PROVIDER_OPENAI, critic_model=GPT_DEFAULT_MODEL,
        target_artifact_id=claude_artifact_id, source_case_ids=list(packet.source_case_ids),
        input_packet_sha256=packet_sha256(packet), findings=findings, created_at=utc_now_iso(),
    )
