"""Static safety verification. Independently reimplemented pattern -
same detector design as observation-agent/tests/test_safety.py,
headquarters/tests/test_safety.py, and reality-sensor/tests/
test_safety.py, not shared code, per EXEC-009's ruling. Extended with
the same network-forbidden check reality-sensor/ established, for the
same reason: this sensor's entire purpose is external research
observation, making a live network call the single easiest safety
property to accidentally break.
"""

import _pathsetup  # noqa: F401
import re
import unittest
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[1] / "src"

_ALLOWED_WRITE_MODULES = {"cli.py", "registry.py"}

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
]

_WRITE_MODE_PATTERN = re.compile(
    r"open\([^)]*['\"][wax][b+]?['\"]|\.write_text\(|\.write_bytes\("
)


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

    def test_no_network_client_anywhere_in_source(self):
        for path in _all_source_files():
            text = path.read_text(encoding="utf-8")
            for needle in _FORBIDDEN_NETWORK:
                self.assertNotIn(
                    needle,
                    text,
                    f"{path.relative_to(_SRC_ROOT)} references {needle!r} — "
                    "this package must never make a live network call; "
                    "capture happens outside it (see ARCHITECTURE.md)",
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
        text = (_SRC_ROOT / "research_sensor" / "registry.py").read_text(encoding="utf-8")
        self.assertRegex(text, _WRITE_MODE_PATTERN)

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

    def test_source_never_references_git_command(self):
        for path in _all_source_files():
            text = path.read_text(encoding="utf-8").lower()
            self.assertNotIn("'git'", text)
            self.assertNotIn('"git"', text)


if __name__ == "__main__":
    unittest.main()
