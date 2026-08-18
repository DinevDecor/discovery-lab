"""Deterministic id assignment for Stage 4 artifacts. Same family of
rules as `blind_analysis_kernel.identity`/`case_claim_kernel.identity`:
identity is scoped to what must never silently collide, and nothing more.
"""

from __future__ import annotations

import hashlib
import json


def _canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str)


def make_falsification_artifact_id(run_id: str, critic_provider: str) -> str:
    """Deterministic id from (run_id, critic_provider) - a retry within
    the same run/critic is idempotent (matches
    blind_analysis_kernel.identity.make_analysis_artifact_id's own
    reasoning); Claude-critiquing-GPT and GPT-critiquing-Claude in the
    same run always get different ids."""
    material = _canonical({"run_id": run_id, "critic_provider": critic_provider})
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()[:32]
    return f"falsification:{digest}"


def make_judgment_id(run_id: str) -> str:
    """One judgment per run, deterministically - a retry of the same
    run's judgment is idempotent, matching
    blind_analysis_kernel.manifest.make_manifest_id's own reasoning for
    the same (run_id)-scoped, one-per-run identity choice."""
    material = _canonical({"run_id": run_id})
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()[:32]
    return f"judgment:{digest}"
