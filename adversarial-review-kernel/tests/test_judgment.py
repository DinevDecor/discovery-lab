"""Task §7/§12: the deterministic Judge. Every test here constructs its
own FalsificationArtifacts by hand (no model call, no mocking needed -
`decide()` takes already-computed data) and asserts the resulting
JudgmentArtifact.status.
"""

import _pathsetup  # noqa: F401
import re
import unittest
from pathlib import Path

from adversarial_review_kernel.judgment import decide
from adversarial_review_kernel.models import (
    ADVANCE,
    CHALLENGED_BY_SOURCE,
    INSUFFICIENT_DATA,
    REJECT,
    SCHEMA_AMBIGUITY,
    SUPPORTED_BY_SOURCE,
    WATCH,
    Disagreement,
    FalsificationArtifact,
    FalsificationFinding,
)

_HASH = "a" * 64
CLAUDE_ID = "analysis:claude"
GPT_ID = "analysis:gpt"


def _finding(field, classification, material, target=GPT_ID):
    return FalsificationFinding(field=field, target_analysis_artifact_id=target,
                                 classification=classification, reason="r",
                                 source_artifact_ids=["OBS-1"], material=material)


def _falsification(critic_provider, critic_model, target_artifact_id, findings):
    return FalsificationArtifact(
        artifact_id=f"falsification:{critic_provider}", run_id="run-1",
        critic_provider=critic_provider, critic_model=critic_model,
        target_artifact_id=target_artifact_id, source_case_ids=["case:abc"],
        input_packet_sha256=_HASH, findings=findings, created_at="2026-08-18T00:00:00Z",
    )


def _decide(disagreements, claude_findings, gpt_findings):
    """claude_findings = Claude-Falsifier's findings ABOUT GPT's analysis
    (target=GPT_ID). gpt_findings = GPT-Falsifier's findings ABOUT
    Claude's analysis (target=CLAUDE_ID)."""
    claude_fals = _falsification("anthropic", "claude-sonnet-4-5", GPT_ID, claude_findings)
    gpt_fals = _falsification("openai", "gpt-4.1", CLAUDE_ID, gpt_findings)
    return decide(judgment_id="judgment:run-1", case_id="case:abc", source_run_id="run-1",
                  claude_artifact_id=CLAUDE_ID, gpt_artifact_id=GPT_ID,
                  disagreements=disagreements, claude_falsification=claude_fals,
                  gpt_falsification=gpt_fals, created_at="2026-08-18T00:00:00Z")


def _disagreement(field):
    return Disagreement(field=field, claude_value="c", gpt_value="g",
                         claude_artifact_id=CLAUDE_ID, gpt_artifact_id=GPT_ID)


class AdvanceTests(unittest.TestCase):
    def test_no_disagreements_advances(self):
        result = _decide([], [], [])
        self.assertEqual(result.status, ADVANCE)

    def test_disagreement_but_neither_side_marks_material_advances(self):
        result = _decide(
            [_disagreement("repair")],
            [_finding("repair", SUPPORTED_BY_SOURCE, material=False)],
            [_finding("repair", SUPPORTED_BY_SOURCE, material=False, target=CLAUDE_ID)],
        )
        self.assertEqual(result.status, ADVANCE)
        self.assertEqual(result.material_disagreements, [])
        self.assertEqual(result.schema_ambiguities, [])


class WatchTests(unittest.TestCase):
    def test_material_schema_ambiguity_caps_at_watch(self):
        """The real run's own carrier finding shape."""
        result = _decide(
            [_disagreement("carrier")],
            [_finding("carrier", SCHEMA_AMBIGUITY, material=True)],
            [_finding("carrier", SCHEMA_AMBIGUITY, material=True, target=CLAUDE_ID)],
        )
        self.assertEqual(result.status, WATCH)
        self.assertEqual(result.schema_ambiguities, ["carrier"])
        self.assertEqual(result.material_disagreements, [])

    def test_material_insufficient_data_watches_not_rejects(self):
        result = _decide(
            [_disagreement("confidence")],
            [_finding("confidence", INSUFFICIENT_DATA, material=True)],
            [_finding("confidence", SUPPORTED_BY_SOURCE, material=False, target=CLAUDE_ID)],
        )
        self.assertEqual(result.status, WATCH)
        self.assertEqual(result.material_disagreements, ["confidence"])

    def test_both_sides_supported_by_source_but_material_still_watches(self):
        """Genuine evidence-grounded disagreement - both readings
        independently defensible from source - is unresolved, not a hard
        falsification of either."""
        result = _decide(
            [_disagreement("hidden_function")],
            [_finding("hidden_function", SUPPORTED_BY_SOURCE, material=True)],
            [_finding("hidden_function", SUPPORTED_BY_SOURCE, material=True, target=CLAUDE_ID)],
        )
        self.assertEqual(result.status, WATCH)
        self.assertEqual(result.material_disagreements, ["hidden_function"])

    def test_schema_ambiguity_on_one_field_caps_watch_even_with_clean_other_fields(self):
        result = _decide(
            [_disagreement("carrier"), _disagreement("repair")],
            [_finding("carrier", SCHEMA_AMBIGUITY, material=True),
             _finding("repair", SUPPORTED_BY_SOURCE, material=False)],
            [_finding("carrier", SCHEMA_AMBIGUITY, material=True, target=CLAUDE_ID),
             _finding("repair", SUPPORTED_BY_SOURCE, material=False, target=CLAUDE_ID)],
        )
        self.assertEqual(result.status, WATCH)
        self.assertEqual(result.schema_ambiguities, ["carrier"])


