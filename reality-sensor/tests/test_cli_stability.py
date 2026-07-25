"""EXEC-008 regression tests — repeated identical runs, empty-result
handling, and read-only verification, exercised through the same
cli.run_once() entry point a human/executor actually invokes, not just
at the unit level. Mirrors observation-agent's own
tests/test_cli_stability.py in spirit (EXEC-006's own precedent for
this exact category of test)."""

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
_CAPTURES = [
    {
        "source_name": "MCP Docs",
        "source_url": "https://modelcontextprotocol.io/",
        "source_trust": "PRIMARY",
        "category": "AGENT_INFRASTRUCTURE",
        "captured_at": "2026-07-20T00:00:00Z",
        "title": "MCP 2.0 released",
        "raw_text": "MCP 2.0 adds streaming tool results.",
        "affected_capability": "MCP 2.0 streaming tool results",
        "capability_keywords": ["mcp", "streaming"],
    }
]


def _write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data), encoding="utf-8")


def _setup(base: Path, captures=None) -> tuple[Path, Path, Path]:
    source_registry = base / "source-registry.json"
    relevance_gate = base / "relevance-gate.json"
    captures_path = base / "captures.json"
    _write_json(source_registry, _SOURCE_REGISTRY)
    _write_json(relevance_gate, _RELEVANCE_GATE)
    _write_json(captures_path, _CAPTURES if captures is None else captures)
    return source_registry, relevance_gate, captures_path


class TestPureDeterminism(unittest.TestCase):
    def test_same_input_fresh_reports_dir_each_time_gives_identical_registry(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source_registry, relevance_gate, captures_path = _setup(base)

            registries = []
            for i in range(3):
                reports_dir = base / f"reports-{i}"
                run_once(
                    str(captures_path), str(source_registry), str(relevance_gate),
                    str(reports_dir), run_timestamp="2026-07-20T00:00:00Z",
                )
                registries.append((reports_dir / "signal-registry.json").read_text())

            self.assertEqual(registries[0], registries[1])
            self.assertEqual(registries[1], registries[2])


class TestRegressionAgainstSelfGeneratedReports(unittest.TestCase):
    def test_repeated_runs_into_the_same_reports_dir_stay_flat(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source_registry, relevance_gate, captures_path = _setup(base)
            reports_dir = base / "reports"

            summaries = []
            for ts in ("2026-07-20T00:00:00Z", "2026-07-21T00:00:00Z", "2026-07-22T00:00:00Z"):
                summaries.append(
                    run_once(
                        str(captures_path), str(source_registry), str(relevance_gate),
                        str(reports_dir), run_timestamp=ts,
                    )
                )

            self.assertEqual(summaries[0]["new_signals"], 1)
            self.assertEqual(summaries[0]["registry_total"], 1)
            self.assertEqual(summaries[1]["new_signals"], 0)
            self.assertEqual(summaries[1]["updated_signals"], 1)
            self.assertEqual(summaries[1]["registry_total"], 1)
            self.assertEqual(summaries[2]["new_signals"], 0)
            self.assertEqual(summaries[2]["registry_total"], 1)

            final = json.loads((reports_dir / "signal-registry.json").read_text())
            self.assertEqual(len(final), 1)
            self.assertEqual(final[0]["times_seen"], 3)
            self.assertEqual(final[0]["signal_id"], "RS-0001")


class TestEmptyResultHandling(unittest.TestCase):
    def test_empty_captures_file_produces_a_valid_empty_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source_registry, relevance_gate, captures_path = _setup(base, captures=[])
            reports_dir = base / "reports"
            summary = run_once(
                str(captures_path), str(source_registry), str(relevance_gate),
                str(reports_dir), run_timestamp="2026-07-20T00:00:00Z",
            )
            self.assertEqual(summary["new_signals"], 0)
            self.assertEqual(summary["registry_total"], 0)
            registry = json.loads((reports_dir / "signal-registry.json").read_text())
            self.assertEqual(registry, [])
            daily = (reports_dir / summary["daily_brief_path"].split("/")[-1]).read_text()
            self.assertIn("No signals this run", daily)


class TestReadOnlyVerification(unittest.TestCase):
    def test_captures_and_config_files_are_never_modified(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source_registry, relevance_gate, captures_path = _setup(base)
            before = {
                p: p.read_text() for p in (source_registry, relevance_gate, captures_path)
            }
            run_once(
                str(captures_path), str(source_registry), str(relevance_gate),
                str(base / "reports"), run_timestamp="2026-07-20T00:00:00Z",
            )
            for p, text_before in before.items():
                self.assertEqual(p.read_text(), text_before, f"{p} was modified by a read-only run")

    def test_writes_are_confined_to_the_reports_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source_registry, relevance_gate, captures_path = _setup(base)
            reports_dir = base / "reports"
            before = set(base.rglob("*"))
            run_once(
                str(captures_path), str(source_registry), str(relevance_gate),
                str(reports_dir), run_timestamp="2026-07-20T00:00:00Z",
            )
            after = set(base.rglob("*"))
            new_paths = after - before
            for p in new_paths:
                self.assertTrue(
                    str(p).startswith(str(reports_dir)),
                    f"unexpected write outside reports_dir: {p}",
                )


if __name__ == "__main__":
    unittest.main()
