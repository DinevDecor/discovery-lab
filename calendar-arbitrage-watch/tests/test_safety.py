"""Static safety verification, same detector design as
constraint_change_observatory/tests/test_safety.py and its own
precedents (observation-agent, reality-sensor, headquarters,
business-candidate-analyst). This package's whole job is to hold
hand/AI-executor-researched calendar evidence without ever touching the
network, a model, or another analyst package's code - this test makes
that boundary a build failure, not just a docstring (2026-08-15 approval,
point 3: "Calendar Arbitrage package не прави собствен network fetch в
тази фаза").
"""

import _pathsetup  # noqa: F401
import re
import unittest
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[1] / "src"

_ALLOWED_WRITE_MODULES = {"ledger.py", "report.py"}

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
    "requests.", "urllib.request", "urllib.error", "httpx.", "http.client", "socket.",
    "ftplib.", "smtplib.", "aiohttp", "WebFetch", "WebSearch", "anthropic", "call_claude",
    "ANTHROPIC_API_KEY",
]

_FORBIDDEN_THIRD_PARTY = ["import yaml", "from yaml"]

_WRITE_MODE_PATTERN = re.compile(r"open\([^)]*['\"][wax][b+]?['\"]|\.write_text\(|\.write_bytes\(")

# Independence boundary: this package must never import another analyst
# package's code, and (checked separately, over the WHOLE repo, not just
# this package's src/) no other analyst package may import this one -
# both directions of the zero-import-dependency norm every sibling
# package already holds itself to.
_OTHER_ANALYST_IMPORT = re.compile(
    r"^\s*(import\s+(ca_agents|business_candidate_analyst|constraint_change_observatory|"
    r"capability_observatory|reality_sensor|observation_agent|headquarters)\b|"
    r"from\s+(ca_agents|business_candidate_analyst|constraint_change_observatory|"
    r"capability_observatory|reality_sensor|observation_agent|headquarters)\b)",
    re.MULTILINE,
)


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
                                  "never call a model or the network in this phase (2026-08-15 approval, point 3).")

    def test_write_mode_file_opens_only_in_allowed_modules(self):
        for path in _all_source_files():
            text = path.read_text(encoding="utf-8")
            if _WRITE_MODE_PATTERN.search(text) and path.name not in _ALLOWED_WRITE_MODULES:
                self.fail(f"{path.relative_to(_SRC_ROOT)} opens a file in a writing mode but is not in "
                          f"the allowed-write list {_ALLOWED_WRITE_MODULES}")

    def test_at_least_the_expected_write_calls_exist(self):
        ledger_text = (_SRC_ROOT / "calendar_arbitrage_watch" / "ledger.py").read_text(encoding="utf-8")
        report_text = (_SRC_ROOT / "calendar_arbitrage_watch" / "report.py").read_text(encoding="utf-8")
        self.assertRegex(ledger_text, _WRITE_MODE_PATTERN)
        self.assertRegex(report_text, _WRITE_MODE_PATTERN)

    def test_no_third_party_parser_dependency(self):
        for path in _all_source_files():
            text = path.read_text(encoding="utf-8")
            for needle in _FORBIDDEN_THIRD_PARTY:
                self.assertNotIn(needle, text,
                                  f"{path.relative_to(_SRC_ROOT)} references {needle!r} - intake is JSON-only.")

    def test_no_module_imports_another_analyst_package(self):
        for path in _all_source_files():
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(_OTHER_ANALYST_IMPORT.search(text),
                               f"{path.relative_to(_SRC_ROOT)} imports another package's analyst code")

    def test_no_other_analyst_package_imports_this_one(self):
        """The other direction of the independence boundary: no existing
        package anywhere in the repo may import calendar_arbitrage_watch
        - the approved architecture review's write points are additive
        only (zero modification to any existing package)."""
        repo_root = _SRC_ROOT.parents[1]
        pattern = re.compile(r"^\s*(import\s+calendar_arbitrage_watch\b|from\s+calendar_arbitrage_watch\b)",
                              re.MULTILINE)
        for path in repo_root.rglob("*.py"):
            if "calendar-arbitrage-watch" in path.parts or ".git" in path.parts:
                continue  # skip this package's own tree and vcs internals
            text = path.read_text(encoding="utf-8", errors="ignore")
            self.assertIsNone(pattern.search(text),
                               f"{path} imports calendar_arbitrage_watch - no existing package should depend on it")

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
        self.assertIn("urllib.request", "import urllib.request\nurllib.request.urlopen(url)")

    def test_write_mode_pattern_actually_detects_a_violation(self):
        self.assertRegex("open('x.json', 'w')", _WRITE_MODE_PATTERN)
        self.assertIsNone(_WRITE_MODE_PATTERN.search("open('x.json', encoding='utf-8')"))

    def test_other_analyst_import_pattern_actually_detects_a_violation(self):
        self.assertIsNotNone(_OTHER_ANALYST_IMPORT.search("from ca_agents.memory import classify_function"))
        self.assertIsNotNone(_OTHER_ANALYST_IMPORT.search("import business_candidate_analyst.analyst"))


if __name__ == "__main__":
    unittest.main()
