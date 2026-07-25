"""Headquarters compatibility (EXEC-008 required test category):
proves signal-registry.json is structurally readable the same
tolerant way headquarters/src/headquarters/collector.py already reads
every other artifact it consumes - a specific, pre-configured file
path, parsed as plain JSON, never a directory walk. This test does not
import or modify any headquarters/ module (ARCHITECTURE.md: "not
attempted here" - this only proves the artifact is ready to be read,
if a later, separate task wires that up)."""

import _pathsetup  # noqa: F401
import json
import tempfile
import unittest
from pathlib import Path

from reality_sensor.config import RelevanceGateConfig, RelevanceRule
from reality_sensor.models import Category, Project, RawCapture, TrustLevel
from reality_sensor.registry import build_signal, save_registry, upsert

_REQUIRED_SIGNAL_FIELDS = {
    "signal_id",
    "timestamp",
    "source",
    "source_trust",
    "category",
    "affected_capability",
    "affected_projects",
    "evidence",
    "summary",
    "practical_impact",
    "confidence",
    "urgency",
    "recommended_action",
}


class TestHeadquartersCompatibility(unittest.TestCase):
    def test_registry_is_a_flat_json_list_of_objects(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "signal-registry.json"
            relevance = RelevanceGateConfig(rules=[RelevanceRule(project=Project.DISCOVERY_LAB, keywords=["mcp"])])
            capture = RawCapture(
                source_name="MCP Docs",
                source_url="https://modelcontextprotocol.io/",
                source_trust=TrustLevel.PRIMARY,
                category=Category.AGENT_INFRASTRUCTURE,
                captured_at="2026-07-20T00:00:00Z",
                title="MCP 2.0",
                raw_text="MCP 2.0 is out.",
                affected_capability="MCP 2.0",
                capability_keywords=["mcp"],
            )
            records = upsert(build_signal([capture], relevance), [], "2026-07-20T00:00:00Z")
            save_registry(path, records)

            # A Headquarters-style tolerant reader: plain json.loads, no
            # custom parser, no schema library.
            raw = json.loads(path.read_text(encoding="utf-8"))
            self.assertIsInstance(raw, list)
            for entry in raw:
                self.assertIsInstance(entry, dict)
                self.assertTrue(_REQUIRED_SIGNAL_FIELDS.issubset(entry.keys()))
                self.assertIsInstance(entry["affected_projects"], list)
                self.assertIsInstance(entry["evidence"], list)
                for e in entry["evidence"]:
                    self.assertIn("source_name", e)
                    self.assertIn("source_url", e)
                    self.assertIn("quoted_text", e)

    def test_empty_registry_is_still_valid_json_a_reader_would_not_crash_on(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "signal-registry.json"
            save_registry(path, [])
            raw = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(raw, [])


if __name__ == "__main__":
    unittest.main()
