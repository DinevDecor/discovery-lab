"""The deterministic Judge (task §7). NOT an LLM - no model call, no
network call, anywhere in this module. Its entire input is already-
computed structured data: the two IndependentAnalysisArtifacts' ids, the
deterministic Disagreement list (disagree.py), and the two
FalsificationArtifacts (falsify.py, already produced and persisted by
the time this runs). `decide()` is a pure function - same inputs always
produce the same JudgmentArtifact (minus `created_at`/`judgment_id`,
which the caller supplies).

WHY "JUDGMENT", NOT "JUDGE"
    `ca_agents.mechanism_judge.ClaudeMechanismJudge` already uses "judge"
    for an LLM wrapper in this codebase. Naming this module `judgment.py`
    (noun, the deterministic decision itself) rather than `judge.py`
    keeps the two concepts visually and lexically distinct - this module
    is the opposite of that one: zero models, one pure function.

DECISION RULE (exact, task §7)
    REJECT  - only when a Falsifier finding is CHALLENGED_BY_SOURCE,
              material=True, for a field where no finding (from either
              critic) also called SCHEMA_AMBIGUITY - a field whose very
              definition is contested cannot simultaneously be "hard
              falsified"; that is unresolved disagreement about an
              ambiguous question, not a clean contradiction (task §6).
    WATCH   - otherwise, whenever ANY field has an unresolved material
              disagreement (schema-ambiguous, evidence-insufficient, or
              genuinely evidence-supported-on-both-sides).
    ADVANCE - only when no field triggers REJECT or WATCH: no unresolved
              material disagreement, no material schema ambiguity, and
              both Falsifications structurally validate (checked before
              this function is ever called - see falsify.py's own
              consumers).
    INSUFFICIENT_DATA on a field NEVER contributes to REJECT - it only
    ever pushes toward WATCH, by construction (the REJECT condition
    checks CHALLENGED_BY_SOURCE only, nowhere else in this function).
"""

from __future__ import annotations

from typing import Dict, List

from .models import (
    CHALLENGED_BY_SOURCE,
    SCHEMA_AMBIGUITY,
    ADVANCE,
    REJECT,
    WATCH,
    Disagreement,
    FalsificationArtifact,
    JudgmentArtifact,
)


def decide(*, judgment_id: str, case_id: str, source_run_id: str,
           claude_artifact_id: str, gpt_artifact_id: str,
           disagreements: List[Disagreement],
           claude_falsification: FalsificationArtifact,
           gpt_falsification: FalsificationArtifact,
           created_at: str) -> JudgmentArtifact:
    """`claude_falsification` critiques GPT's analysis (produced by
    calling Claude - see falsify.py::run_claude_falsifier);
    `gpt_falsification` critiques Claude's analysis. Both are required -
    the caller is responsible for having actually obtained both before
    calling this (see run_stage4_job.py's `judge` subcommand, which
    loads both artifact files and fails loudly if either is missing,
    exactly like blind_analysis_kernel's own structural-integrity gate)."""

    findings_about_claude = {f.field: f for f in gpt_falsification.findings}
    findings_about_gpt = {f.field: f for f in claude_falsification.findings}

    material_disagreements: List[str] = []
    schema_ambiguities: List[str] = []
    reject_triggers: List[str] = []

    for d in disagreements:
        fc = findings_about_claude.get(d.field)
        fg = findings_about_gpt.get(d.field)
        material = bool(fc and fc.material) or bool(fg and fg.material)
        if not material:
            continue

        classes = {f.classification for f in (fc, fg) if f}

        if SCHEMA_AMBIGUITY in classes:
            schema_ambiguities.append(d.field)
            continue

        material_disagreements.append(d.field)
        if CHALLENGED_BY_SOURCE in classes:
            reject_triggers.append(d.field)

    reasons: List[str] = []
    if reject_triggers:
        status = REJECT
        reasons.append(
            f"hard falsification: field(s) {sorted(reject_triggers)} classified "
            "CHALLENGED_BY_SOURCE with material=True by a Falsifier, with no "
            "counter-classification of SCHEMA_AMBIGUITY on the same field."
        )
    elif schema_ambiguities or material_disagreements:
        status = WATCH
        if schema_ambiguities:
            reasons.append(
                f"schema ambiguity on field(s) {sorted(schema_ambiguities)} caps judgment "
                "at WATCH regardless of other fields (task §6)."
            )
        if material_disagreements:
            reasons.append(
                f"unresolved material disagreement on field(s) {sorted(material_disagreements)} "
                "- neither Falsifier resolved this to a shared, non-ambiguous, uncontested reading."
            )
    else:
        status = ADVANCE
        reasons.append(
            "no unresolved material disagreement and no material schema ambiguity across "
            f"{len(disagreements)} deterministically-detected field difference(s); evidence floor met."
        )

    return JudgmentArtifact(
        judgment_id=judgment_id,
        case_id=case_id,
        source_run_id=source_run_id,
        source_analysis_artifact_ids=sorted({claude_artifact_id, gpt_artifact_id}),
        source_falsification_artifact_ids=sorted({claude_falsification.artifact_id, gpt_falsification.artifact_id}),
        status=status,
        reasons=reasons,
        material_disagreements=sorted(set(material_disagreements)),
        schema_ambiguities=sorted(set(schema_ambiguities)),
        created_at=created_at,
    )
