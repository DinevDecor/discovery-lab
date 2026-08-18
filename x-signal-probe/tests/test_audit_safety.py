"""Static safety verification for the audit subsystem, same detector
design as tests/test_safety.py. Makes the audit's own boundary a build
failure, not just CONTRACT.md/audit/README.md prose:

  - no destructive/git-action call anywhere;
  - no model/LLM call anywhere;
  - a network call may only happen in audit_client.py;
  - a file may only be opened in a writing mode from audit_io.py;
  - no audit module ever imports or calls client.search_recent, and
    none references config/queries.json - "no new discovery search" is
    enforced, not just documented;
  - no audit module imports ca_agents or business_candidate_analyst;
  - AuditSampleEntry/AuditVerdict never grow a text/quote field.
"""

import _pathsetup  # noqa: F401
import re
import unittest
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
_AUDIT_MODULES = sorted(_SRC_ROOT.glob("x_signal_probe/audit_*.py"))

_ALLOWED_WRITE_MODULES = {"audit_io.py"}
_ALLOWED_NETWORK_MODULES = {"audit_client.py"}

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
]

_FORBIDDEN_MODEL = ["anthropic", "call_claude", "ANTHROPIC_API_KEY", "openai", "ChatCompletion"]

_NETWORK_NEEDLES = [
    "urllib.request",
    "urllib.error",
    "requests.",
    "httpx.",
    "http.client",
    "socket.",
    "aiohttp",
]

_WRITE_MODE_PATTERN = re.compile(r"open\([^)]*['\"][wax][b+]?['\"]|\.write_text\(|\.write_bytes\(")
_UPSTREAM_IMPORT_PATTERN = re.compile(
    r"^\s*(import\s+ca_agents\b|from\s+ca_agents\b|"
    r"import\s+business_candidate_analyst\b|from\s+business_candidate_analyst\b)",
    re.MULTILINE,
)
_SEARCH_RECENT_PATTERN = re.compile(r"\bsearch_recent\b")
_QUERIES_JSON_PATTERN = re.compile(r"queries\.json")

_TRIPLE_QUOTED = re.compile(r'("""|\'\'\')(?:(?!\1).)*\1', re.DOTALL)
_LINE_COMMENT = re.compile(r"#.*")


def _code_only(text: str) -> str:
    """Strips triple-quoted docstrings and line comments before scanning
    for search_recent/queries.json references - several modules here
    legitimately *mention* those names in prose to document what they
    deliberately do NOT do (e.g. "never imports client.search_recent").
    Only an actual code reference is the violation these checks exist to
    catch, matching the precedent in test_safety.py's own ca_agents-import
    check (docstring mentions are fine; an executable coupling is not)."""
    return _LINE_COMMENT.sub("", _TRIPLE_QUOTED.sub("", text))


class AuditSafetyTests(unittest.TestCase):
    def test_audit_modules_exist_to_scan(self):
        self.assertGreater(len(_AUDIT_MODULES), 0)

    def test_no_forbidden_destructive_call_anywhere(self):
        for path in _AUDIT_MODULES:
            text = path.read_text(encoding="utf-8")
            for pattern in _FORBIDDEN_ANYWHERE:
                self.assertIsNone(re.search(pattern, text), f"{pattern!r} found in {path.name}")

    def test_no_model_call_anywhere(self):
        for path in _AUDIT_MODULES:
            text = path.read_text(encoding="utf-8")
            for needle in _FORBIDDEN_MODEL:
                self.assertNotIn(needle, text, f"{path.name} references {needle!r}")

    def test_network_call_only_in_audit_client_module(self):
        for path in _AUDIT_MODULES:
            text = path.read_text(encoding="utf-8")
            if any(needle in text for needle in _NETWORK_NEEDLES):
                self.assertIn(path.name, _ALLOWED_NETWORK_MODULES, f"{path.name} makes a network call")

    def test_write_mode_file_opens_only_in_audit_io(self):
        for path in _AUDIT_MODULES:
            text = path.read_text(encoding="utf-8")
            if _WRITE_MODE_PATTERN.search(text) and path.name not in _ALLOWED_WRITE_MODULES:
                self.fail(f"{path.name} opens a file in a writing mode outside {_ALLOWED_WRITE_MODULES}")

    def test_no_audit_module_imports_ca_agents_or_bca(self):
        for path in _AUDIT_MODULES:
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(_UPSTREAM_IMPORT_PATTERN.search(text), f"{path.name} imports upstream CA/BCA code")

    def test_no_audit_module_references_search_recent(self):
        # audit_review.py and audit_client.py's own module-level names
        # legitimately contain "search" nowhere - this directly encodes
        # "no new discovery search is required/possible" as a build
        # failure if it ever becomes false.
        for path in _AUDIT_MODULES:
            code = _code_only(path.read_text(encoding="utf-8"))
            self.assertIsNone(_SEARCH_RECENT_PATTERN.search(code), f"{path.name} references search_recent in code")

    def test_no_audit_module_references_queries_json(self):
        for path in _AUDIT_MODULES:
            code = _code_only(path.read_text(encoding="utf-8"))
            self.assertIsNone(_QUERIES_JSON_PATTERN.search(code), f"{path.name} references queries.json in code")

    def test_search_recent_pattern_actually_detects_a_violation(self):
        self.assertIsNotNone(_SEARCH_RECENT_PATTERN.search("from .client import search_recent"))

    def test_no_persisted_model_carries_raw_text_or_author_identifier(self):
        models_text = (_SRC_ROOT / "x_signal_probe" / "audit_models.py").read_text(encoding="utf-8")
        for cls_name in ("AuditSampleEntry", "AuditVerdict"):
            start = models_text.index(f"class {cls_name}:")
            rest = models_text[start + len(f"class {cls_name}:"):]
            end = re.search(r"\n\S", rest)
            block = rest if end is None else rest[: end.start()]
            for forbidden in ("text:", "quote", "author_id", "raw_text"):
                self.assertNotIn(forbidden, block, f"{cls_name} must not carry a field matching {forbidden!r}")


