import _pathsetup  # noqa: F401
import json
import tempfile
import unittest
from pathlib import Path

from research_sensor.cli import run_once

_SOURCE_REGISTRY = {
    "processing_budget": 10,
    "window_days": 30,
    "sources": [
        {
            "name": "arXiv cs.AI Recent",
            "url": "https://arxiv.org/list/cs.AI/recent",
            "source_trust": "PRIMARY",
            "domain_hint": "A",
        }
    ],
}
_RELEVANCE_GATE = {"rules": [{"project": "KOD", "keywords": ["provenance"]}]}


def _write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data), encoding="utf-8")


def _paper(**overrides):
    base = {
        "title": "Provenance Tracking",
        "authors": ["A. Researcher"],
        "publication": "arXiv",
        "date": "2026-07-10",
        "source_name": "arXiv cs.AI Recent",
        "source_url": "https://arxiv.org/list/cs.AI/recent",
        "source_trust": "PRIMARY",
        "evidence_level": "NOTABLE_LAB_PREPRINT",
        "domain": "KNOWLEDGE_SYSTEMS",
        "raw_abstract": "abstract",
        "problem_addressed": "provenance problem",
        "main_contribution": "a tracker",
        "idea_keywords": ["provenance"],
    }
    base.update(overrides)
    return base


class TestSourceValidation(unittest.TestCase):
    def test_capture_from_a_source_not_in_the_registry_is_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source_registry = base / "source-registry.json"
            relevance_gate = base / "relevance-gate.json"
            captures = base / "captures.json"
            _write_json(source_registry, _SOURCE_REGISTRY)
            _write_json(relevance_gate, _RELEVANCE_GATE)
            _write_json(captures, [_paper(
                source_name="Some Random Preprint Server",
                source_url="https://random.example.com/paper",
                source_trust="COMMUNITY",
            )])
            summary = run_once(
                str(captures), str(source_registry), str(relevance_gate), str(base / "reports"),
                run_timestamp="2026-07-20T00:00:00Z",
            )
            self.assertTrue(
                any("not in the Source Registry" in w for w in summary["validation_warnings"])
            )

    def test_capture_trust_mismatch_is_corrected_to_registry_value(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source_registry = base / "source-registry.json"
            relevance_gate = base / "relevance-gate.json"
            captures = base / "captures.json"
            _write_json(source_registry, _SOURCE_REGISTRY)
            _write_json(relevance_gate, _RELEVANCE_GATE)
            _write_json(captures, [_paper(source_trust="COMMUNITY")])  # registry says PRIMARY
            summary = run_once(
                str(captures), str(source_registry), str(relevance_gate), str(base / "reports"),
                run_timestamp="2026-07-20T00:00:00Z",
            )
            self.assertTrue(any("Registry wins" in w for w in summary["validation_warnings"]))
            registry = json.loads((base / "reports" / "research-registry.json").read_text())
            self.assertEqual(registry[0]["evidence"][0]["source_trust"], "PRIMARY")


if __name__ == "__main__":
    unittest.main()
