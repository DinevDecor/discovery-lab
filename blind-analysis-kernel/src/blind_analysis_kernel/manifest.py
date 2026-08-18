"""Run manifest: the smallest additional record Stage 3B needs.

`IndependentAnalysisArtifact` (models.py) already carries `run_id`,
`source_case_ids`, `source_artifact_ids`, `provider`, `model`,
`created_at`, `protocol_version`, and the full `analysis` payload - a
`RunManifest` does NOT repeat any of that. It exists only to answer one
question neither artifact answers alone: "which Claude artifact and
which GPT artifact came from the SAME run, against which exact commit of
the repository, and under which evidence packet hash" - a run-level
pointer record, not a third copy of the analysis content.

`workflow_run_id` and `run_id` are the same value in this system (Stage
3's `IndependentAnalysisArtifact.run_id` is always set from
`github.run_id` - see dispatch.py/run_stage3_job.py's `prepare`
subcommand). Both fields are kept, spelled out separately, because nothing
prevents a future run_id scheme from diverging from GitHub's own run id,
and the manifest is exactly the place that distinction should be
recorded if it ever happens - not something to guess at now.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class RunManifest:
    manifest_id: str
    run_id: str
    workflow_run_id: str
    head_sha: str
    input_packet_sha256: str
    source_case_ids: List[str]
    source_artifact_ids: List[str]
    claude_artifact_id: str
    claude_provider: str
    claude_model: str
    gpt_artifact_id: str
    gpt_provider: str
    gpt_model: str
    created_at: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ManifestValidationError(ValueError):
    pass


def make_manifest_id(run_id: str) -> str:
    """One manifest per run, deterministically - a retry of the same run
    is idempotent (see ledger.py's own reasoning for why this matters)."""
    return f"manifest:{run_id}"


def build_run_manifest(claude_artifact, gpt_artifact, *, workflow_run_id: str,
                        head_sha: str, created_at: str) -> RunManifest:
    """Both arguments are `models.IndependentAnalysisArtifact` (or
    anything with the same field names) for the SAME run - callers
    (run_stage3_job.py's `persist` subcommand) are responsible for the
    structural-integrity checks (matching run_id, matching
    input_packet_sha256, matching source_case_ids, distinct artifact_id)
    BEFORE calling this - this function only assembles the record, it
    does not re-validate what the caller already checked.
    """
    return RunManifest(
        manifest_id=make_manifest_id(claude_artifact.run_id),
        run_id=claude_artifact.run_id,
        workflow_run_id=workflow_run_id,
        head_sha=head_sha,
        input_packet_sha256=claude_artifact.input_packet_sha256,
        source_case_ids=list(claude_artifact.source_case_ids),
        source_artifact_ids=list(claude_artifact.source_artifact_ids),
        claude_artifact_id=claude_artifact.artifact_id,
        claude_provider=claude_artifact.provider,
        claude_model=claude_artifact.model,
        gpt_artifact_id=gpt_artifact.artifact_id,
        gpt_provider=gpt_artifact.provider,
        gpt_model=gpt_artifact.model,
        created_at=created_at,
    )


def validate_manifest(manifest: RunManifest) -> None:
    for name in ("manifest_id", "run_id", "workflow_run_id", "head_sha",
                 "input_packet_sha256", "claude_artifact_id", "claude_provider",
                 "claude_model", "gpt_artifact_id", "gpt_provider", "gpt_model", "created_at"):
        value = getattr(manifest, name)
        if not isinstance(value, str) or not value:
            raise ManifestValidationError(f"{name} must be a non-empty string")
    if not manifest.created_at.endswith("Z"):
        raise ManifestValidationError("created_at must be UTC ISO ending in 'Z'")
    if manifest.claude_artifact_id == manifest.gpt_artifact_id:
        raise ManifestValidationError("claude_artifact_id and gpt_artifact_id must not collide")
    if not manifest.source_case_ids:
        raise ManifestValidationError("source_case_ids must be non-empty")


class RunManifestLedger:
    """Append-only writer for `blind-analysis-kernel/data/runs.jsonl`.
    Same idempotent-append, only-write-path-is-append-mode discipline as
    `ledger.AnalysisLedger` - a deliberate, small duplication rather than
    a shared base class, so this module stays independently readable and
    neither ledger risks a change to one silently affecting the other.
    """

    def __init__(self, path: str):
        self.path = path
        self._known: set = set()
        self._entries: List[Dict[str, Any]] = []
        self._load_known()

    def _load_known(self) -> None:
        if not os.path.exists(self.path):
            return
        with open(self.path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                self._entries.append(row)
                mid = row.get("manifest_id")
                if isinstance(mid, str):
                    self._known.add(mid)

    def has(self, manifest_id: str) -> bool:
        return manifest_id in self._known

    @property
    def known_count(self) -> int:
        return len(self._known)

    def all_entries(self) -> List[Dict[str, Any]]:
        return list(self._entries)

    def append(self, manifest: RunManifest) -> bool:
        validate_manifest(manifest)
        if manifest.manifest_id in self._known:
            return False
        os.makedirs(os.path.dirname(os.path.abspath(self.path)) or ".", exist_ok=True)
        line = json.dumps(manifest.to_dict(), sort_keys=True, ensure_ascii=False, default=str)
        with open(self.path, "a", encoding="utf-8") as fh:  # append mode only
            fh.write(line + "\n")
        self._known.add(manifest.manifest_id)
        self._entries.append(manifest.to_dict())
        return True
