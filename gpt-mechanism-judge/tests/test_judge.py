"""Mirrors constraint-archaeology-agents/tests/test_mechanism_judge.py
exactly, against OpenAIMechanismJudge instead of ClaudeMechanismJudge -
same malformed-JSON-degrades-to-the-gate's-existing-outcome behaviour,
same "a transport error is not the same as an undecidable answer"
distinction.
"""

import _pathsetup  # noqa: F401
import unittest
from unittest.mock import patch

from gpt_mechanism_judge.judge import OpenAIMechanismJudge
from gpt_mechanism_judge.openai_client import OpenAIError


class JudgeParseResilienceTests(unittest.TestCase):
    def test_counterfactual_malformed_json_becomes_undecidable(self):
        judge = OpenAIMechanismJudge()
        with patch("gpt_mechanism_judge.judge.call_openai",
                   return_value='{"removes_failure": true, "reason": "unterminated'):
            result = judge.counterfactual("irrelevant prompt")
        self.assertIsNone(result["removes_failure"])
        self.assertIn("reason", result)

    def test_counterfactual_valid_json_passes_through_unchanged(self):
        judge = OpenAIMechanismJudge()
        with patch("gpt_mechanism_judge.judge.call_openai",
                   return_value='{"removes_failure": true, "reason": "ok"}'):
            result = judge.counterfactual("irrelevant prompt")
        self.assertEqual(result, {"removes_failure": True, "reason": "ok"})

    def test_profile_malformed_json_becomes_empty_dict(self):
        judge = OpenAIMechanismJudge()
        with patch("gpt_mechanism_judge.judge.call_openai",
                   return_value='{"hidden_function": "reconcile", "confidence": 0.9'):
            result = judge.profile("irrelevant prompt")
        self.assertEqual(result, {})

    def test_profile_valid_json_passes_through_unchanged(self):
        judge = OpenAIMechanismJudge()
        payload = '{"hidden_function": "reconcile", "confidence": 0.9, "failure_class": "absence"}'
        with patch("gpt_mechanism_judge.judge.call_openai", return_value=payload):
            result = judge.profile("irrelevant prompt")
        self.assertEqual(result["hidden_function"], "reconcile")
        self.assertEqual(result["confidence"], 0.9)

    def test_transport_errors_are_not_swallowed(self):
        # A missing API key or network failure is an infra problem, not an
        # "undecidable" model answer - it must propagate, not be silently
        # absorbed into {} / removes_failure=None.
        judge = OpenAIMechanismJudge()
        with patch("gpt_mechanism_judge.judge.call_openai",
                   side_effect=OpenAIError("OPENAI_API_KEY is not set")):
            with self.assertRaises(OpenAIError):
                judge.counterfactual("irrelevant prompt")
            with self.assertRaises(OpenAIError):
                judge.profile("irrelevant prompt")


class JudgeProtocolShapeTests(unittest.TestCase):
    """Structural (duck-typed) satisfaction of ca_agents.same_mechanism_gate
    .JudgeProtocol - checked here without importing ca_agents at all,
    matching this package's own zero-dependency claim."""

    def test_has_profile_method_with_one_string_argument(self):
        import inspect
        sig = inspect.signature(OpenAIMechanismJudge.profile)
        params = [p for p in sig.parameters if p != "self"]
        self.assertEqual(params, ["prompt"])

    def test_has_counterfactual_method_with_one_string_argument(self):
        import inspect
        sig = inspect.signature(OpenAIMechanismJudge.counterfactual)
        params = [p for p in sig.parameters if p != "self"]
        self.assertEqual(params, ["prompt"])

    def test_profile_returns_a_dict(self):
        judge = OpenAIMechanismJudge()
        with patch("gpt_mechanism_judge.judge.call_openai", return_value='{"confidence": 0.5}'):
            self.assertIsInstance(judge.profile("p"), dict)

    def test_counterfactual_returns_a_dict(self):
        judge = OpenAIMechanismJudge()
        with patch("gpt_mechanism_judge.judge.call_openai",
                   return_value='{"removes_failure": false, "reason": "no"}'):
            self.assertIsInstance(judge.counterfactual("p"), dict)


if __name__ == "__main__":
    unittest.main()
