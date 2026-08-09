import os, sys, unittest
from unittest.mock import patch
ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(ROOT, "src"))
from ca_agents.mechanism_judge import ClaudeMechanismJudge
from ca_agents.llm import LLMError


class TestJudgeParseResilience(unittest.TestCase):
    """A real run crashed 3 times on json.decoder.JSONDecodeError raised
    from inside counterfactual()/profile() when Claude's response wasn't
    valid JSON - taking down the whole daily pipeline before anything could
    be committed. These calls must degrade to the gate's own existing
    "can't tell" outcome instead of propagating a parse exception."""

    def test_counterfactual_malformed_json_becomes_undecidable(self):
        judge = ClaudeMechanismJudge()
        with patch("ca_agents.mechanism_judge.call_claude", return_value='{"removes_failure": true, "reason": "unterminated'):
            result = judge.counterfactual("irrelevant prompt")
        self.assertIsNone(result["removes_failure"])
        self.assertIn("reason", result)

    def test_counterfactual_valid_json_passes_through_unchanged(self):
        judge = ClaudeMechanismJudge()
        with patch("ca_agents.mechanism_judge.call_claude", return_value='{"removes_failure": true, "reason": "ok"}'):
            result = judge.counterfactual("irrelevant prompt")
        self.assertEqual(result, {"removes_failure": True, "reason": "ok"})

    def test_profile_malformed_json_becomes_empty_dict(self):
        judge = ClaudeMechanismJudge()
        with patch("ca_agents.mechanism_judge.call_claude", return_value='{"hidden_function": "reconcile", "confidence": 0.9'):
            result = judge.profile("irrelevant prompt")
        self.assertEqual(result, {})

    def test_profile_valid_json_passes_through_unchanged(self):
        judge = ClaudeMechanismJudge()
        payload = '{"hidden_function": "reconcile", "confidence": 0.9, "failure_class": "absence"}'
        with patch("ca_agents.mechanism_judge.call_claude", return_value=payload):
            result = judge.profile("irrelevant prompt")
        self.assertEqual(result["hidden_function"], "reconcile")
        self.assertEqual(result["confidence"], 0.9)

    def test_llm_transport_errors_are_not_swallowed(self):
        # A missing API key or empty response is an infra problem that
        # should surface loudly (caught by run_daily.py's per-item
        # try/except and recorded as an error), not be silently treated as
        # "undecidable" the way a parse failure is.
        judge = ClaudeMechanismJudge()
        with patch("ca_agents.mechanism_judge.call_claude", side_effect=LLMError("ANTHROPIC_API_KEY is not set")):
            with self.assertRaises(LLMError):
                judge.counterfactual("irrelevant prompt")
            with self.assertRaises(LLMError):
                judge.profile("irrelevant prompt")


if __name__ == "__main__":
    unittest.main()
