"""OpenAIMechanismJudge: the thin adapter itself.

Satisfies `ca_agents.same_mechanism_gate.JudgeProtocol` PURELY BY SHAPE -
`Protocol` in that module is structural typing, so this class does not
need to import `JudgeProtocol` (or anything else from `ca_agents`) to be
accepted anywhere a judge is expected. Two methods, same signatures, same
return shape as `ca_agents.mechanism_judge.ClaudeMechanismJudge` - that
existing class is the exact reference this adapter was built to match,
field-for-field:

  .profile(prompt: str) -> Dict[str, Any]
  .counterfactual(prompt: str) -> Dict[str, Any]

Same SYSTEM instruction text as ClaudeMechanismJudge, reproduced here
(not imported) so both providers are judged against literally the same
task framing - changing the wording would confound "does the adapter
work" with "did I also change the question being asked."

Same error-handling contract as ClaudeMechanismJudge, and for the same
documented reason: a malformed/unparseable model response is not a
decision, it's a missing one, and same_mechanism_gate.py already has a
defined "can't tell" outcome for both call sites
(profile_anomaly's confidence-floor check, _cross_test's
`removes_failure is None` check) - this adapter degrades into those
existing outcomes rather than crashing the run or inventing a third
"error" outcome the gate does not know about. A genuine transport failure
(missing key, network/HTTP error) is NOT caught here and propagates as
OpenAIError, exactly like ClaudeMechanismJudge lets LLMError propagate -
an infrastructure problem must surface loudly, not silently read as
"undecidable".
"""

from __future__ import annotations

from typing import Any, Dict

from .openai_client import call_openai, parse_json_object

SYSTEM = (
    "You are a mechanism judge for Constraint Archaeology. Analyze causal "
    "failure mechanisms only. Do not propose products, markets, startups, "
    "or investments. Return JSON only."
)

PROVIDER = "openai"


class OpenAIMechanismJudge:
    def profile(self, prompt: str) -> Dict[str, Any]:
        try:
            return parse_json_object(call_openai(SYSTEM, prompt, 900))
        except (ValueError, KeyError):
            return {}

    def counterfactual(self, prompt: str) -> Dict[str, Any]:
        try:
            return parse_json_object(call_openai(SYSTEM, prompt, 900))
        except (ValueError, KeyError) as exc:
            return {"removes_failure": None, "reason": f"judge response unparseable: {exc}"}
