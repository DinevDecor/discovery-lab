"""Static safety verification, same detector design as
`adversarial_review_kernel.tests.test_safety`/`constraint_change_observatory
.tests.test_safety` and their own precedents.

Task Sec 14/17: 'no Stage 1-4 production semantics modified', 'no CA/BCA
lifecycle writes', 'no scheduling', 'no Trust Engine activation' - all
proven here structurally, not just documented.
"""

import _pathsetup  # noqa: F401
import re
import unittest
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
_PKG_ROOT = Path(__file__).resolve().parents[1]
_REPO_ROOT = _PKG_ROOT.parent

_WRITE_MODE_PATTERN = re.compile(r"open\([^)]*['\"][wax][b+]?['\"]|\.write_text\(|\.write_bytes\(")
_ALLOWED_WRITE_MODULES = {"ledger.py"}

# Zero cross-package import - this package is a wholly separate evidence
# stream, same boundary constraint_change_observatory's own CONTRACT.md
# states explicitly ("Not connected to Constraint Archaeology or Business
# Candidate Analyst").
_OTHER_PACKAGE_IMPORT = re.compile(
    r"^\s*(import\s+(ca_agents|case_claim_kernel|gpt_mechanism_judge|blind_analysis_kernel|"
    r"adversarial_review_kernel|business_candidate_analyst|calendar_arbitrage_watch|"
    r"constraint_change_observatory|x_signal_probe|capability_observatory)\b|"
    r"from\s+(ca_agents|case_claim_kernel|gpt_mechanism_judge|blind_analysis_kernel|"
    r"adversarial_review_kernel|business_candidate_analyst|calendar_arbitrage_watch|"
    r"constraint_change_observatory|x_signal_probe|capability_observatory)\b)",
    re.MULTILINE,
)

_MODEL_CLIENT_MARKERS = ("anthropic", "openai", "call_claude", "call_openai",
                          "ANTHROPIC_API_KEY", "OPENAI_API_KEY", "requests.", "urllib.request")

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

_PRODUCTION_DATA_PATH_MARKERS = (
    "constraint-archaeology-agents/data", "business-candidate-analyst/data",
    "calendar-arbitrage-watch/data", "blind-analysis-kernel/data",
    "case-claim-kernel/data", "adversarial-review-kernel/data",
    "constraint-change-observatory/data", "x-signal-probe/data",
    "capability-observatory/data",
)


def _all_library_source_files():
    return sorted(_SRC_ROOT.rglob("*.py"))


def _all_package_files():
    files = list(_all_library_source_files())
    run_cli = _PKG_ROOT / "run_prospective_ground_truth.py"
    if run_cli.exists():
        files.append(run_cli)
    return files


class ZeroCrossPackageImportTests(unittest.TestCase):
    """Task Sec 17: no CA/BCA lifecycle writes, no Stage 1-4 semantics
    touched - the strongest structural proof of both is that this
    package never even imports any of those packages' code."""

    def test_no_module_imports_another_packages_code(self):
        for path in _all_package_files():
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(_OTHER_PACKAGE_IMPORT.search(text),
                               f"{path.name} imports another package's code - this package must be standalone")

    def test_pattern_actually_detects_a_violation(self):
        self.assertIsNotNone(_OTHER_PACKAGE_IMPORT.search("from ca_agents.llm import call_claude"))
        self.assertIsNotNone(_OTHER_PACKAGE_IMPORT.search("import business_candidate_analyst.registry"))


class NoModelOrNetworkCallTests(unittest.TestCase):
    """Task Sec 8/15: 'Models are never resolution evidence', 'do not
    call this a calibration system' - this package makes no model or
    network call anywhere, structurally."""

    def test_no_model_client_marker_anywhere_in_package(self):
        for path in _all_package_files():
            text = path.read_text(encoding="utf-8")
            for marker in _MODEL_CLIENT_MARKERS:
                self.assertNotIn(marker, text, f"{path.name} references {marker!r} - this package must call no model")


class NoWriteModeOutsideLedgerTests(unittest.TestCase):
    def test_no_write_mode_open_outside_ledger(self):
        for path in _all_library_source_files():
            if path.name in _ALLOWED_WRITE_MODULES:
                continue
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(_WRITE_MODE_PATTERN.search(text),
                               f"{path.name} opens a file in a writing mode outside ledger.py")

    def test_ledger_module_actually_writes(self):
        text = (_SRC_ROOT / "prospective_ground_truth" / "ledger.py").read_text(encoding="utf-8")
        self.assertRegex(text, _WRITE_MODE_PATTERN)

    def test_write_mode_pattern_actually_detects_a_violation(self):
        self.assertRegex("open('x.jsonl', 'a')", _WRITE_MODE_PATTERN)


