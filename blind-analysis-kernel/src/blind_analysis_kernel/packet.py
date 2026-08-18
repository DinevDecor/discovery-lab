"""EvidencePacket: the one immutable input both provider jobs consume.

Pure data shape + a canonical hash function only - no ca_agents import
here (that stays confined to dispatch.py, the module that actually knows
how to build one from a real CA anomaly - see its docstring). This keeps
the blindness invariant checkable by inspection: everything a packet CAN
contain is enumerated in one dataclass, right here, so "does the packet
leak the other provider's output" is answerable by reading one small
file, not by auditing every call site.

TASK §1'S "MUST NOT CONTAIN" LIST, ENFORCED BY ABSENCE
    There is no field here named or shaped like a verdict, confidence,
    profile, or analysis of any kind - `EvidencePacket` has exactly the
    fields task §1 says it MAY contain (case/artifact ids, the raw
    evidence the existing gate needs, the shared prompt template, run
    metadata) and nothing else. Adding an `analysis`-shaped field to this
    dataclass would be the one change that could reintroduce leakage -
    tests/test_blindness.py checks this dataclass's own field set for
    exactly that reason.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Dict, List

from .models import PROTOCOL_VERSION


def _canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str)


@dataclass(frozen=True)
class EvidencePacket:
    run_id: str
    protocol_version: str
    source_case_ids: List[str]
    source_artifact_ids: List[str]
    # The exact ca_agents.same_mechanism_gate.GateAnomaly field values
    # (id/source/process/pain/current_carrier/failure_mode/evidence_count/
    # confidence) - the raw/source evidence the existing mechanism gate
    # needs, copied through unchanged, never re-interpreted here.
    anomaly: Dict[str, Any]
    # ca_agents.same_mechanism_gate.PROFILE_PROMPT, verbatim - the shared
    # task prompt template BOTH providers are asked with. Embedding the
    # literal text (not just a version tag) makes the packet fully
    # self-describing and hashable: "exactly what was asked" is provable
    # from the packet alone, without trusting that same_mechanism_gate.py
    # hasn't changed since.
    profile_prompt_template: str
    system_prompt_note: str
    created_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "protocol_version": self.protocol_version,
            "source_case_ids": list(self.source_case_ids),
            "source_artifact_ids": list(self.source_artifact_ids),
            "anomaly": self.anomaly,
            "profile_prompt_template": self.profile_prompt_template,
            "system_prompt_note": self.system_prompt_note,
            "created_at": self.created_at,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "EvidencePacket":
        return EvidencePacket(
            run_id=data["run_id"],
            protocol_version=data.get("protocol_version", PROTOCOL_VERSION),
            source_case_ids=list(data["source_case_ids"]),
            source_artifact_ids=list(data["source_artifact_ids"]),
            anomaly=dict(data["anomaly"]),
            profile_prompt_template=data["profile_prompt_template"],
            system_prompt_note=data.get("system_prompt_note", ""),
            created_at=data["created_at"],
        )


def packet_sha256(packet: EvidencePacket) -> str:
    """The one hash both provider jobs must report identically (task §7/
    §8). Computed over `to_dict()`'s canonical JSON - the exact same
    serialization used to persist/transmit the packet, so a byte-for-byte
    re-serialization (e.g. after a JSON round-trip through a GitHub
    Actions artifact download) hashes the same."""
    return hashlib.sha256(_canonical(packet.to_dict()).encode("utf-8")).hexdigest()
