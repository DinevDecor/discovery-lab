"""Static safety verification, same detector design as
constraint-change-observatory/tests/test_safety.py and its own
precedents (observation-agent, reality-sensor, headquarters,
x-signal-probe). This package's whole job is deterministic identity
wrapping of two already-published files - this test makes the
read-only-against-CA/BCA and append-only-against-its-own-ledger
boundary a build failure, not just a docstring.
"""

import _pathsetup  # noqa: F401
import re
import unittest
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[1] / "src"

_ALLOWED_WRITE_MODULES = {"ledger.py"}

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
    "ANTHROPIC_API_KEY", "OPENAI_API_KEY",
]

_WRITE_MODE_PATTERN = re.compile(r"open\([^)]*['\"][wax][b+]?['\"]|\.write_text\(|\.write_bytes\(")

# The one rule this whole package exists to prove: never import another
# package's code, only ever read its data files.
_OTHER_PACKAGE_IMPORT = re.compile(
    r"^\s*(import\s+(ca_agents|business_candidate_analyst)\b|"
    r"from\s+(ca_agents|business_candidate_analyst)\b)",
    re.MULTILINE,
)


def _all_source_files():
    files = sorted(_SRC_ROOT.rglob("*.py"))
    run_cli = Path(__file__).resolve().parents[1] / "run_case_claim_kernel.py"
    if run_cli.exists():
        files.append(run_cli)
    return files


class SafetyTests(unittest.TestCase):
    def test_source_files_exist_to_scan(self):
        self.assertGreater(len(_all_source_files()), 0)

    def test_no_forbidden_call_anywhere_in_source(self):
        for path in _all_source_files():
            text = path.read_text(encoding="utf-8")
            for pattern in _FORBIDDEN_ANYWHERE:
                self.assertIsNone(re.search(pattern, text),
                                   f"Forbidden pattern {pattern!r} found in {path.name}")

    def test_no_network_or_model_client_anywhere_in_source(self):
        for path in _all_source_files():
            text = path.read_text(encoding="utf-8")
            for needle in _FORBIDDEN_NETWORK:
                self.assertNotIn(needle, text,
                                  f"{path.name} references {needle!r} - this package must never call a "
                                  "model or the network; it is a pure function of two already-published "
                                  "JSON files.")

    def test_write_mode_file_opens_only_in_ledger(self):
        for path in _all_source_files():
            if path.name == "run_case_claim_kernel.py":
                continue
            text = path.read_text(encoding="utf-8")
            if _WRITE_MODE_PATTERN.search(text) and path.name not in _ALLOWED_WRITE_MODULES:
                self.fail(f"{path.name} opens a file in a writing mode but is not in the allowed-write "
                          f"list {_ALLOWED_WRITE_MODULES}")

    def test_ledger_module_actually_writes(self):
        ledger_text = (_SRC_ROOT / "case_claim_kernel" / "ledger.py").read_text(encoding="utf-8")
        self.assertRegex(ledger_text, _WRITE_MODE_PATTERN)

    def test_no_module_imports_ca_or_bca_code(self):
        """Independence boundary: this package reads CA's and BCA's
        published *data* files (wrap.py's json.load calls) and never
        imports either package's *code* - per CONTRACT.md's "Zero
        import dependency" rule, matching constraint_change_observatory's
        own precedent for the same rule."""
        for path in _all_source_files():
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(_OTHER_PACKAGE_IMPORT.search(text),
                               f"{path.name} imports another package's analyst code")

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
        self.assertRegex("open('x.jsonl', 'a')", _WRITE_MODE_PATTERN)
        self.assertIsNone(_WRITE_MODE_PATTERN.search("open('x.json', encoding='utf-8')"))

    def test_other_package_import_pattern_actually_detects_a_violation(self):
        self.assertIsNotNone(_OTHER_PACKAGE_IMPORT.search("from ca_agents.memory import classify_function"))
        self.assertIsNotNone(_OTHER_PACKAGE_IMPORT.search("import business_candidate_analyst.analyst"))


if __name__ == "__main__":
    unittest.main()
