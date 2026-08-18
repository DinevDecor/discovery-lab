"""Proves the blindness invariant (task §1/§7) offline, against a packet
built from real, already-committed CA data (ANOM-0001 - the same real
anomaly Stage 2's acceptance script uses). No real network call is made;
`call_claude`/`call_openai` are mocked at their respective source
functions, exactly like ca_agents/tests/test_mechanism_judge.py and
gpt-mechanism-judge/tests/test_judge.py already do.
"""

import _pathsetup  # noqa: F401
import inspect
import json
import os
import unittest
from unittest.mock import patch

from blind_analysis_kernel.dispatch import build_packet, run_claude_analysis, run_gpt_analysis
from blind_analysis_kernel.packet import packet_sha256

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CA_ANOMALIES_PATH = os.path.join(REPO_ROOT, "constraint-archaeology-agents", "data", "anomalies.json")
CA_OBSERVATIONS_PATH = os.path.join(REPO_ROOT, "constraint-archaeology-agents", "data", "observations.jsonl")

_PROFILE_RESPONSE = json.dumps({
    "hidden_function": "publish a working research prototype",
    "inputs": "implementation effort", "outputs": "usable tool",
    "carrier": "irrelevant", "failure_class": "capacity",
    "failure_mechanism": "execution speed too slow", "repair": "optimize runtime",
    "confidence": 0.7,
})


