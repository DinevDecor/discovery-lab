"""Task §4/§12: cross-falsification blindness, proven offline against
the real, already-committed run 32142997999 data. `call_claude`/
`call_openai` are mocked - no real network call.
"""

import _pathsetup  # noqa: F401
import inspect
import json
import os
import unittest
from unittest.mock import patch

from adversarial_review_kernel.disagree import extract_disagreements
from adversarial_review_kernel.falsify import build_falsifier_packet, run_claude_falsifier, run_gpt_falsifier
from adversarial_review_kernel.models import COMPARED_FIELDS

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ANALYSES_LEDGER = os.path.join(REPO_ROOT, "blind-analysis-kernel", "data", "analyses.jsonl")
CA_ANOMALIES_PATH = os.path.join(REPO_ROOT, "constraint-archaeology-agents", "data", "anomalies.json")
CA_OBSERVATIONS_PATH = os.path.join(REPO_ROOT, "constraint-archaeology-agents", "data", "observations.jsonl")
REAL_RUN_ID = "32142997999"

_FALSIFIER_RESPONSE_TEMPLATE = json.dumps({"findings": [
    {"field": f, "classification": "SUPPORTED_BY_SOURCE", "reason": "r", "material": False}
    for f in ("hidden_function", "inputs", "outputs", "carrier", "failure_mechanism", "repair", "confidence")
]})