class RejectTests(unittest.TestCase):
    def test_material_challenged_by_source_with_no_ambiguity_rejects(self):
        result = _decide(
            [_disagreement("failure_mechanism")],
            [_finding("failure_mechanism", CHALLENGED_BY_SOURCE, material=True)],
            [_finding("failure_mechanism", SUPPORTED_BY_SOURCE, material=True, target=CLAUDE_ID)],
        )
        self.assertEqual(result.status, REJECT)
        self.assertIn("failure_mechanism", result.reasons[0])

    def test_challenged_but_also_schema_ambiguous_on_same_field_does_not_reject(self):
        """Task §6: an ambiguous-schema field cannot be a clean hard
        falsification - it caps at WATCH instead."""
        result = _decide(
            [_disagreement("carrier")],
            [_finding("carrier", CHALLENGED_BY_SOURCE, material=True)],
            [_finding("carrier", SCHEMA_AMBIGUITY, material=True, target=CLAUDE_ID)],
        )
        self.assertEqual(result.status, WATCH)
        self.assertEqual(result.schema_ambiguities, ["carrier"])

    def test_non_material_challenged_by_source_does_not_reject(self):
        result = _decide(
            [_disagreement("repair")],
            [_finding("repair", CHALLENGED_BY_SOURCE, material=False)],
            [_finding("repair", SUPPORTED_BY_SOURCE, material=False, target=CLAUDE_ID)],
        )
        self.assertEqual(result.status, ADVANCE)


class InsufficientDataNeverRejectTests(unittest.TestCase):
    def test_insufficient_data_alone_across_many_fields_never_rejects(self):
        fields = ["carrier", "confidence", "repair", "hidden_function"]
        result = _decide(
            [_disagreement(f) for f in fields],
            [_finding(f, INSUFFICIENT_DATA, material=True) for f in fields],
            [_finding(f, INSUFFICIENT_DATA, material=True, target=CLAUDE_ID) for f in fields],
        )
        self.assertNotEqual(result.status, REJECT)
        self.assertEqual(result.status, WATCH)

    def test_reject_condition_never_mentions_insufficient_data(self):
        """Structural proof: the only guard around `reject_triggers
        .append(...)` in judgment.py's source text is a
        CHALLENGED_BY_SOURCE check - INSUFFICIENT_DATA never appears on
        that guarding line."""
        import adversarial_review_kernel.judgment as judgment_module
        source = Path(judgment_module.__file__).read_text(encoding="utf-8")
        lines = source.splitlines()
        guard_lines = [lines[i - 1] for i, line in enumerate(lines) if "reject_triggers.append" in line]
        self.assertTrue(guard_lines, "no reject_triggers.append call found in judgment.py")
        for guard in guard_lines:
            self.assertIn("CHALLENGED_BY_SOURCE", guard)
            self.assertNotIn("INSUFFICIENT_DATA", guard)


class ArtifactShapeTests(unittest.TestCase):
    def test_reasons_are_never_empty(self):
        for result in (_decide([], [], []),
                       _decide([_disagreement("carrier")],
                               [_finding("carrier", SCHEMA_AMBIGUITY, material=True)],
                               [_finding("carrier", SCHEMA_AMBIGUITY, material=True, target=CLAUDE_ID)])):
            self.assertTrue(result.reasons)

    def test_source_analysis_artifact_ids_sorted_and_deduplicated(self):
        result = _decide([], [], [])
        self.assertEqual(result.source_analysis_artifact_ids, sorted({CLAUDE_ID, GPT_ID}))

    def test_source_falsification_artifact_ids_present(self):
        result = _decide([], [], [])
        self.assertEqual(len(result.source_falsification_artifact_ids), 2)


class NoModelOrNetworkCallTests(unittest.TestCase):
    """Task §12: 'deterministic judge contains no model/network call'."""

    _FORBIDDEN = [
        r"\bcall_claude\b", r"\bcall_openai\b", r"\burllib\b", r"\brequests\.",
        r"\bimport\s+ca_agents\b", r"\bimport\s+gpt_mechanism_judge\b",
        r"^\s*from\s+ca_agents\b", r"^\s*from\s+gpt_mechanism_judge\b",
    ]

    def test_judgment_module_has_no_model_or_network_reference(self):
        import adversarial_review_kernel.judgment as judgment_module
        source = Path(judgment_module.__file__).read_text(encoding="utf-8")
        for pattern in self._FORBIDDEN:
            self.assertIsNone(re.search(pattern, source, re.MULTILINE),
                               f"judgment.py contains forbidden pattern {pattern!r}")

    def test_decide_is_a_pure_function_same_input_same_output(self):
        args = ([_disagreement("carrier")],
                [_finding("carrier", SCHEMA_AMBIGUITY, material=True)],
                [_finding("carrier", SCHEMA_AMBIGUITY, material=True, target=CLAUDE_ID)])
        r1 = _decide(*args)
        r2 = _decide(*args)
        self.assertEqual(r1.status, r2.status)
        self.assertEqual(r1.material_disagreements, r2.material_disagreements)
        self.assertEqual(r1.schema_ambiguities, r2.schema_ambiguities)


if __name__ == "__main__":
    unittest.main()
