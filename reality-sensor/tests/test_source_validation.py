import _pathsetup  # noqa: F401
import json
import tempfile
import unittest
from pathlib import Path

from reality_sensor.cli import run_once

_SOURCE_REGISTRY = {
    "search_budget": 10,
    "sources": [
        {
            "name": "MCP Docs",
            "url": "https://modelcontextprotocol.io/",
            "trust_level": "PRIMARY",
            "category": "AGENT_INFRASTRUCTURE",
            "domain": "B",
        }
    ],
}
_RELEVANCE_GATE = {"rules": [{"project": "Discovery Lab", "keywords": ["mcp"]}]}


def _write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data), encoding="utf-8")


class TestSourceValidation(unittest.TestCase):
    def test_capture_from_a_source_not_in_the_registry_is_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source_registry = base / "source-registry.json"
            relevance_gate = base / "relevance-gate.json"
            captures = base / "captures.json"
            _write_json(source_registry, _SOURCE_REGISTRY)
            _write_json(relevance_gate, _RELEVANCE_GATE)
            _write_json(
                captures,
                [
                    {
                        "source_name": "Some Random Blog",
                        "source_url": "https://random-blog.example.com/post",
                        "source_trust": "COMMUNITY",
                        "category": "AGENT_INFRASTRUCTURE",
                        "captured_at": "2026-07-20T00:00:00Z",
                        "title": "MCP rumor",
                        "raw_text": "Someone said MCP will change.",
                        "affected_capability": "unconfirmed MCP change",
                        "capability_keywords": ["mcp"],
                    }
                ],
            )
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
            _write_json(
                captures,
                [
                    {
                        "source_name": "MCP Docs",
                        "source_url": "https://modelcontextprotocol.io/",
                        "source_trust": "COMMUNITY",  # wrong - registry says PRIMARY
                        "category": "AGENT_INFRASTRUCTURE",
                        "captured_at": "2026-07-20T00:00:00Z",
                        "title": "MCP 2.0",
                        "raw_text": "MCP 2.0 is out.",
                        "affected_capability": "MCP 2.0",
                        "capability_keywords": ["mcp"],
                    }
                ],
            )
            summary = run_once(
                str(captures), str(source_registry), str(relevance_gate), str(base / "reports"),
                run_timestamp="2026-07-20T00:00:00Z",
            )
            self.assertTrue(any("Registry wins" in w for w in summary["validation_warnings"]))
            registry = json.loads((base / "reports" / "signal-registry.json").read_text())
            self.assertEqual(registry[0]["evidence"][0]["source_trust"], "PRIMARY")


if __name__ == "__main__":
    unittest.main()