def _load_real_pair():
    claude = gpt = None
    with open(ANALYSES_LEDGER, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if row.get("run_id") != REAL_RUN_ID:
                continue
            if row["provider"] == "anthropic":
                claude = row
            elif row["provider"] == "openai":
                gpt = row
    return claude, gpt


def _load_anomaly_and_observations():
    with open(CA_ANOMALIES_PATH, encoding="utf-8") as f:
        anomalies = {a["anomaly_id"]: a for a in json.load(f)}
    observations = {}
    with open(CA_OBSERVATIONS_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                o = json.loads(line)
                observations[o["observation_id"]] = o
    return anomalies["ANOM-0001"], observations


@unittest.skipUnless(os.path.exists(ANALYSES_LEDGER), f"{ANALYSES_LEDGER} not present")
@unittest.skipUnless(os.path.exists(CA_ANOMALIES_PATH), f"{CA_ANOMALIES_PATH} not present")
class FalsifierSignatureTests(unittest.TestCase):
    """Structural proof: neither function has a parameter through which
    the critic's own prior analysis, or the other Falsifier's output,
    could arrive."""

    def test_run_claude_falsifier_has_no_claude_analysis_parameter(self):
        params = list(inspect.signature(run_claude_falsifier).parameters)
        self.assertEqual(params, ["packet", "gpt_analysis", "gpt_artifact_id", "disagreements"])
        for forbidden in ("claude_analysis", "claude_artifact", "claude_falsification", "gpt_falsification"):
            self.assertNotIn(forbidden, params)

    def test_run_gpt_falsifier_has_no_gpt_analysis_parameter(self):
        params = list(inspect.signature(run_gpt_falsifier).parameters)
        self.assertEqual(params, ["packet", "claude_analysis", "claude_artifact_id", "disagreements"])
        for forbidden in ("gpt_analysis", "gpt_artifact", "gpt_falsification", "claude_falsification"):
            self.assertNotIn(forbidden, params)


@unittest.skipUnless(os.path.exists(ANALYSES_LEDGER), f"{ANALYSES_LEDGER} not present")
@unittest.skipUnless(os.path.exists(CA_ANOMALIES_PATH), f"{CA_ANOMALIES_PATH} not present")
class RealRunFalsificationBlindnessTests(unittest.TestCase):
    def setUp(self):
        self.claude, self.gpt = _load_real_pair()
        anomaly, observations = _load_anomaly_and_observations()
        self.packet = build_falsifier_packet(anomaly, observations, REAL_RUN_ID)
        self.disagreements = extract_disagreements(
            self.claude["analysis"], self.gpt["analysis"],
            claude_artifact_id=self.claude["artifact_id"], gpt_artifact_id=self.gpt["artifact_id"],
        )

    def test_claude_falsifier_never_calls_the_openai_transport(self):
        with patch("adversarial_review_kernel.falsify.call_claude",
                   return_value=_FALSIFIER_RESPONSE_TEMPLATE) as mock_claude, \
             patch("adversarial_review_kernel.falsify.call_openai") as mock_openai:
            run_claude_falsifier(self.packet, self.gpt["analysis"], self.gpt["artifact_id"], self.disagreements)
        mock_claude.assert_called_once()
        mock_openai.assert_not_called()

    def test_gpt_falsifier_never_calls_the_anthropic_transport(self):
        with patch("adversarial_review_kernel.falsify.call_openai",
                   return_value=_FALSIFIER_RESPONSE_TEMPLATE) as mock_openai, \
             patch("adversarial_review_kernel.falsify.call_claude") as mock_claude:
            run_gpt_falsifier(self.packet, self.claude["analysis"], self.claude["artifact_id"], self.disagreements)
        mock_openai.assert_called_once()
        mock_claude.assert_not_called()

    def test_claude_falsifier_never_receives_claudes_own_original_value(self):
        """Real, concrete proof: Claude's own real carrier text
        ('Probabilistic programming language...') must never appear in
        the prompt sent to call_claude when Claude is critiquing GPT."""
        captured = {}

        def _capture(system, prompt, max_tokens=1400):
            captured["prompt"] = prompt
            return _FALSIFIER_RESPONSE_TEMPLATE

        with patch("adversarial_review_kernel.falsify.call_claude", side_effect=_capture):
            run_claude_falsifier(self.packet, self.gpt["analysis"], self.gpt["artifact_id"], self.disagreements)

        claude_carrier = self.claude["analysis"]["carrier"]
        self.assertNotIn(claude_carrier, captured["prompt"],
                          "Claude's own original carrier value leaked into its own Falsifier prompt")
        # GPT's value (the thing under review) SHOULD be present.
        self.assertIn(self.gpt["analysis"]["carrier"], captured["prompt"])

    def test_gpt_falsifier_never_receives_gpts_own_original_value(self):
        """Uses SYNTHETIC analysis dicts with a distinctive marker value,
        not the real persisted pair: GPT's real `carrier` text happens to
        equal the packet's own raw `current_carrier` evidence field
        (GPT literally echoed the input - itself evidence of the real
        schema ambiguity), so a blanket substring check against real data
        false-positives on that legitimately-shown raw-evidence section.
        A synthetic marker can never coincidentally collide with real
        evidence text, so it isolates the actual blindness property."""
        gpt_own_marker = "GPT_OWN_CARRIER_MARKER_7c1e"
        claude_target_marker = "CLAUDE_TARGET_CARRIER_MARKER_4b92"
        gpt_analysis = dict(self.gpt["analysis"])
        gpt_analysis["carrier"] = gpt_own_marker
        claude_analysis = dict(self.claude["analysis"])
        claude_analysis["carrier"] = claude_target_marker
        disagreements = extract_disagreements(
            claude_analysis, gpt_analysis,
            claude_artifact_id=self.claude["artifact_id"], gpt_artifact_id=self.gpt["artifact_id"],
        )

        captured = {}

        def _capture(system, prompt, max_tokens=1400):
            captured["prompt"] = prompt
            return _FALSIFIER_RESPONSE_TEMPLATE

        with patch("adversarial_review_kernel.falsify.call_openai", side_effect=_capture):
            run_gpt_falsifier(self.packet, claude_analysis, self.claude["artifact_id"], disagreements)

        self.assertNotIn(gpt_own_marker, captured["prompt"],
                          "GPT's own original carrier value leaked into its own Falsifier prompt")
        # Claude's value (the thing under review) SHOULD be present.
        self.assertIn(claude_target_marker, captured["prompt"])

    def test_neither_falsifier_sees_the_others_critique(self):
        """Distinctive markers embedded in each mocked Falsifier's own
        RESPONSE text (never the prompt template's own JSON-format
        instructions, which both prompts legitimately share) prove no
        shared mutable state threads one Falsifier's output into the
        other's prompt. Claude's Falsifier runs first; if its response
        text somehow leaked into GPT's later call, GPT's marker (which
        does not exist until AFTER Claude's call returns) could not
        appear in Claude's own prompt, and Claude's marker could not
        appear in GPT's prompt unless the response object itself were
        threaded through - which neither function's signature permits
        (see FalsifierSignatureTests)."""
        claude_response_marker = "CLAUDE_FALSIFIER_RESPONSE_MARKER_9f3d"
        gpt_response_marker = "GPT_FALSIFIER_RESPONSE_MARKER_2a71"
        claude_response = json.dumps({"findings": [
            {"field": f, "classification": "SUPPORTED_BY_SOURCE", "reason": claude_response_marker, "material": False}
            for f in COMPARED_FIELDS
        ]})
        gpt_response = json.dumps({"findings": [
            {"field": f, "classification": "SUPPORTED_BY_SOURCE", "reason": gpt_response_marker, "material": False}
            for f in COMPARED_FIELDS
        ]})

        captured = {}

        def _capture_claude(system, prompt, max_tokens=1400):
            captured["claude_prompt"] = prompt
            return claude_response

        def _capture_gpt(system, prompt, max_tokens=1400):
            captured["gpt_prompt"] = prompt
            return gpt_response

        with patch("adversarial_review_kernel.falsify.call_claude", side_effect=_capture_claude):
            run_claude_falsifier(self.packet, self.gpt["analysis"], self.gpt["artifact_id"], self.disagreements)
        with patch("adversarial_review_kernel.falsify.call_openai", side_effect=_capture_gpt):
            run_gpt_falsifier(self.packet, self.claude["analysis"], self.claude["artifact_id"], self.disagreements)

        # GPT's response marker did not exist yet when Claude's prompt was
        # built, so its absence there is trivially guaranteed; the real
        # proof is that it is ALSO absent from GPT's own prompt (nothing
        # ever feeds a prior response's text back into a later prompt).
        self.assertNotIn(gpt_response_marker, captured["claude_prompt"])
        self.assertNotIn(claude_response_marker, captured["gpt_prompt"])
        self.assertNotIn(gpt_response_marker, captured["gpt_prompt"])
        self.assertNotIn(claude_response_marker, captured["claude_prompt"])

    def test_both_falsifiers_report_the_same_input_packet_sha256(self):
        with patch("adversarial_review_kernel.falsify.call_claude", return_value=_FALSIFIER_RESPONSE_TEMPLATE):
            claude_fals = run_claude_falsifier(self.packet, self.gpt["analysis"], self.gpt["artifact_id"],
                                                self.disagreements)
        with patch("adversarial_review_kernel.falsify.call_openai", return_value=_FALSIFIER_RESPONSE_TEMPLATE):
            gpt_fals = run_gpt_falsifier(self.packet, self.claude["analysis"], self.claude["artifact_id"],
                                          self.disagreements)
        self.assertEqual(claude_fals.input_packet_sha256, gpt_fals.input_packet_sha256)

    def test_falsification_targets_are_correctly_the_opposite_provider(self):
        with patch("adversarial_review_kernel.falsify.call_claude", return_value=_FALSIFIER_RESPONSE_TEMPLATE):
            claude_fals = run_claude_falsifier(self.packet, self.gpt["analysis"], self.gpt["artifact_id"],
                                                self.disagreements)
        with patch("adversarial_review_kernel.falsify.call_openai", return_value=_FALSIFIER_RESPONSE_TEMPLATE):
            gpt_fals = run_gpt_falsifier(self.packet, self.claude["analysis"], self.claude["artifact_id"],
                                          self.disagreements)
        self.assertEqual(claude_fals.target_artifact_id, self.gpt["artifact_id"])
        self.assertEqual(gpt_fals.target_artifact_id, self.claude["artifact_id"])
        self.assertEqual(claude_fals.critic_provider, "anthropic")
        self.assertEqual(gpt_fals.critic_provider, "openai")


@unittest.skipUnless(os.path.exists(ANALYSES_LEDGER), f"{ANALYSES_LEDGER} not present")
@unittest.skipUnless(os.path.exists(CA_ANOMALIES_PATH), f"{CA_ANOMALIES_PATH} not present")
class SchemaAmbiguityVsFalsificationTests(unittest.TestCase):
    """Task §12: 'schema ambiguity != falsification'."""

    def setUp(self):
        self.claude, self.gpt = _load_real_pair()
        anomaly, observations = _load_anomaly_and_observations()
        self.packet = build_falsifier_packet(anomaly, observations, REAL_RUN_ID)
        self.disagreements = extract_disagreements(
            self.claude["analysis"], self.gpt["analysis"],
            claude_artifact_id=self.claude["artifact_id"], gpt_artifact_id=self.gpt["artifact_id"],
        )

    def test_schema_ambiguity_classification_is_distinct_from_challenged(self):
        response = json.dumps({"findings": [
            {"field": d.field, "classification": "SCHEMA_AMBIGUITY" if d.field == "carrier" else "SUPPORTED_BY_SOURCE",
             "reason": "r", "material": d.field == "carrier"}
            for d in self.disagreements
        ]})
        with patch("adversarial_review_kernel.falsify.call_claude", return_value=response):
            artifact = run_claude_falsifier(self.packet, self.gpt["analysis"], self.gpt["artifact_id"],
                                             self.disagreements)
        carrier_finding = next(f for f in artifact.findings if f.field == "carrier")
        self.assertEqual(carrier_finding.classification, "SCHEMA_AMBIGUITY")
        other_findings = [f for f in artifact.findings if f.field != "carrier"]
        for f in other_findings:
            self.assertNotEqual(f.classification, "SCHEMA_AMBIGUITY")


if __name__ == "__main__":
    unittest.main()