class NeverWritesToProductionDataTests(unittest.TestCase):
    """Task Sec 17: 'no CA/BCA lifecycle writes'."""

    def test_ledger_module_never_mentions_another_packages_data_directory(self):
        text = (_SRC_ROOT / "prospective_ground_truth" / "ledger.py").read_text(encoding="utf-8")
        for marker in _PRODUCTION_DATA_PATH_MARKERS:
            self.assertNotIn(marker, text)

    def test_cli_default_ledger_paths_are_scoped_to_this_package(self):
        text = (_PKG_ROOT / "run_prospective_ground_truth.py").read_text(encoding="utf-8")
        self.assertIn('os.path.join(ROOT, "data", "cases.jsonl")', text)
        self.assertIn('os.path.join(ROOT, "data", "resolutions.jsonl")', text)
        for marker in _PRODUCTION_DATA_PATH_MARKERS:
            self.assertNotIn(marker, text)


class NoSchedulingTests(unittest.TestCase):
    """Task Sec 9/17: 'initial intake must remain manual' / 'no
    scheduled job'. No GitHub Actions workflow file exists for this
    package - checked against the real repo-wide workflows directory."""

    def test_no_github_actions_workflow_references_this_package(self):
        workflows_dir = _REPO_ROOT / ".github" / "workflows"
        if not workflows_dir.exists():
            self.skipTest("no .github/workflows directory in this checkout")
        for path in workflows_dir.glob("*.yml"):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("prospective-ground-truth", text,
                              f"{path.name} references prospective-ground-truth - intake must stay manual")

    def test_no_cron_or_schedule_keyword_anywhere_in_package(self):
        for path in _all_package_files():
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("schedule:", text)
            self.assertNotIn("cron(", text)


class NoTrustEngineOrStage5Tests(unittest.TestCase):
    def test_no_trust_engine_reference_anywhere_in_package(self):
        for path in _all_package_files():
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("Trust Engine", text)
            self.assertNotIn("trust_engine", text)

    def test_no_stage5_or_router_reference_anywhere_in_package(self):
        for path in _all_package_files():
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("Stage 5", text)
            self.assertNotIn("stage5", text.lower().replace(" ", ""))


class NoHardcodedSecretTests(unittest.TestCase):
    def test_no_hardcoded_key_anywhere_in_package(self):
        for path in _all_package_files():
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(_HARDCODED_SECRET.search(text),
                               f"{path.name} appears to contain a hardcoded provider secret literal")

    def test_secret_pattern_actually_detects_a_violation(self):
        self.assertIsNotNone(_HARDCODED_SECRET.search("sk-" + "a" * 25))


class NoForbiddenCallsTests(unittest.TestCase):
    def test_no_forbidden_call_anywhere_in_source(self):
        for path in _all_package_files():
            text = path.read_text(encoding="utf-8")
            for pattern in _FORBIDDEN_ANYWHERE:
                self.assertIsNone(re.search(pattern, text), f"forbidden pattern {pattern!r} in {path.name}")


class NoCalibrationOrScoringLogicTests(unittest.TestCase):
    """Task Sec 15: 'do not compute model reliability', 'do not assign
    model weights'. This is a stream, not a scorer - no module DEFINES a
    function/class/variable computing an aggregate accuracy/reliability/
    weight value from Resolution data. (Prose explaining that no such
    logic exists - as several module docstrings here do, citing Sec 15
    by name - legitimately contains this vocabulary and is not itself a
    violation, so this checks identifier definitions, not free text.)"""

    _DEFINITION_PATTERN = re.compile(
        r"^\s*(def|class)\s+\w*(model_weight|reliability_score|calibrat)\w*\s*[:(]|"
        r"^\s*\w*(model_weight|reliability_score|calibrat)\w*\s*(:\s*\w+\s*)?=",
        re.MULTILINE | re.IGNORECASE,
    )

    def test_no_calibration_or_weighting_definition_in_source(self):
        for path in _all_library_source_files():
            text = path.read_text(encoding="utf-8")
            match = self._DEFINITION_PATTERN.search(text)
            self.assertIsNone(match, f"{path.name} defines a calibration/weighting identifier: {match}")

    def test_pattern_actually_detects_a_violation(self):
        self.assertIsNotNone(self._DEFINITION_PATTERN.search("def compute_reliability_score(x):\n    pass"))
        self.assertIsNotNone(self._DEFINITION_PATTERN.search("model_weight = 0.5"))


if __name__ == "__main__":
    unittest.main()