def _load_real_packet(run_id="test-run-1"):
    with open(CA_ANOMALIES_PATH, encoding="utf-8") as f:
        anomalies = {a["anomaly_id"]: a for a in json.load(f)}
    observations = {}
    with open(CA_OBSERVATIONS_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                o = json.loads(line)
                observations[o["observation_id"]] = o
    return build_packet(anomalies["ANOM-0001"], observations, run_id)


@unittest.skipUnless(os.path.exists(CA_ANOMALIES_PATH), "real CA anomalies.json not present")
@unittest.skipUnless(os.path.exists(CA_OBSERVATIONS_PATH), "real CA observations.jsonl not present")
class DispatchSignatureTests(unittest.TestCase):
    """Structural proof there is no back-channel parameter either
    function could use to receive the other provider's output."""

    def test_run_claude_analysis_takes_only_packet(self):
        params = list(inspect.signature(run_claude_analysis).parameters)
        self.assertEqual(params, ["packet"])

    def test_run_gpt_analysis_takes_only_packet(self):
        params = list(inspect.signature(run_gpt_analysis).parameters)
        self.assertEqual(params, ["packet"])


@unittest.skipUnless(os.path.exists(CA_ANOMALIES_PATH), "real CA anomalies.json not present")
@unittest.skipUnless(os.path.exists(CA_OBSERVATIONS_PATH), "real CA observations.jsonl not present")
class BlindDispatchOfflineTests(unittest.TestCase):
    def setUp(self):
        self.packet = _load_real_packet()

    def test_claude_analysis_never_calls_the_openai_transport(self):
        with patch("ca_agents.mechanism_judge.call_claude", return_value=_PROFILE_RESPONSE) as mock_claude, \
             patch("gpt_mechanism_judge.judge.call_openai") as mock_openai:
            run_claude_analysis(self.packet)
        mock_claude.assert_called_once()
        mock_openai.assert_not_called()

    def test_gpt_analysis_never_calls_the_anthropic_transport(self):
        with patch("gpt_mechanism_judge.judge.call_openai", return_value=_PROFILE_RESPONSE) as mock_openai, \
             patch("ca_agents.mechanism_judge.call_claude") as mock_claude:
            run_gpt_analysis(self.packet)
        mock_openai.assert_called_once()
        mock_claude.assert_not_called()

    def test_both_artifacts_have_distinct_ids(self):
        with patch("ca_agents.mechanism_judge.call_claude", return_value=_PROFILE_RESPONSE):
            claude_artifact = run_claude_analysis(self.packet)
        with patch("gpt_mechanism_judge.judge.call_openai", return_value=_PROFILE_RESPONSE):
            gpt_artifact = run_gpt_analysis(self.packet)
        self.assertNotEqual(claude_artifact.artifact_id, gpt_artifact.artifact_id)

    def test_both_artifacts_share_the_same_source_case_ids(self):
        with patch("ca_agents.mechanism_judge.call_claude", return_value=_PROFILE_RESPONSE):
            claude_artifact = run_claude_analysis(self.packet)
        with patch("gpt_mechanism_judge.judge.call_openai", return_value=_PROFILE_RESPONSE):
            gpt_artifact = run_gpt_analysis(self.packet)
        self.assertEqual(claude_artifact.source_case_ids, gpt_artifact.source_case_ids)
        # And it's the real Stage-1 case_id for ANOM-0001, not a placeholder.
        self.assertEqual(claude_artifact.source_case_ids, ["case:951963c3345d364c44c2f2ab34197651"])

    def test_both_artifacts_share_the_same_input_packet_sha256(self):
        with patch("ca_agents.mechanism_judge.call_claude", return_value=_PROFILE_RESPONSE):
            claude_artifact = run_claude_analysis(self.packet)
        with patch("gpt_mechanism_judge.judge.call_openai", return_value=_PROFILE_RESPONSE):
            gpt_artifact = run_gpt_analysis(self.packet)
        self.assertEqual(claude_artifact.input_packet_sha256, gpt_artifact.input_packet_sha256)
        self.assertEqual(claude_artifact.input_packet_sha256, packet_sha256(self.packet))

    def test_providers_and_models_are_correctly_attributed(self):
        with patch("ca_agents.mechanism_judge.call_claude", return_value=_PROFILE_RESPONSE):
            claude_artifact = run_claude_analysis(self.packet)
        with patch("gpt_mechanism_judge.judge.call_openai", return_value=_PROFILE_RESPONSE):
            gpt_artifact = run_gpt_analysis(self.packet)
        self.assertEqual(claude_artifact.provider, "anthropic")
        self.assertEqual(gpt_artifact.provider, "openai")
        self.assertNotEqual(claude_artifact.model, gpt_artifact.model)

    def test_analysis_payload_never_contains_the_other_providers_field_values(self):
        """A cheap but concrete cross-contamination check: GPT's mocked
        response text must never appear inside Claude's persisted
        analysis, and vice versa."""
        claude_response = json.dumps({**json.loads(_PROFILE_RESPONSE), "repair": "CLAUDE_ONLY_MARKER"})
        gpt_response = json.dumps({**json.loads(_PROFILE_RESPONSE), "repair": "GPT_ONLY_MARKER"})
        with patch("ca_agents.mechanism_judge.call_claude", return_value=claude_response):
            claude_artifact = run_claude_analysis(self.packet)
        with patch("gpt_mechanism_judge.judge.call_openai", return_value=gpt_response):
            gpt_artifact = run_gpt_analysis(self.packet)
        self.assertEqual(claude_artifact.analysis["repair"], "CLAUDE_ONLY_MARKER")
        self.assertEqual(gpt_artifact.analysis["repair"], "GPT_ONLY_MARKER")
        self.assertNotIn("GPT_ONLY_MARKER", json.dumps(claude_artifact.to_dict()))
        self.assertNotIn("CLAUDE_ONLY_MARKER", json.dumps(gpt_artifact.to_dict()))


@unittest.skipUnless(os.path.exists(CA_ANOMALIES_PATH), "real CA anomalies.json not present")
@unittest.skipUnless(os.path.exists(CA_OBSERVATIONS_PATH), "real CA observations.jsonl not present")
class CredentialFailuresPropagateLoudlyTests(unittest.TestCase):
    """Task §5: a missing secret must fail loudly, never degrade into
    INSUFFICIENT_DATA."""

    def test_missing_anthropic_key_raises_llmerror(self):
        from ca_agents.llm import LLMError
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(LLMError):
                run_claude_analysis(_load_real_packet())

    def test_missing_openai_key_raises_openaierror(self):
        from gpt_mechanism_judge.openai_client import OpenAIError
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(OpenAIError):
                run_gpt_analysis(_load_real_packet())


if __name__ == "__main__":
    unittest.main()
