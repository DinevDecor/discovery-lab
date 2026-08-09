from __future__ import annotations
from .llm import call_claude, parse_json_object

SYSTEM="""You are a mechanism judge for Constraint Archaeology. Analyze causal failure mechanisms only. Do not propose products, markets, startups, or investments. Return JSON only."""


class ClaudeMechanismJudge:
    def profile(self,prompt:str):
        try:
            return parse_json_object(call_claude(SYSTEM,prompt,900))
        except (ValueError, KeyError):
            # A malformed/unparseable judge response is not a decision - it's
            # a missing one. Returning {} lets profile_anomaly() fall back to
            # its own defaults (confidence=0.0), which same_mechanism()'s
            # existing evidence-floor check already routes to
            # INSUFFICIENT_DATA/UNRESOLVED (see test_thin_evidence_unresolved).
            # No new gate outcome, no changed threshold - this only stops a
            # parsing hiccup from crashing the whole run before that check runs.
            return {}

    def counterfactual(self,prompt:str):
        try:
            # 500 was observed truncating the model's JSON mid-string in real
            # runs; raised to match profile()'s budget. Kept even though the
            # except below also covers truncation, since giving the model
            # more room to finish is strictly better than relying on the
            # fallback.
            return parse_json_object(call_claude(SYSTEM,prompt,900))
        except (ValueError, KeyError) as exc:
            # Same reasoning as profile(): an unparseable response can't tell
            # us whether the repair removes the failure. removes_failure=None
            # is the exact "undecidable" shape _cross_test already expects
            # and routes to INSUFFICIENT_DATA/UNRESOLVED (see
            # test_undecidable_counterfactual_unresolved) - not a new outcome.
            return {"removes_failure": None, "reason": f"judge response unparseable: {exc}"}
