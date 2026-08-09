"""Static safety verification. Same detector design as
reality-sensor/tests/test_safety.py: this package's whole reason for
existing is to process externally-fetched evidence, so it would be easy to
accidentally add a live network call into the checked-in, tested pipeline --
which would break the "process the same input twice, get the same output"
guarantee capture_intake.py and storage.py depend on. This test makes that
boundary a build failure, not just a docstring.

No test in this suite requires live internet access.
"""

import _pathsetup  # noqa: F401
import re
import unittest
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[1] / "src"

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

_FORBIDDEN_DESTRUCTIVE = [
    r"^\s*import subprocess\b",
    r"^\s*from subprocess\b",
    r"\bsubprocess\.",
    r"\bos\.system\(",
    r"\bos\.remove\(",
    r"\bos\.unlink\(",
    r"\bshutil\.rmtree\(",
    r"\.push\(",
    r"\.commit\(",
    r"\.merge\(",
]


def _iter_source_files():
    return sorted(_SRC_ROOT.rglob("*.py"))


class SafetyTests(unittest.TestCase):
    def test_source_files_exist_to_scan(self):
        files = _iter_source_files()
        self.assertGreater(len(files), 0, "expected capability_observatory source files to scan")

    def test_no_network_client_anywhere_in_checked_in_source(self):
        offenders = []
        for path in _iter_source_files():
            text = path.read_text(encoding="utf-8")
            for needle in _FORBIDDEN_NETWORK:
                if needle in text:
                    offenders.append(f"{path.relative_to(_SRC_ROOT)}: contains {needle!r}")
        self.assertEqual(offenders, [], "network client reference(s) found:\n" + "\n".join(offenders))

    def test_no_destructive_or_git_action_calls_in_checked_in_source(self):
        offenders = []
        for path in _iter_source_files():
            text = path.read_text(encoding="utf-8")
            for pattern in _FORBIDDEN_DESTRUCTIVE:
                if re.search(pattern, text, re.MULTILINE):
                    offenders.append(f"{path.relative_to(_SRC_ROOT)}: matches {pattern!r}")
        self.assertEqual(offenders, [], "destructive/git-action call(s) found:\n" + "\n".join(offenders))

    def test_detector_actually_catches_a_real_violation(self):
        """Self-check, mirroring reality-sensor's own precedent: prove the
        scan logic isn't vacuously passing."""
        sample = "import urllib.request\nurllib.request.urlopen('https://example.test')\n"
        self.assertTrue(any(needle in sample for needle in _FORBIDDEN_NETWORK))


if __name__ == "__main__":
    unittest.main()