class TopLevelScriptSafetyTests(unittest.TestCase):
    """review_audit_sample.py legitimately prints post text to the
    terminal (that's the whole point - see audit/README.md) but must
    never write it to a file. This checks the CLI scripts directly."""

    _ROOT = Path(__file__).resolve().parents[1]

    def test_review_script_never_opens_a_file_in_writing_mode_directly(self):
        text = (self._ROOT / "review_audit_sample.py").read_text(encoding="utf-8")
        self.assertIsNone(
            _WRITE_MODE_PATTERN.search(text),
            "review_audit_sample.py must persist only via audit_io.append_verdict_line, "
            "never open a file itself",
        )

    def test_review_script_calls_get_bearer_token_not_hardcoded(self):
        text = (self._ROOT / "review_audit_sample.py").read_text(encoding="utf-8")
        self.assertIn("get_bearer_token", text)

    def test_review_script_does_not_import_search_recent(self):
        code = _code_only((self._ROOT / "review_audit_sample.py").read_text(encoding="utf-8"))
        self.assertIsNone(_SEARCH_RECENT_PATTERN.search(code))

    def test_select_script_never_opens_a_file_in_writing_mode_directly(self):
        text = (self._ROOT / "select_audit_sample.py").read_text(encoding="utf-8")
        # allow the read-mode open() of --observations; forbid any write-mode open()
        self.assertIsNone(_WRITE_MODE_PATTERN.search(text))

    def test_select_script_does_not_call_x_api(self):
        text = (self._ROOT / "select_audit_sample.py").read_text(encoding="utf-8")
        for needle in _NETWORK_NEEDLES:
            self.assertNotIn(needle, text)

    def test_rehydrate_availability_only_never_opens_a_file_in_writing_mode(self):
        text = (self._ROOT / "rehydrate_availability_only.py").read_text(encoding="utf-8")
        self.assertIsNone(
            _WRITE_MODE_PATTERN.search(text),
            "rehydrate_availability_only.py must never write to a file - output is stdout only",
        )

    def test_rehydrate_availability_only_never_reads_the_text_field(self):
        code = _code_only((self._ROOT / "rehydrate_availability_only.py").read_text(encoding="utf-8"))
        self.assertNotIn(
            '["text"]', code,
            "rehydrate_availability_only.py must never read found[pid]['text'] - "
            "only availability (dict membership) may be derived from the lookup result",
        )
        self.assertNotIn("['text']", code)

    def test_rehydrate_availability_only_does_not_import_search_recent(self):
        code = _code_only((self._ROOT / "rehydrate_availability_only.py").read_text(encoding="utf-8"))
        self.assertIsNone(_SEARCH_RECENT_PATTERN.search(code))

    def test_rehydrate_availability_only_calls_get_bearer_token(self):
        text = (self._ROOT / "rehydrate_availability_only.py").read_text(encoding="utf-8")
        self.assertIn("get_bearer_token", text)


if __name__ == "__main__":
    unittest.main()
