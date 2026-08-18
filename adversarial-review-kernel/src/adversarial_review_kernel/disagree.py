"""Deterministic disagreement extraction (task §3). Zero cross-package
dependency - operates on plain dicts shaped like
`blind_analysis_kernel.models.IndependentAnalysisArtifact`, never imports
that module (the CLI layer, which does import it, is responsible for
handing this module `.artifact_id`/`.analysis` values already).

THIS MODULE NEVER DECIDES WHICH MODEL IS RIGHT
    `extract_disagreements` is a value-inequality check over
    `COMPARED_FIELDS` only - field, both raw values, both artifact ids.
    No `material` flag, no classification, no reasoning text. Materiality
    and classification are exclusively `FalsificationFinding` concerns,
    produced later by a model call reviewing source evidence (falsify.py)
    - this module could not produce them even if asked to, because it
    never sees the source evidence packet, only the two analyses.
"""

from __future__ import annotations

from typing import Any, Dict, List

from .models import COMPARED_FIELDS, Disagreement


def extract_disagreements(claude_analysis: Dict[str, Any], gpt_analysis: Dict[str, Any], *,
                           claude_artifact_id: str, gpt_artifact_id: str) -> List[Disagreement]:
    """`claude_analysis`/`gpt_analysis` are the `.analysis` dicts off two
    IndependentAnalysisArtifacts for the same run. Returns one
    Disagreement per field in COMPARED_FIELDS whose value differs by
    plain `!=` - no normalization, no fuzzy/semantic matching (same
    "identity is asserted, never inferred" discipline
    `capability_observatory`'s ADR 002 and every `*_kernel.identity`
    module in this repo already holds itself to)."""
    out: List[Disagreement] = []
    for name in COMPARED_FIELDS:
        cv = claude_analysis.get(name)
        gv = gpt_analysis.get(name)
        if cv != gv:
            out.append(Disagreement(
                field=name, claude_value=cv, gpt_value=gv,
                claude_artifact_id=claude_artifact_id, gpt_artifact_id=gpt_artifact_id,
            ))
    return out
