"""Static safety verification, same detector design as
blind-analysis-kernel/tests/test_safety.py and its own precedents.
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
_ALLOWED_WRITE_MODULES = {"ledger.py"}

# Only falsify.py may import another package's code - it IS the
# cross-falsification dispatch boundary (see its own docstring). Every
# other module here (models/identity/disagree/redact/prompts/validator/
# ledger/judgment) must be a standalone library.
_OTHER_PACKAGE_IMPORT = re.compile(
    r"^\s*(import\s+(ca_agents|case_claim_kernel|gpt_mechanism_judge|blind_analysis_kernel|business_candidate_analyst)\b|"
    r"from\s+(ca_agents|case_claim_kernel|gpt_mechanism_judge|blind_analysis_kernel|business_candidate_analyst)\b)",
    re.MULTILINE,
)

_NON_DISPATCH_LIBRARY_MODULES = (
    "models.py", "identity.py", "disagree.py", "redact.py", "prompts.py",
    "validator.py", "ledger.py", "judgment.py",
)

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

# Files Stage 4 must never modify (task §1/§6): the frozen mechanism gate
# and both providers' judge/transport modules it symmetrically reuses.
_PINNED_FILES = {
    "constraint-archaeology-agents/src/ca_agents/same_mechanism_gate.py":
        "0dfa74a84d8258ba511f809d723357bbfa992785efeb1d08c5df3368480a1225",
    "constraint-archaeology-agents/src/ca_agents/mechanism_judge.py":
        "c871842b3c0fc5132f0e66a5f5b1af90e0571e5d671826fe899e5a829d4ff418",
    "constraint-archaeology-agents/src/ca_agents/llm.py":
        "71e391d42dbc87cd11cb868d1b97f473257c0dc55d92502a5576ee2f8778d2ca",
    "gpt-mechanism-judge/src/gpt_mechanism_judge/openai_client.py":
        "ba262776b5f2acc96f1adc677229dec22797da78e024eb4579b24b1d76b02214",
    "blind-analysis-kernel/src/blind_analysis_kernel/dispatch.py":
        "9cc52d1a06ef6d3c977d1aee24cec34c865e2dedba2cf96a8c3785717cfea410",
    "blind-analysis-kernel/src/blind_analysis_kernel/packet.py":
        "2e6b44aca6583b172c601c0c90656e8b9576d1c0dd3bd8fe1fae4fae3baa6f45",
}

_CA_BCA_PATH_MARKERS = ("constraint-archaeology-agents/data", "business-candidate-analyst/data")


def _all_library_source_files():
    return sorted(_SRC_ROOT.rglob("*.py"))


def _all_package_files():
    files = list(_all_library_source_files())
    run_cli = _PKG_ROOT / "run_stage4_job.py"
    if run_cli.exists():
        files.append(run_cli)
    return files


class FalsifyIsTheOnlyCrossPackageImportTests(unittest.TestCase):
    def test_non_dispatch_library_modules_import_nothing_from_another_package(self):
        for name in _NON_DISPATCH_LIBRARY_MODULES:
            path = _SRC_ROOT / "adversarial_review_kernel" / name
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(_OTHER_PACKAGE_IMPORT.search(text),
                               f"{name} imports another package's code - only falsify.py may")

    def test_falsify_module_is_the_one_that_imports_the_other_packages(self):
        text = (_SRC_ROOT / "adversarial_review_kernel" / "falsify.py").read_text(encoding="utf-8")
        self.assertIsNotNone(_OTHER_PACKAGE_IMPORT.search(text))

    def test_pattern_actually_detects_a_violation(self):
        self.assertIsNotNone(_OTHER_PACKAGE_IMPORT.search("from ca_agents.llm import call_claude"))
        self.assertIsNotNone(_OTHER_PACKAGE_IMPORT.search("import blind_analysis_kernel.dispatch"))


class NoWriteModeOutsideLedgerTests(unittest.TestCase):
    def test_no_write_mode_open_outside_ledger(self):
        for path in _all_library_source_files():
            if path.name in _ALLOWED_WRITE_MODULES:
                continue
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(_WRITE_MODE_PATTERN.search(text),
                               f"{path.name} opens a file in a writing mode outside ledger.py")

    def test_ledger_module_actually_writes(self):
        text = (_SRC_ROOT / "adversarial_review_kernel" / "ledger.py").read_text(encoding="utf-8")
        self.assertRegex(text, _WRITE_MODE_PATTERN)

    def test_write_mode_pattern_actually_detects_a_violation(self):
        self.assertRegex("open('x.jsonl', 'a')", _WRITE_MODE_PATTERN)


class NeverWritesToCaBcaOrBlindAnalysisLedgerTests(unittest.TestCase):
    """Task §9/§12: 'do not write to CA/BCA ledgers', 'original analysis
    records untouched', 'CA/BCA lifecycle untouched'. The structural
    proof this needs already exists in `NoWriteModeOutsideLedgerTests`
    (only ledger.py may ever open a file in a writing mode); these tests
    add the specific check that ledger.py itself never even mentions a
    CA/BCA/blind-analysis-kernel path, so it could not write there even
    if a future edit tried to."""

    def test_ledger_module_never_mentions_another_packages_data_directory(self):
        text = (_SRC_ROOT / "adversarial_review_kernel" / "ledger.py").read_text(encoding="utf-8")
        for marker in _CA_BCA_PATH_MARKERS + ("blind-analysis-kernel",):
            self.assertNotIn(marker, text)

    def test_run_stage4_job_persist_subcommand_default_ledger_paths_are_scoped_to_this_package(self):
        text = (_PKG_ROOT / "run_stage4_job.py").read_text(encoding="utf-8")
        self.assertIn('os.path.join(ROOT, "data", "falsifications.jsonl")', text)
        self.assertIn('os.path.join(ROOT, "data", "judgments.jsonl")', text)


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
    def test_pinned_files_content_hash_unchanged(self):
        for rel_path, expected in _PINNED_FILES.items():
            path = _REPO_ROOT / rel_path
            if not path.exists():
                self.skipTest(f"{rel_path} not present in this checkout")
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(actual, expected, f"{rel_path} content changed - Stage 4 must never modify this file")


if __name__ == "__main__":
    unittest.main()
