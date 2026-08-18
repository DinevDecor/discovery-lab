"""Deterministic id assignment for Stage 3 artifacts.

DIFFERENT RULE FROM case_claim_kernel.identity, ON PURPOSE
    Stage 1's `make_case_id`/`make_claim_id` deliberately exclude content
    and run identity, so a Case/Claim's id survives a later re-run with
    revised content. An independent analysis is the opposite kind of
    object: task §9 requires "a rerun is a new run_id and new analysis
    artifacts" and forbids deduping two different provider analyses into
    one artifact. So `make_analysis_artifact_id` DOES include `run_id`
    and `provider` in its hash material - identity here is scoped to
    "this run, this provider", not to "this real-world case" the way
    Stage 1's ids are. `source_case_ids` stays out of the hash on
    purpose too: two providers analyzing the exact same case in the same
    run must still get two different artifact_ids (§3: "The same source
    Cases/Claims must retain the same semantic identities... Provider/
    model must NOT enter Case/Claim identity" - the mirror image of that
    rule is that Case identity must not leak INTO artifact identity
    either, or a provider name typo could silently collide two providers'
    ids if they ever produced byte-identical case-id lists).
"""

from __future__ import annotations

import hashlib
import json
import uuid


def _canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str)


def default_run_id() -> str:
    """A fresh, unpredictable run_id when the caller doesn't supply one
    (e.g. a real GitHub Actions run should pass `github.run_id` instead -
    see run_stage3_job.py's `prepare` subcommand). Never used to derive
    an artifact_id on its own; always paired with `provider`."""
    return uuid.uuid4().hex


def make_analysis_artifact_id(run_id: str, provider: str) -> str:
    """Deterministic id from (run_id, provider) alone. A retry within the
    same run_id/provider (e.g. a flaky-step re-run of the same GitHub
    Actions job) is idempotent - same id, same ledger no-op on re-append
    (see ledger.py). A genuinely new run_id always produces a new id,
    regardless of whether the analysis content ends up identical.
    """
    material = _canonical({"run_id": run_id, "provider": provider})
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()[:32]
    return f"analysis:{digest}"
