import _pathsetup  # noqa: F401
import unittest

from research_sensor.experiments import build_experiments, is_high_value
from research_sensor.models import Confidence, Domain, EvidenceLevel, Project, RawPaperCapture, SourceTrust

_REQUIRED_KEYS = ("description", "expected_benefit", "uncertainty", "prerequisites", "validation_idea")


def _capture(notes):
    return RawPaperCapture(
        title="T",
        authors=["A"],
        publication="arXiv",
        date="2026-07-10",
        source_name="arXiv cs.AI Recent",
        source_url="https://arxiv.org/abs/x",
        source_trust=SourceTrust.PRIMARY,
        evidence_level=EvidenceLevel.NOTABLE_LAB_PREPRINT,
        domain=Domain.AI_FOR_SCIENTIFIC_DISCOVERY,
        raw_abstract="abstract",
        problem_addressed="problem",
        main_contribution="contribution",
        possible_experiment_notes=notes,
    )


class TestExperimentExtractionStructure(unittest.TestCase):
    def test_well_formed_note_produces_an_experiment(self):
        note = {
            "description": "Try the method on KOD's registry data",
            "expected_benefit": "faster retrieval",
            "uncertainty": "unclear if it generalizes past small registries",
            "prerequisites": "a sample of KOD registry data",
            "validation_idea": "measure retrieval latency before/after",
        }
        experiments = build_experiments([_capture([note])])
        self.assertEqual(len(experiments), 1)
        for key in _REQUIRED_KEYS:
            self.assertTrue(getattr(experiments[0], key))

    def test_incomplete_note_is_dropped_not_invented(self):
        # EXEC-010: "Do not generate implementation plans... do not
        # invent experiment content the capture step didn't supply."
        incomplete = {"description": "Try something", "expected_benefit": "faster retrieval"}
        experiments = build_experiments([_capture([incomplete])])
        self.assertEqual(experiments, [])

    def test_multiple_captures_can_each_contribute_experiments(self):
        note_a = {k: f"a-{k}" for k in _REQUIRED_KEYS}
        note_b = {k: f"b-{k}" for k in _REQUIRED_KEYS}
        experiments = build_experiments([_capture([note_a]), _capture([note_b])])
        self.assertEqual(len(experiments), 2)

    def test_no_notes_gives_no_experiments(self):
        self.assertEqual(build_experiments([_capture([])]), [])

    def test_experiment_never_contains_implementation_plan_fields(self):
        # Structural guarantee: PossibleExperiment has no field for
        # code, file paths, or task lists - not just a convention.
        note = {k: f"v-{k}" for k in _REQUIRED_KEYS}
        experiments = build_experiments([_capture([note])])
        experiment_fields = set(vars(experiments[0]).keys())
        self.assertEqual(experiment_fields, set(_REQUIRED_KEYS))


class TestHighValueGating(unittest.TestCase):
    def test_watch_only_is_never_high_value(self):
        self.assertFalse(is_high_value([Project.WATCH], Confidence.HIGH))

    def test_named_project_with_high_confidence_is_high_value(self):
        self.assertTrue(is_high_value([Project.KOD], Confidence.HIGH))

    def test_named_project_with_insufficient_evidence_is_not_high_value(self):
        self.assertFalse(is_high_value([Project.KOD], Confidence.INSUFFICIENT_EVIDENCE))


if __name__ == "__main__":
    unittest.main()
