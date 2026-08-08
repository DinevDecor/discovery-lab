from __future__ import annotations
from .llm import call_claude, parse_json_object

SYSTEM="""You are a mechanism judge for Constraint Archaeology. Analyze causal failure mechanisms only. Do not propose products, markets, startups, or investments. Return JSON only."""

class ClaudeMechanismJudge:
    def profile(self,prompt:str):
        return parse_json_object(call_claude(SYSTEM,prompt,900))
    def counterfactual(self,prompt:str):
        return parse_json_object(call_claude(SYSTEM,prompt,500))
