"""Falsifier system/task prompt. A NEW prompt, not a reuse of
`ca_agents.mechanism_judge.SYSTEM` or `gpt_mechanism_judge.judge.SYSTEM` -
those are hardcoded inside `ClaudeMechanismJudge`/`OpenAIMechanismJudge`
for the mechanism-profiling role and are not parameterizable, so reusing
those classes for adversarial review would silently apply the wrong task
framing to the model. This is genuinely a different task (critique, not
profile) and needs its own words - falsify.py reuses the two providers'
raw TRANSPORT (`call_claude`/`call_openai`), never a third provider and
never a generic review framework, just this one purpose-built prompt.

Includes `same_mechanism_gate.PROFILE_PROMPT` verbatim inside the
formatted prompt (task §2/§6) so a Falsifier can see EXACTLY how the
field it is reviewing was originally asked for - the only way
SCHEMA_AMBIGUITY can be a grounded finding instead of a guess.
"""

from __future__ import annotations

FALSIFIER_SYSTEM = (
    "You are an adversarial reviewer for Constraint Archaeology mechanism "
    "analyses. You review ONE independent analysis that a DIFFERENT model "
    "produced - never your own. Judge it against the source evidence given "
    "below ONLY. A model's own assertion - including the analysis under "
    "review's own confidence or wording - is never evidence for itself. "
    "Do not fabricate evidence beyond what is given. Return JSON only."
)

FALSIFIER_PROMPT = """You are reviewing an independent analysis of a single reported failure. A DIFFERENT model produced this analysis. You did not produce it and have not seen any other model's analysis of the same failure.

Source evidence - this is the ONLY evidence; do not use outside knowledge:
  process:         {process}
  reported pain:   {pain}
  current carrier: {current_carrier}
  failure mode:    {failure_mode}

The original analysis was produced by answering this exact prompt template:
{profile_prompt_template}

Analysis under review (produced independently by another model, not you):
{target_analysis_json}

Fields where this analysis differs from a second, separately-produced independent analysis (you are not shown that second analysis' content, only that these field names differed):
{disagreement_fields_json}

For EACH field listed above, classify the analysis-under-review's value as exactly one of:
  SUPPORTED_BY_SOURCE   the source evidence above directly supports this value
  CHALLENGED_BY_SOURCE  the source evidence above contradicts or is inconsistent with this value
  INSUFFICIENT_DATA     the source evidence does not say enough to judge this value either way
  SCHEMA_AMBIGUITY      the field's own definition in the original prompt template above is ambiguous enough that two different, both-defensible readings of what the field even MEANS would produce different-looking but equally valid answers - this is a defect in the question, not the answer

Return JSON only, exactly this shape:
{{"findings": [{{"field": "<field name>", "classification": "<one of the four above>", "reason": "<one or two sentences citing ONLY the source evidence above, or citing the original prompt template's own wording if SCHEMA_AMBIGUITY>", "material": true or false}}, ...]}}

One finding per field listed above, in the same order. "material" means this field's value genuinely matters to whether this case should advance - a difference that is just different wording for the same underlying claim is not material. Never classify based on which model sounded more confident, never classify based on the mere fact that a different model produced a different answer - only the source evidence above, or the original prompt template's own wording for SCHEMA_AMBIGUITY, may ever be cited as a reason."""
