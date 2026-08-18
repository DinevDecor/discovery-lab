"""Static safety verification, same detector design as every other
package's own tests/test_safety.py.

Task instruction: 'Preserve the hard read-only boundary. No Stage 5, no
actions, no mutation buttons.' - proven here structurally.
"""

import _pathsetup  # noqa: F401
import re
import unittest
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
_PKG_ROOT = Path(__file__).resolve().parents[1]
_SITE_ROOT = _PKG_ROOT / "site"
_REPO_ROOT = _PKG_ROOT.parent

_WRITE_MODE_PATTERN = re.compile(r"open\([^)]*['\"][wax][b+]?['\"]|\.write_text\(|\.write_bytes\(")

_MODEL_CLIENT_MARKERS = ("anthropic", "openai", "call_claude", "call_openai", "ANTHROPIC_API_KEY", "OPENAI_API_KEY")

_HARDCODED_SECRET = re.compile(r"(sk-[A-Za-z0-9_-]{20,}|sk-ant-[A-Za-z0-9_-]{20,})")

_PRODUCTION_DATA_WRITE_MARKERS = (
    "constraint-archaeology-agents/data", "business-candidate-analyst/data",
    "blind-analysis-kernel/data", "case-claim-kernel/data", "adversarial-review-kernel/data",
    "prospective-ground-truth/data",
)


def _all_library_source_files():
    return sorted(_SRC_ROOT.rglob("*.py"))


class SourceModulesAreReadOnlyTests(unittest.TestCase):
    """Every module under src/mobile_console/ is 100% read-only - the
    CLI (run_mobile_console.py) is the only file in this package
    permitted to write, and even it only ever writes this package's own
    data/ and site/data.json."""

    def test_no_write_mode_open_anywhere_under_src(self):
        for path in _all_library_source_files():
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(_WRITE_MODE_PATTERN.search(text),
                               f"{path.name} opens a file in a writing mode - src/ must be 100% read-only")

    def test_write_mode_pattern_actually_detects_a_violation(self):
        self.assertRegex("open('x.json', 'w')", _WRITE_MODE_PATTERN)


class CliWritesOnlyToOwnPathsTests(unittest.TestCase):
    def test_cli_never_writes_to_another_packages_data_directory(self):
        cli_path = _PKG_ROOT / "run_mobile_console.py"
        text = cli_path.read_text(encoding="utf-8")
        for marker in _PRODUCTION_DATA_WRITE_MARKERS:
            self.assertNotIn(marker, text)

    def test_cli_default_outputs_are_scoped_to_this_package(self):
        cli_path = _PKG_ROOT / "run_mobile_console.py"
        text = cli_path.read_text(encoding="utf-8")
        self.assertIn('os.path.join(ROOT, "data", "snapshot.json")', text)
        self.assertIn('os.path.join(ROOT, "site", "data.json")', text)


class NoModelOrNetworkCallTests(unittest.TestCase):
    def test_no_model_client_marker_anywhere_in_python_source(self):
        files = _all_library_source_files() + [_PKG_ROOT / "run_mobile_console.py"]
        for path in files:
            text = path.read_text(encoding="utf-8")
            for marker in _MODEL_CLIENT_MARKERS:
                self.assertNotIn(marker, text, f"{path.name} references {marker!r}")

    def test_no_hardcoded_secret_anywhere(self):
        files = _all_library_source_files() + [_PKG_ROOT / "run_mobile_console.py"]
        for path in files:
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(_HARDCODED_SECRET.search(text))


class NoMutationSurfaceInSiteTests(unittest.TestCase):
    """Task instruction: 'No Stage 5, no actions, no mutation buttons.'
    The static site's own JS must contain no fetch() call using a
    mutating HTTP method, no form POST, and no reference to a write
    endpoint - it is a read-only viewer over a pre-built JSON snapshot,
    structurally incapable of writing anything back anywhere."""

    def _site_js_and_html(self):
        if not _SITE_ROOT.exists():
            self.skipTest("site/ not built yet")
        return list(_SITE_ROOT.rglob("*.js")) + list(_SITE_ROOT.rglob("*.html"))

    def test_no_mutating_http_method_anywhere_in_the_site(self):
        for path in self._site_js_and_html():
            text = path.read_text(encoding="utf-8")
            for method in ("method: 'POST'", 'method: "POST"', "method: 'PUT'", 'method: "PUT"',
                           "method: 'DELETE'", 'method: "DELETE"', "method: 'PATCH'", 'method: "PATCH"'):
                self.assertNotIn(method, text, f"{path.name} contains a mutating fetch method: {method}")

    def test_no_form_element_in_the_site(self):
        for path in self._site_js_and_html():
            if path.suffix == ".html":
                text = path.read_text(encoding="utf-8")
                self.assertNotIn("<form", text.lower())

    def test_no_stage5_or_trust_engine_reference_in_the_site(self):
        for path in self._site_js_and_html():
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("Stage 5", text)
            self.assertNotIn("Trust Engine", text)


if __name__ == "__main__":
    unittest.main()
