"""Task §12: 'deterministic disagreement detection', 'no semantic
decision in disagreement extractor'. Uses the real, already-durably-
persisted run 32142997999 (blind-analysis-kernel/data/analyses.jsonl) as
the primary acceptance case, plus synthetic edge cases.
"""

import _pathsetup  # noqa: F401
import inspect
import json
import os
import unittest

from adversarial_review_kernel.disagree import extract_disagreements
from adversarial_review_kernel.models import COMPARED_FIELDS, Disagreement

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ANALYSES_LEDGER = os.path.join(REPO_ROOT, "blind-analysis-kernel", "data", "analyses.jsonl")
REAL_RUN_ID = "32142997999"


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


class NoSemanticDecisionTests(unittest.TestCase):
    """The extractor must be structurally incapable of deciding
    correctness - proven by inspecting its own return type and
    signature, not just by convention."""

    def test_disagreement_dataclass_has_no_verdict_shaped_field(self):
        from dataclasses import fields
        field_names = {f.name for f in fields(Disagreement)}
        for forbidden in ("material", "classification", "correct", "verdict", "winner"):
            self.assertNotIn(forbidden, field_names)

    def test_extract_disagreements_signature_takes_no_evidence_parameter(self):
        """The extractor cannot possibly weigh evidence - it never
        receives any (no packet, no source text - only the two analysis
        dicts and their ids)."""
        params = list(inspect.signature(extract_disagreements).parameters)
        self.assertEqual(params, ["claude_analysis", "gpt_analysis", "claude_artifact_id", "gpt_artifact_id"])

    def test_only_compares_the_task_defined_field_set(self):
        claude = {"anomaly_id": "x", **{f: "claude" for f in COMPARED_FIELDS}}
        gpt = {"anomaly_id": "y", **{f: "gpt" for f in COMPARED_FIELDS}}
        result = extract_disagreements(claude, gpt, claude_artifact_id="c", gpt_artifact_id="g")
        # anomaly_id differs too but is NOT in COMPARED_FIELDS - must not appear.
        self.assertEqual({d.field for d in result}, set(COMPARED_FIELDS))


class SyntheticDisagreementTests(unittest.TestCase):
    def test_identical_analyses_produce_no_disagreements(self):
        analysis = {f: "same" for f in COMPARED_FIELDS}
        result = extract_disagreements(analysis, dict(analysis), claude_artifact_id="c", gpt_artifact_id="g")
        self.assertEqual(result, [])

    def test_single_field_difference_produces_exactly_one_disagreement(self):
        claude = {f: "same" for f in COMPARED_FIELDS}
        gpt = dict(claude)
        gpt["carrier"] = "different"
        result = extract_disagreements(claude, gpt, claude_artifact_id="c", gpt_artifact_id="g")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].field, "carrier")
        self.assertEqual(result[0].claude_value, "same")
        self.assertEqual(result[0].gpt_value, "different")

    def test_confidence_float_inequality_is_detected(self):
        claude = {f: "same" for f in COMPARED_FIELDS}
        gpt = dict(claude)
        claude["confidence"] = 0.92
        gpt["confidence"] = 0.0
        result = extract_disagreements(claude, gpt, claude_artifact_id="c", gpt_artifact_id="g")
        self.assertEqual([d.field for d in result], ["confidence"])

    def test_artifact_ids_are_carried_through_unchanged(self):
        claude = {f: "x" for f in COMPARED_FIELDS}
        gpt = {f: "y" for f in COMPARED_FIELDS}
        result = extract_disagreements(claude, gpt, claude_artifact_id="analysis:AAA", gpt_artifact_id="analysis:BBB")
        for d in result:
            self.assertEqual(d.claude_artifact_id, "analysis:AAA")
            self.assertEqual(d.gpt_artifact_id, "analysis:BBB")


@unittest.skipUnless(os.path.exists(ANALYSES_LEDGER), f"{ANALYSES_LEDGER} not present")
class RealRunDisagreementTests(unittest.TestCase):
    """The real, durably-persisted disagreement from run 32142997999 -
    the task's own primary acceptance case (§2/§11)."""

    def setUp(self):
        self.claude, self.gpt = _load_real_pair()
        self.assertIsNotNone(self.claude, "real claude artifact for run 32142997999 not found")
        self.assertIsNotNone(self.gpt, "real gpt artifact for run 32142997999 not found")

    def test_real_run_has_the_expected_carrier_and_confidence_disagreement(self):
        result = extract_disagreements(self.claude["analysis"], self.gpt["analysis"],
                                        claude_artifact_id=self.claude["artifact_id"],
                                        gpt_artifact_id=self.gpt["artifact_id"])
        fields = {d.field for d in result}
        self.assertIn("carrier", fields)
        self.assertIn("confidence", fields)
        # failure_class agreed (both "latency") in the real run - must NOT appear.
        self.assertNotIn("failure_class", fields)

    def test_real_carrier_disagreement_values_match_the_durable_record(self):
        result = extract_disagreements(self.claude["analysis"], self.gpt["analysis"],
                                        claude_artifact_id=self.claude["artifact_id"],
                                        gpt_artifact_id=self.gpt["artifact_id"])
        carrier = next(d for d in result if d.field == "carrier")
        self.assertIn("Probabilistic programming language", carrier.claude_value)
        self.assertEqual(carrier.gpt_value, "Developer working on personal project since 2018")

    def test_real_disagreement_carries_the_real_artifact_ids(self):
        result = extract_disagreements(self.claude["analysis"], self.gpt["analysis"],
                                        claude_artifact_id=self.claude["artifact_id"],
                                        gpt_artifact_id=self.gpt["artifact_id"])
        for d in result:
            self.assertEqual(d.claude_artifact_id, "analysis:d8cb132a5bb53cbc89853a01f00006d3")
            self.assertEqual(d.gpt_artifact_id, "analysis:0e06c0de4e91c1868ee9664851c3ba8a")


if __name__ == "__main__":
    unittest.main()
