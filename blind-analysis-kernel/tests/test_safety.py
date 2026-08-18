"""Static safety verification, same detector design as
gpt-mechanism-judge/tests/test_safety.py and case-claim-kernel/tests
/test_safety.py.
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
# manifest.py (Stage 3B) owns RunManifestLedger, the run-manifest analog
# of ledger.py's AnalysisLedger - same append-only discipline, same
# reason it's allowed to open a file in a writing mode.
_ALLOWED_WRITE_MODULES = {"ledger.py", "manifest.py"}

# Only dispatch.py may import another package's code - it IS the
# blind-dispatch boundary (see its own docstring). Every other module in
# this package (models/identity/packet/validator/ledger/manifest) must be
# a standalone library, same discipline case-claim-kernel and
# gpt-mechanism-judge already hold their own libraries to.
_OTHER_PACKAGE_IMPORT = re.compile(
    r"^\s*(import\s+(ca_agents|case_claim_kernel|gpt_mechanism_judge|business_candidate_analyst)\b|"
    r"from\s+(ca_agents|case_claim_kernel|gpt_mechanism_judge|business_candidate_analyst)\b)",
    re.MULTILINE,
)

_NON_DISPATCH_LIBRARY_MODULES = ("models.py", "identity.py", "packet.py", "validator.py", "ledger.py", "manifest.py")

_HARDCODED_SECRET = re.compile(r"(sk-[A-Za-z0-9_-]{20,}|sk-ant-[A-Za-z0-9_-]{20,})")

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

# The files Stage 3 must never modify (task §2: "Do not modify
# JudgeProtocol. Do not modify same_mechanism_gate.py." - and by the same
# logic, the real ClaudeMechanismJudge Stage 3 reuses).
_PINNED_FILES = {
    "constraint-archaeology-agents/src/ca_agents/same_mechanism_gate.py":
        "0dfa74a84d8258ba511f809d723357bbfa992785efeb1d08c5df3368480a1225",
    "constraint-archaeology-agents/src/ca_agents/mechanism_judge.py":
        "c871842b3c0fc5132f0e66a5f5b1af90e0571e5d671826fe899e5a829d4ff418",
}


def _all_library_source_files():
    return sorted(_SRC_ROOT.rglob("*.py"))


def _all_package_files():
    files = list(_all_library_source_files())
    run_cli = _PKG_ROOT / "run_stage3_job.py"
    if run_cli.exists():
        files.append(run_cli)
    return files


class DispatchIsTheOnlyCrossPackageImportTests(unittest.TestCase):
    def test_non_dispatch_library_modules_import_nothing_from_another_package(self):
        for name in _NON_DISPATCH_LIBRARY_MODULES:
            path = _SRC_ROOT / "blind_analysis_kernel" / name
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(_OTHER_PACKAGE_IMPORT.search(text),
                               f"{name} imports another package's code - only dispatch.py may")

    def test_dispatch_module_is_the_one_that_imports_the_other_packages(self):
        text = (_SRC_ROOT / "blind_analysis_kernel" / "dispatch.py").read_text(encoding="utf-8")
        self.assertIsNotNone(_OTHER_PACKAGE_IMPORT.search(text))

    def test_pattern_actually_detects_a_violation(self):
        self.assertIsNotNone(_OTHER_PACKAGE_IMPORT.search("from ca_agents.same_mechanism_gate import gate_pair"))
        self.assertIsNotNone(_OTHER_PACKAGE_IMPORT.search("import gpt_mechanism_judge.judge"))


class NoWriteModeOutsideLedgerTests(unittest.TestCase):
    def test_no_write_mode_open_outside_ledger(self):
        for path in _all_library_source_files():
            if path.name in _ALLOWED_WRITE_MODULES:
                continue
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(_WRITE_MODE_PATTERN.search(text),
                               f"{path.name} opens a file in a writing mode outside ledger.py")

    def test_ledger_module_actually_writes(self):
        text = (_SRC_ROOT / "blind_analysis_kernel" / "ledger.py").read_text(encoding="utf-8")
        self.assertRegex(text, _WRITE_MODE_PATTERN)

    def test_write_mode_pattern_actually_detects_a_violation(self):
        self.assertRegex("open('x.jsonl', 'a')", _WRITE_MODE_PATTERN)


class NoHardcodedSecretTests(unittest.TestCase):
    def test_no_hardcoded_key_anywhere_in_package(self):
        for path in _all_package_files():
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(_HARDCODED_SECRET.search(text),
                               f"{path.name} appears to contain a hardcoded provider secret literal")

    def test_secret_pattern_actually_detects_a_violation(self):
        self.assertIsNotNone(_HARDCODED_SECRET.search("sk-" + "a" * 25))
        self.assertIsNotNone(_HARDCODED_SECRET.search("sk-ant-" + "a" * 25))


class NoForbiddenCallsTests(unittest.TestCase):
    def test_no_forbidden_call_anywhere_in_source(self):
        for path in _all_package_files():
            text = path.read_text(encoding="utf-8")
            for pattern in _FORBIDDEN_ANYWHERE:
                self.assertIsNone(re.search(pattern, text), f"forbidden pattern {pattern!r} in {path.name}")


class PinnedFilesUntouchedTests(unittest.TestCase):
    """The files Stage 3 must never modify - content-hash pinned, same
    technique gpt-mechanism-judge/tests/test_safety.py already uses for
    same_mechanism_gate.py."""

    def test_pinned_files_content_hash_unchanged(self):
        for rel_path, expected in _PINNED_FILES.items():
            path = _REPO_ROOT / rel_path
            if not path.exists():
                self.skipTest(f"{rel_path} not present in this checkout")
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(actual, expected, f"{rel_path} content changed - Stage 3 must never modify this file")


if __name__ == "__main__":
    unittest.main()
