"""Static safety verification — the literal implementation of this
implementation's own Mission: "If any code path could modify state,
disable or remove it." This test does not trust the docstrings or
comments elsewhere in the package; it scans the actual source text for
the specific patterns that would constitute a write, delete, commit,
push, merge, or subprocess call, and fails if any exist outside the
two files explicitly allowed to write this agent's own output."""

import _pathsetup  # noqa: F401
import re
import unittest
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[1] / "src"

# The only two modules allowed to open a file in a writing mode — and
# only for this agent's own report/log/snapshot output, never for any
# file belonging to an observed repository.
_ALLOWED_WRITE_MODULES = {"report.py", "cli.py"}

_FORBIDDEN_ANYWHERE = [
    # Real invocation syntax only (import or attribute-call form) — a
    # prose mention of the word (e.g. in a docstring explaining this
    # very safety property) must not trip this check.
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
        # A negative-only test suite (nothing forbidden found) could pass
        # vacuously if the patterns above are simply wrong. Confirm the
        # detector actually works by checking it DOES find the report
        # module's own legitimate report-writing call.
        report_text = (_SRC_ROOT / "observation_agent" / "cli.py").read_text(encoding="utf-8")
        self.assertRegex(report_text, _WRITE_MODE_PATTERN)

    def test_forbidden_patterns_actually_detect_violations(self):
        # Self-check on the detector itself: prove each pattern would
        # catch a real violation, so a passing suite above means "none
        # found," not "the patterns are too narrow to find anything."
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


if __name__ == "__main__":
    unittest.main()
