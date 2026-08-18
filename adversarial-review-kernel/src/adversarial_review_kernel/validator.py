"""Validation for FalsificationArtifact and JudgmentArtifact. Same
discipline every `*_kernel.validator` module in this repo already
holds itself to (non-empty ids, UTC-Z timestamps, closed vocabularies) -
re-implemented, not imported, per this whole family's "read data, never
import another package's code" convention within the library layer.
"""

from __future__ import annotations

from .models import (
    CLASSIFICATIONS,
    JUDGMENT_STATUSES,
    ARTIFACT_TYPE_FALSIFICATION,
    ARTIFACT_TYPE_JUDGMENT,
    FalsificationArtifact,
    JudgmentArtifact,
)


class ArtifactValidationError(ValueError):
    pass


def validate_falsification_artifact(artifact: FalsificationArtifact) -> None:
    if artifact.artifact_type != ARTIFACT_TYPE_FALSIFICATION:
        raise ArtifactValidationError(f"unknown artifact_type: {artifact.artifact_type!r}")

    for name in ("artifact_id", "run_id", "critic_provider", "critic_model",
                 "target_artifact_id", "input_packet_sha256", "created_at"):
        value = getattr(artifact, name)
        if not isinstance(value, str) or not value:
            raise ArtifactValidationError(f"{name} must be a non-empty string")

    if not artifact.created_at.endswith("Z"):
        raise ArtifactValidationError("created_at must be UTC ISO ending in 'Z'")

    if not artifact.source_case_ids:
        raise ArtifactValidationError("source_case_ids must be non-empty")

    if not artifact.findings:
        raise ArtifactValidationError("findings must be non-empty")

    for finding in artifact.findings:
        if finding.classification not in CLASSIFICATIONS:
            raise ArtifactValidationError(f"unknown classification: {finding.classification!r}")
        if not finding.field:
            raise ArtifactValidationError("finding.field must be non-empty")
        if not isinstance(finding.material, bool):
            raise ArtifactValidationError("finding.material must be a bool")
        if finding.target_analysis_artifact_id != artifact.target_artifact_id:
            raise ArtifactValidationError(
                "finding.target_analysis_artifact_id must match the artifact's own target_artifact_id")


def validate_judgment_artifact(artifact: JudgmentArtifact) -> None:
    if artifact.artifact_type != ARTIFACT_TYPE_JUDGMENT:
        raise ArtifactValidationError(f"unknown artifact_type: {artifact.artifact_type!r}")

    if artifact.status not in JUDGMENT_STATUSES:
        raise ArtifactValidationError(f"unknown status: {artifact.status!r}")

    for name in ("judgment_id", "case_id", "source_run_id", "created_at"):
        value = getattr(artifact, name)
        if not isinstance(value, str) or not value:
            raise ArtifactValidationError(f"{name} must be a non-empty string")

    if not artifact.created_at.endswith("Z"):
        raise ArtifactValidationError("created_at must be UTC ISO ending in 'Z'")

    if not artifact.source_analysis_artifact_ids:
        raise ArtifactValidationError("source_analysis_artifact_ids must be non-empty")

    if not artifact.source_falsification_artifact_ids:
        raise ArtifactValidationError("source_falsification_artifact_ids must be non-empty")

    if not artifact.reasons:
        raise ArtifactValidationError("reasons must be non-empty - every judgment must explain itself")
