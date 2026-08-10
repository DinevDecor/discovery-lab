"""Static safety verification, same detector design as
observation-agent/tests/test_safety.py, headquarters/tests/test_safety.py,
reality-sensor/tests/test_safety.py and capability-observatory/tests/
test_safety.py. This package's whole reason for existing is to read
Constraint Archaeology's published evidence without ever touching it, so
this test makes the architectural boundary in CONTRACT.md a build
failure, not just a docstring:

  - no network client of any kind anywhere in the source (no web search,
    no LLM call - state transitions must be evidence-driven, never "the
    model liked this pattern");
  - no destructive/git-action call anywhere;
  - a file may only be opened in a writing mode from registry.py or
    report.py - both write only under business-candidate-analyst/ own
    data/ and reports/, never into constraint-archaeology-agents/;
  - evidence_reader.py (the module that reads Constraint Archaeology's
    files) never imports the ca_agents package, so there is no code path
    back into the upstream sensor/gate/thresholds.
"""

import _pathsetup  # noqa: F401
import re
import unittest
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[1] / "src"

_ALLOWED_WRITE_MODULES = {"registry.py", "report.py"}

_FORBIDDEN_ANYWHERE = [
    r"^\s*import subprocess\b",
    r"^\s*from subprocess\b",
    r"\bsubprocess\.",
    r"\bos\.system\(",
    r"\bos\.remove\(",
    r"\bos\.unlink\(",
    r"\bos\.rmdir\(",
    r"\bshutil\.rmtree\(",
    r"\bshutil\.move\(",
    r"\.push\(",
    r"\.commit\(",
    r"\.merge\(",
    r"\bos\.rename\(",
    r"\.unlink\(\)",
]

_FORBIDDEN_NETWORK = [
    "requests.",
    "urllib.request",
    "urllib.error",
    "httpx.",
    "http.client",
    "socket.",
    "ftplib.",
    "smtplib.",
    "aiohttp",
    "WebFetch",
    "WebSearch",
    "anthropic",
    "call_claude",
    "ANTHROPIC_API_KEY",
]

_WRITE_MODE_PATTERN = re.compile(r"open\([^)]*['\"][wax][b+]?['\"]|\.write_text\(|\.write_bytes\(")


def _all_source_files():
    return sorted(_SRC_ROOT.rglob("*.py"))


class SafetyTests(unittest.TestCase):
    def test_source_files_exist_to_scan(self):
        self.assertGreater(len(_all_source_files()), 0)

    def test_no_forbidden_call_anywhere_in_source(self):
        for path in _all_source_files():
            text = path.read_text(encoding="utf-8")
            for pattern in _FORBIDDEN_ANYWHERE:
                self.assertIsNone(re.search(pattern, text),
                                   f"Forbidden pattern {pattern!r} found in {path.relative_to(_SRC_ROOT)}")

    def test_no_network_or_model_client_anywhere_in_source(self):
        for path in _all_source_files():
            text = path.read_text(encoding="utf-8")
            for needle in _FORBIDDEN_NETWORK:
                self.assertNotIn(needle, text,
                                  f"{path.relative_to(_SRC_ROOT)} references {needle!r} - this package must "
                                  "never call a model or the network; classification is fully deterministic.")

    def test_write_mode_file_opens_only_in_allowed_modules(self):
        for path in _all_source_files():
            text = path.read_text(encoding="utf-8")
            if _WRITE_MODE_PATTERN.search(text) and path.name not in _ALLOWED_WRITE_MODULES:
                self.fail(f"{path.relative_to(_SRC_ROOT)} opens a file in a writing mode but is not in "
                          f"the allowed-write list {_ALLOWED_WRITE_MODULES}")

    def test_at_least_the_expected_write_calls_exist(self):
        registry_text = (_SRC_ROOT / "business_candidate_analyst" / "registry.py").read_text(encoding="utf-8")
        report_text = (_SRC_ROOT / "business_candidate_analyst" / "report.py").read_text(encoding="utf-8")
        self.assertRegex(registry_text, _WRITE_MODE_PATTERN)
        self.assertRegex(report_text, _WRITE_MODE_PATTERN)

    def test_no_module_anywhere_imports_ca_agents(self):
        # Prose mentions of "ca_agents" in a docstring (explaining why this
        # package deliberately mirrors a pattern from it) are fine and
        # expected; an actual import statement is the coupling this test
        # exists to catch.
        import_pattern = re.compile(r"^\s*(import\s+ca_agents\b|from\s+ca_agents\b)", re.MULTILINE)
        for path in _all_source_files():
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(import_pattern.search(text),
                               f"{path.relative_to(_SRC_ROOT)} imports ca_agents - this package must have zero "
                               "import dependency on the upstream Constraint Archaeology code")

    def test_ca_agents_import_pattern_actually_detects_a_violation(self):
        import_pattern = re.compile(r"^\s*(import\s+ca_agents\b|from\s+ca_agents\b)", re.MULTILINE)
        self.assertIsNotNone(import_pattern.search("from ca_agents.memory import classify_function"))
        self.assertIsNotNone(import_pattern.search("import ca_agents.models"))

    def test_forbidden_patterns_actually_detect_violations(self):
        samples = {
            r"\bsubprocess\.": "import subprocess\nsubprocess.run(['git', 'push'])",
            r"\.push\(": "repo.push()",
            r"\.commit\(": "repo.index.commit('msg')",
            r"\bos\.remove\(": "os.remove(path)",
        }
        for pattern, sample in samples.items():
            self.assertRegex(sample, pattern, f"pattern {pattern!r} failed to match its own positive sample")

    def test_network_forbidden_list_actually_detects_a_violation(self):
        sample = "import urllib.request\nurllib.request.urlopen(url)"
        self.assertIn("urllib.request", sample)

    def test_write_mode_pattern_actually_detects_a_violation(self):
        self.assertRegex("open('x.json', 'w')", _WRITE_MODE_PATTERN)
        self.assertRegex("open('x.jsonl', 'a', encoding='utf-8')", _WRITE_MODE_PATTERN)
        self.assertIsNone(_WRITE_MODE_PATTERN.search("open('x.json', encoding='utf-8')"))


if __name__ == "__main__":
    unittest.main()
