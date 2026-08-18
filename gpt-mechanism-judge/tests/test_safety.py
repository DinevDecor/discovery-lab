"""Static safety verification, same detector design as
case-claim-kernel/tests/test_safety.py and its own precedents
(observation-agent, constraint-change-observatory).
"""

import _pathsetup  # noqa: F401
import hashlib
import re
import unittest
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
_PKG_ROOT = Path(__file__).resolve().parents[1]
_REPO_ROOT = _PKG_ROOT.parent

_WRITE_MODE_PATTERN = re.compile(r"open\([^)]*['\"][wax][b+]?['\"]|\.write_text\(|\.write_bytes\(")

# The library (openai_client.py, judge.py, attribution.py) must have zero
# import dependency on any other package - it satisfies JudgeProtocol
# structurally. Only the acceptance script and the integration test are
# allowed to import ca_agents/case_claim_kernel, and that exception is
# checked separately below, not by this pattern.
_OTHER_PACKAGE_IMPORT = re.compile(
    r"^\s*(import\s+(ca_agents|case_claim_kernel|business_candidate_analyst)\b|"
    r"from\s+(ca_agents|case_claim_kernel|business_candidate_analyst)\b)",
    re.MULTILINE,
)

# A plausible-looking OpenAI secret literal, to catch an accidentally
# hardcoded key. Real OpenAI keys start with "sk-"; this pattern requires
# a run of 20+ key-alphabet characters after it so it can't false-positive
# on the short, human-written literal "sk-test" used in tests.
_HARDCODED_SECRET = re.compile(r"sk-[A-Za-z0-9_-]{20,}")

_FORBIDDEN_ANYWHERE = [
    r"^\s*import subprocess\b",
    r"^\s*from subprocess\b",
    r"\bsubprocess\.",
    r"\bos\.system\(",
    r"\bos\.remove\(",
    r"\bshutil\.rmtree\(",
    r"\.push\(",
    r"\.commit\(",
]

# The one and only expected same_mechanism_gate.py content hash as of
# when Stage 2 was authored (constraint-archaeology-agents/src/ca_agents/
# same_mechanism_gate.py, verified untouched via `git diff` before this
# package was written). If this ever fails, either that file changed for
# an unrelated reason (investigate before assuming this test is stale) or
# Stage 2 accidentally modified it (the one thing Stage 2 must never do).
_EXPECTED_SAME_MECHANISM_GATE_SHA256 = (
    "0dfa74a84d8258ba511f809d723357bbfa992785efeb1d08c5df3368480a1225"
)


def _all_library_source_files():
    return sorted(_SRC_ROOT.rglob("*.py"))


def _all_package_files():
    files = list(_all_library_source_files())
    for extra in ("run_stage2_acceptance.py",):
        p = _PKG_ROOT / extra
        if p.exists():
            files.append(p)
    return files


class LibraryHasZeroCrossPackageImportsTests(unittest.TestCase):
    def test_openai_client_module_imports_nothing_from_another_package(self):
        text = (_SRC_ROOT / "gpt_mechanism_judge" / "openai_client.py").read_text(encoding="utf-8")
        self.assertIsNone(_OTHER_PACKAGE_IMPORT.search(text))

    def test_judge_module_imports_nothing_from_another_package(self):
        text = (_SRC_ROOT / "gpt_mechanism_judge" / "judge.py").read_text(encoding="utf-8")
        self.assertIsNone(_OTHER_PACKAGE_IMPORT.search(text))

    def test_attribution_module_imports_nothing_from_another_package_at_module_level(self):
        """attribution.py's builder functions accept an already-built
        MechanismProfile/GateDecision object and only need `dataclasses
        .asdict`/`.to_dict()` - no ca_agents import anywhere, module-level
        or local, is needed or present."""
        text = (_SRC_ROOT / "gpt_mechanism_judge" / "attribution.py").read_text(encoding="utf-8")
        self.assertIsNone(_OTHER_PACKAGE_IMPORT.search(text))

    def test_the_other_package_import_pattern_actually_detects_a_violation(self):
        self.assertIsNotNone(_OTHER_PACKAGE_IMPORT.search("from ca_agents.same_mechanism_gate import gate_pair"))
        self.assertIsNotNone(_OTHER_PACKAGE_IMPORT.search("import case_claim_kernel.identity"))


class NoWriteModeAnywhereTests(unittest.TestCase):
    """This package has no ledger and no data directory - nothing under
    src/ should ever open a file in a writing mode. The acceptance
    script only prints to stdout."""

    def test_no_write_mode_open_in_library(self):
        for path in _all_library_source_files():
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(_WRITE_MODE_PATTERN.search(text),
                               f"{path.name} opens a file in a writing mode - this package has no ledger")

    def test_write_mode_pattern_actually_detects_a_violation(self):
        self.assertRegex("open('x.json', 'w')", _WRITE_MODE_PATTERN)


class NoHardcodedSecretTests(unittest.TestCase):
    def test_no_hardcoded_openai_key_anywhere_in_package(self):
        for path in _all_package_files():
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(_HARDCODED_SECRET.search(text),
                               f"{path.name} appears to contain a hardcoded OpenAI-shaped secret literal")

    def test_key_is_read_from_environment_not_a_default_argument(self):
        text = (_SRC_ROOT / "gpt_mechanism_judge" / "openai_client.py").read_text(encoding="utf-8")
        self.assertIn('os.environ.get("OPENAI_API_KEY")', text)

    def test_secret_pattern_actually_detects_a_violation(self):
        self.assertIsNotNone(_HARDCODED_SECRET.search("sk-" + "a" * 25))
        self.assertIsNone(_HARDCODED_SECRET.search("sk-test"))


class NoForbiddenCallsTests(unittest.TestCase):
    def test_no_forbidden_call_anywhere_in_source(self):
        for path in _all_package_files():
            text = path.read_text(encoding="utf-8")
            for pattern in _FORBIDDEN_ANYWHERE:
                self.assertIsNone(re.search(pattern, text), f"forbidden pattern {pattern!r} in {path.name}")


class SameMechanismGateUntouchedTests(unittest.TestCase):
    """The one file Stage 2 must never modify."""

    def test_same_mechanism_gate_content_hash_unchanged(self):
        path = _REPO_ROOT / "constraint-archaeology-agents" / "src" / "ca_agents" / "same_mechanism_gate.py"
        if not path.exists():
            self.skipTest("constraint-archaeology-agents not present in this checkout")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        self.assertEqual(actual, _EXPECTED_SAME_MECHANISM_GATE_SHA256,
                          "same_mechanism_gate.py content changed - Stage 2 must never modify this file")


if __name__ == "__main__":
    unittest.main()
