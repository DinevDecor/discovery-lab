"""Static safety verification — the literal implementation of
CONTRACT.md's Human Authority Boundary. Same detector design as
observation-agent/tests/test_safety.py (the shared-scanner opportunity
this run's own Opportunity Detector flags): scans the actual source
text for write/delete/commit/push/merge/subprocess patterns and fails
if any exist outside the one module allowed to write this tool's own
report output."""

import _pathsetup  # noqa: F401
import re
import unittest
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[1] / "src"

_ALLOWED_WRITE_MODULES = {"cli.py", "recommendation.py", "history.py"}

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

_WRITE_MODE_PATTERN = re.compile(r"open\([^)]*['\"][wax][b+]?['\"]")


def _all_source_files() -> list[Path]:
    return sorted(_SRC_ROOT.rglob("*.py"))


class TestSafety(unittest.TestCase):
    def test_no_forbidden_call_anywhere_in_source(self):
        for path in _all_source_files():
            text = path.read_text(encoding="utf-8")
            for pattern in _FORBIDDEN_ANYWHERE:
                match = re.search(pattern, text)
                self.assertIsNone(
                    match,
                    f"Forbidden pattern {pattern!r} found in {path.relative_to(_SRC_ROOT)}",
                )

    def test_write_mode_file_opens_only_in_allowed_modules(self):
        for path in _all_source_files():
            text = path.read_text(encoding="utf-8")
            if _WRITE_MODE_PATTERN.search(text) and path.name not in _ALLOWED_WRITE_MODULES:
                self.fail(
                    f"{path.relative_to(_SRC_ROOT)} opens a file in a "
                    "writing mode, but is not in the allowed-write list "
                    f"{_ALLOWED_WRITE_MODULES}"
                )

    def test_at_least_the_expected_write_call_exists(self):
        cli_text = (_SRC_ROOT / "headquarters" / "cli.py").read_text(encoding="utf-8")
        self.assertRegex(cli_text, _WRITE_MODE_PATTERN)

    def test_forbidden_patterns_actually_detect_violations(self):
        samples = {
            r"\bsubprocess\.": "import subprocess\nsubprocess.run(['git', 'push'])",
            r"\.push\(": "repo.push()",
            r"\.commit\(": "repo.index.commit('msg')",
            r"\bos\.remove\(": "os.remove(path)",
        }
        for pattern, sample in samples.items():
            self.assertRegex(sample, pattern, f"pattern {pattern!r} failed to match its own positive sample")

    def test_source_never_references_git_command(self):
        for path in _all_source_files():
            text = path.read_text(encoding="utf-8").lower()
            self.assertNotIn("'git'", text)
            self.assertNotIn('"git"', text)

    def test_source_never_calls_github_or_network_apis(self):
        # Headquarters reads local filesystem artifacts only. It must
        # never reach out to GitHub's API or any network endpoint —
        # that would blur the read-only, advisory-only boundary.
        forbidden_substrings = ["requests.", "urllib.request", "httpx.", "http.client"]
        for path in _all_source_files():
            text = path.read_text(encoding="utf-8")
            for needle in forbidden_substrings:
                self.assertNotIn(needle, text, f"{path.name} references {needle!r}")


if __name__ == "__main__":
    unittest.main()
