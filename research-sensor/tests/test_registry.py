import _pathsetup  # noqa: F401
import tempfile
import unittest
from pathlib import Path

from research_sensor.config import RelevanceGateConfig, RelevanceRule
from research_sensor.models import Confidence, Domain, EvidenceLevel, Project, RawPaperCapture, SourceTrust
from research_sensor.registry import build_signal, load_registry, save_registry, upsert

_RELEVANCE = RelevanceGateConfig(
    rules=[RelevanceRule(project=Project.KOD, keywords=["provenance"])]
)


def _capture(**overrides):
    base = dict(
        title="Provenance Tracking for Agentic Pipelines",
        authors=["A. Researcher", "B. Researcher"],
        publication="arXiv",
        date="2026-07-10",
        source_name="arXiv cs.AI Recent",
        source_url="https://arxiv.org/abs/2607.00001",
        source_trust=SourceTrust.PRIMARY,
        evidence_level=EvidenceLevel.NOTABLE_LAB_PREPRINT,
        domain=Domain.KNOWLEDGE_SYSTEMS,
        raw_abstract="We propose a provenance-tracking method for agentic pipelines.",
        problem_addressed="lack of provenance in agentic pipelines",
        main_contribution="a lightweight provenance tracker",
        idea_keywords=["provenance", "agentic"],
        architectural_relevance_note="Relevant to KOD's own provenance and retrieval needs.",
    )
    base.update(overrides)
    return RawPaperCapture(**base)


class TestEvidenceSeparation(unittest.TestCase):
    def test_signal_has_citable_evidence(self):
        signal = build_signal([_capture()], _RELEVANCE)
        self.assertIsNotNone(signal)
        self.assertGreaterEqual(len(signal.evidence), 1)
        for citation in signal.evidence_citations():
            self.assertIn("http", citation)

    def test_evidence_quoted_abstract_never_contains_the_signals_own_interpretation(self):
        signal = build_signal([_capture()], _RELEVANCE)
        for e in signal.evidence:
            self.assertNotIn(signal.recommended_action, e.quoted_abstract)
            self.assertNotIn(signal.architectural_relevance, e.quoted_abstract)

    def test_community_hint_only_cluster_is_not_a_signal(self):
        hint_only = _capture(source_trust=SourceTrust.COMMUNITY, evidence_level=EvidenceLevel.COMMUNITY_HINT)
        signal = build_signal([hint_only], _RELEVANCE)
        self.assertIsNone(signal)


class TestStableIds(unittest.TestCase):
    def test_same_key_reuses_id_across_runs(self):
        records = upsert(build_signal([_capture()], _RELEVANCE), [], "2026-07-20T00:00:00Z")
        first_id = records[0].research_id

        records = upsert(build_signal([_capture()], _RELEVANCE), records, "2026-07-21T00:00:00Z")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].research_id, first_id)
        self.assertEqual(records[0].times_seen, 2)

    def test_different_problem_gets_a_new_id(self):
        records = upsert(build_signal([_capture()], _RELEVANCE), [], "2026-07-20T00:00:00Z")
        other = _capture(problem_addressed="an unrelated problem", idea_keywords=["other"])
        records = upsert(build_signal([other], _RELEVANCE), records, "2026-07-20T00:00:00Z")
        self.assertEqual(len(records), 2)
        self.assertNotEqual(records[0].research_id, records[1].research_id)

    def test_ids_are_sequential_res_prefixed(self):
        records = upsert(build_signal([_capture()], _RELEVANCE), [], "2026-07-20T00:00:00Z")
        other = _capture(problem_addressed="second problem", idea_keywords=["second"])
        records = upsert(build_signal([other], _RELEVANCE), records, "2026-07-20T00:00:00Z")
        self.assertEqual({r.research_id for r in records}, {"RES-0001", "RES-0002"})


class TestResearchRegistryStabilityAndRegression(unittest.TestCase):
    """Regression against self-generated reports: reprocessing the same
    captures against an already-populated registry must not create a
    duplicate signal."""

    def test_reprocessing_same_captures_against_existing_registry_stays_flat(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry_path = Path(tmp) / "research-registry.json"

            records = []
            for run_ts in ("2026-07-20T00:00:00Z", "2026-07-21T00:00:00Z", "2026-07-22T00:00:00Z"):
                records = load_registry(registry_path)
                signal = build_signal([_capture()], _RELEVANCE)
                records = upsert(signal, records, run_ts)
                save_registry(registry_path, records)

            final = load_registry(registry_path)
            self.assertEqual(len(final), 1)
            self.assertEqual(final[0].times_seen, 3)
            self.assertEqual(final[0].research_id, "RES-0001")

    def test_saved_and_reloaded_registry_round_trips_experiments(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "research-registry.json"
            capture_with_experiment = _capture(
                possible_experiment_notes=[{
                    "description": "Apply the tracker to KOD's own retrieval pipeline",
                    "expected_benefit": "improved traceability",
                    "uncertainty": "overhead unknown at scale",
                    "prerequisites": "a KOD retrieval pipeline to instrument",
                    "validation_idea": "compare traceability coverage before/after",
                }]
            )
            records = upsert(build_signal([capture_with_experiment], _RELEVANCE), [], "2026-07-20T00:00:00Z")
            save_registry(path, records)
            reloaded = load_registry(path)
            self.assertEqual(len(reloaded[0].possible_experiments), 1)
            self.assertEqual(
                reloaded[0].possible_experiments[0].expected_benefit, "improved traceability"
            )


if __name__ == "__main__":
    unittest.main()
