"""Headquarters compatibility (EXEC-010 required test category):
proves research-registry.json is structurally readable the same
tolerant way headquarters/src/headquarters/collector.py already reads
every other artifact it consumes. Does not import or modify any
headquarters/ module."""

import _pathsetup  # noqa: F401
import json
import tempfile
import unittest
from pathlib import Path

from research_sensor.config import RelevanceGateConfig, RelevanceRule
from research_sensor.models import Domain, EvidenceLevel, Project, RawPaperCapture, SourceTrust
from research_sensor.registry import build_signal, save_registry, upsert

_REQUIRED_SIGNAL_FIELDS = {
    "research_id", "title", "authors", "publication", "date", "domain",
    "problem_addressed", "main_contribution", "evidence_level",
    "affected_projects", "possible_experiments", "architectural_relevance",
    "confidence", "recommended_action",
}


class TestHeadquartersCompatibility(unittest.TestCase):
    def test_registry_is_a_flat_json_list_of_objects(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "research-registry.json"
            relevance = RelevanceGateConfig(rules=[RelevanceRule(project=Project.KOD, keywords=["provenance"])])
            capture = RawPaperCapture(
                title="Provenance Tracking",
                authors=["A. Researcher"],
                publication="arXiv",
                date="2026-07-10",
                source_name="arXiv cs.AI Recent",
                source_url="https://arxiv.org/abs/x",
                source_trust=SourceTrust.PRIMARY,
                evidence_level=EvidenceLevel.NOTABLE_LAB_PREPRINT,
                domain=Domain.KNOWLEDGE_SYSTEMS,
                raw_abstract="abstract",
                problem_addressed="provenance problem",
                main_contribution="a tracker",
                idea_keywords=["provenance"],
            )
            records = upsert(build_signal([capture], relevance), [], "2026-07-20T00:00:00Z")
            save_registry(path, records)

            raw = json.loads(path.read_text(encoding="utf-8"))
            self.assertIsInstance(raw, list)
            for entry in raw:
                self.assertIsInstance(entry, dict)
                self.assertTrue(_REQUIRED_SIGNAL_FIELDS.issubset(entry.keys()))
                self.assertIsInstance(entry["affected_projects"], list)
                self.assertIsInstance(entry["possible_experiments"], list)
                self.assertIsInstance(entry["evidence"], list)

    def test_empty_registry_is_still_valid_json_a_reader_would_not_crash_on(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "research-registry.json"
            save_registry(path, [])
            raw = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(raw, [])


if __name__ == "__main__":
    unittest.main()
