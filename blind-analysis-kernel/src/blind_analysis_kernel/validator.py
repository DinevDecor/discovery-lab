"""Validation for IndependentAnalysisArtifact. Mirrors the discipline
`case_claim_kernel.validator`/`ca_agents.findings_ledger.validate()`
already established (non-empty ids, UTC-Z timestamps, non-empty
provenance) - re-implemented, not imported, per this whole family of
packages' "read data, never import another package's code" convention.
"""

from __future__ import annotations

from .models import ARTIFACT_TYPE_INDEPENDENT_ANALYSIS, IndependentAnalysisArtifact


class ArtifactValidationError(ValueError):
    pass


def validate(artifact: IndependentAnalysisArtifact) -> None:
    if artifact.artifact_type != ARTIFACT_TYPE_INDEPENDENT_ANALYSIS:
        raise ArtifactValidationError(f"unknown artifact_type: {artifact.artifact_type!r}")

    for name in ("artifact_id", "run_id", "provider", "model", "created_at",
                 "input_packet_sha256", "protocol_version"):
        value = getattr(artifact, name)
        if not isinstance(value, str) or not value:
            raise ArtifactValidationError(f"{name} must be a non-empty string")

    if not artifact.created_at.endswith("Z"):
        raise ArtifactValidationError("created_at must be UTC ISO ending in 'Z'")

    if len(artifact.input_packet_sha256) != 64:
        raise ArtifactValidationError("input_packet_sha256 must be a full sha256 hex digest")

    if not isinstance(artifact.source_case_ids, list) or not artifact.source_case_ids or \
            any(not isinstance(x, str) or not x for x in artifact.source_case_ids):
        raise ArtifactValidationError("source_case_ids must be a non-empty list of non-empty strings")

    if not isinstance(artifact.source_artifact_ids, list) or not artifact.source_artifact_ids or \
            any(not isinstance(x, str) or not x for x in artifact.source_artifact_ids):
        raise ArtifactValidationError("source_artifact_ids must be a non-empty list of non-empty strings")

    if not isinstance(artifact.analysis, dict):
        raise ArtifactValidationError("analysis must be an object")
