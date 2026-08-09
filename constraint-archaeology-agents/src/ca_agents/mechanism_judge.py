from __future__ import annotations
from .llm import call_claude, parse_json_object

SYSTEM="""You are a mechanism judge for Constraint Archaeology. Analyze causal failure mechanisms only. Do not propose products, markets, startups, or investments. Return JSON only."""

class ClaudeMechanismJudge:
    def profile(self,prompt:str):
        return parse_json_object(call_claude(SYSTEM,prompt,900))
    def counterfactual(self,prompt:str):
        # 500 was observed truncating the model's JSON mid-string in real runs
        # (json.decoder.JSONDecodeError: Unterminated string), crashing the
        # whole daily run before anything could be committed. Raised to match
        # profile()'s budget - this changes nothing about what the gate
        # decides, only whether it can finish deciding.
        return parse_json_object(call_claude(SYSTEM,prompt,900))
