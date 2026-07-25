import _pathsetup  # noqa: F401
import tempfile
import unittest
from pathlib import Path

from reality_sensor.config import RelevanceGateConfig, RelevanceRule
from reality_sensor.models import Category, Confidence, Project, RawCapture, TrustLevel
from reality_sensor.registry import build_signal, load_registry, save_registry, upsert

_RELEVANCE = RelevanceGateConfig(rules=[RelevanceRule(project=Project.DISCOVERY_LAB, keywords=["mcp"])])


def _capture(**overrides):
    base = dict(
        source_name="MCP Docs",
        source_url="https://modelcontextprotocol.io/",
        source_trust=TrustLevel.PRIMARY,
        category=Category.AGENT_INFRASTRUCTURE,
        captured_at="2026-07-20T00:00:00Z",
        title="MCP 2.0 released",
        raw_text="MCP 2.0 adds streaming tool results.",
        affected_capability="MCP streaming tool results",
        capability_keywords=["mcp", "streaming"],
    )
    base.update(overrides)
    return RawCapture(**base)


class TestEvidenceEnforcement(unittest.TestCase):
    def test_signal_with_evidence_is_not_insufficient(self):
        signal = build_signal([_capture()], _RELEVANCE)
        self.assertNotEqual(signal.confidence, Confidence.INSUFFICIENT_EVIDENCE)
        self.assertGreaterEqual(len(signal.evidence), 1)

    def test_every_evidence_entry_is_citable(self):
        signal = build_signal([_capture(), _capture(source_name="Second Source")], _RELEVANCE)
        for citation in signal.evidence_citations():
            self.assertIn("http", citation)


class TestFactVsInterpretationSeparation(unittest.TestCase):
    def test_evidence_quoted_text_is_never_the_signals_own_interpretation(self):
        # EXEC-008: "Strict separation: FACT -> CLAIM -> EVIDENCE ->
        # INTERPRETATION -> ACTION. Never merge these." Evidence.quoted_text
        # must come only from the source's own raw_text, never from the
        # Signal's own summary/practical_impact/recommended_action - those
        # live in structurally separate fields.
        signal = build_signal([_capture(practical_impact_note="This could speed up agent tool calls.")], _RELEVANCE)
        for e in signal.evidence:
            self.assertNotIn(signal.recommended_action, e.quoted_text)
            self.assertNotIn(signal.summary, e.quoted_text)

    def test_summary_and_practical_impact_are_distinct_fields(self):
        signal = build_signal([_capture(practical_impact_note="Impact note here.")], _RELEVANCE)
        self.assertNotEqual(signal.summary, signal.practical_impact)
        self.assertEqual(signal.practical_impact, "Impact note here.")


class TestStableIds(unittest.TestCase):
    def test_same_key_reuses_id_across_runs(self):
        signal1 = build_signal([_capture()], _RELEVANCE)
        records = upsert(signal1, [], "2026-07-20T00:00:00Z")
        first_id = records[0].signal_id

        signal2 = build_signal([_capture()], _RELEVANCE)  # identical content, new run
        records = upsert(signal2, records, "2026-07-21T00:00:00Z")

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].signal_id, first_id)
        self.assertEqual(records[0].times_seen, 2)

    def test_different_capability_gets_a_new_id(self):
        records = upsert(build_signal([_capture()], _RELEVANCE), [], "2026-07-20T00:00:00Z")
        other = _capture(affected_capability="unrelated capability", capability_keywords=["other"])
        records = upsert(build_signal([other], _RELEVANCE), records, "2026-07-20T00:00:00Z")
        self.assertEqual(len(records), 2)
        self.assertNotEqual(records[0].signal_id, records[1].signal_id)

    def test_ids_are_sequential_rs_prefixed(self):
        records = upsert(build_signal([_capture()], _RELEVANCE), [], "2026-07-20T00:00:00Z")
        other = _capture(affected_capability="second capability", capability_keywords=["second"])
        records = upsert(build_signal([other], _RELEVANCE), records, "2026-07-20T00:00:00Z")
        self.assertEqual({r.signal_id for r in records}, {"RS-0001", "RS-0002"})


class TestRegressionAgainstSelfGeneratedReports(unittest.TestCase):
    """Mirrors EXEC-006's own lesson: feeding a tool's prior output back
    into itself must never silently grow the registry. Here that means
    re-processing the *same* raw captures against an already-populated
    registry must not create a duplicate signal."""

    def test_reprocessing_same_captures_against_existing_registry_stays_flat(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry_path = Path(tmp) / "signal-registry.json"

            records = []
            for run_ts in ("2026-07-20T00:00:00Z", "2026-07-21T00:00:00Z", "2026-07-22T00:00:00Z"):
                records = load_registry(registry_path)
                signal = build_signal([_capture()], _RELEVANCE)
                records = upsert(signal, records, run_ts)
                save_registry(registry_path, records)

            final = load_registry(registry_path)
            self.assertEqual(len(final), 1)
            self.assertEqual(final[0].times_seen, 3)
            self.assertEqual(final[0].signal_id, "RS-0001")


if __name__ == "__main__":
    unittest.main()
