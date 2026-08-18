"""Static safety verification, same detector design as
observation-agent/tests/test_safety.py, headquarters/tests/test_safety.py,
reality-sensor/tests/test_safety.py, capability-observatory/tests/test_safety.py
and business-candidate-analyst/tests/test_safety.py. This package's whole reason
for existing is a bounded, isolated, probe-only experiment (CONTRACT.md), so this
test makes that boundary a build failure, not just a docstring:

  - no destructive/git-action call anywhere;
  - no model/LLM call anywhere - classification is fully deterministic;
  - a network call may only happen in client.py - nowhere else reaches out to
    the X API or anything else;
  - a file may only be opened in a writing mode from probe.py or report.py - the
    only modules that persist ProbeObservations or render the report, both
    confined to x-signal-probe/data and x-signal-probe/reports;
  - no module imports ca_agents or business_candidate_analyst, so there is no
    code path back into Constraint Archaeology or Business Candidate Analyst;
  - models.ProbeObservation - the only shape ever written to disk - never grows
    a text/quote/author-identifier field (data-minimization rule), as a static
    belt-and-suspenders alongside test_secret_never_persisted.py's dynamic check.
"""

import _pathsetup  # noqa: F401
import re
import unittest
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[1] / "src"

_ALLOWED_WRITE_MODULES = {"probe.py", "report.py"}
_ALLOWED_NETWORK_MODULES = {"client.py"}

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

_PROBE_OBSERVATION_FORBIDDEN_FIELDS = ("text:", "quote", "evidence_quote", "raw_text", "author_id")


def _all_source_files():
    return sorted(_SRC_ROOT.rglob("*.py"))


class SafetyTests(unittest.TestCase):
    def test_source_files_exist_to_scan(self):
        self.assertGreater(len(_all_source_files()), 0)

    def test_no_forbidden_destructive_call_anywhere(self):
        for path in _all_source_files():
            text = path.read_text(encoding="utf-8")
            for pattern in _FORBIDDEN_ANYWHERE:
                self.assertIsNone(
                    re.search(pattern, text),
                    f"Forbidden pattern {pattern!r} found in {path.relative_to(_SRC_ROOT)}",
                )

    def test_no_model_call_anywhere(self):
        for path in _all_source_files():
            text = path.read_text(encoding="utf-8")
            for needle in _FORBIDDEN_MODEL:
                self.assertNotIn(
                    needle,
                    text,
                    f"{path.relative_to(_SRC_ROOT)} references {needle!r} - this probe must stay "
                    "fully deterministic, no model call anywhere.",
                )

    def test_network_call_only_in_client_module(self):
        for path in _all_source_files():
            text = path.read_text(encoding="utf-8")
            if any(needle in text for needle in _NETWORK_NEEDLES):
                self.assertIn(
                    path.name,
                    _ALLOWED_NETWORK_MODULES,
                    f"{path.relative_to(_SRC_ROOT)} makes a network call but is not the allowed "
                    f"client module {_ALLOWED_NETWORK_MODULES}",
                )

    def test_write_mode_file_opens_only_in_allowed_modules(self):
        for path in _all_source_files():
            text = path.read_text(encoding="utf-8")
            if _WRITE_MODE_PATTERN.search(text) and path.name not in _ALLOWED_WRITE_MODULES:
                self.fail(
                    f"{path.relative_to(_SRC_ROOT)} opens a file in a writing mode but is not in "
                    f"the allowed-write list {_ALLOWED_WRITE_MODULES}"
                )

    def test_at_least_the_expected_write_call_exists(self):
        probe_text = (_SRC_ROOT / "x_signal_probe" / "probe.py").read_text(encoding="utf-8")
        self.assertRegex(probe_text, _WRITE_MODE_PATTERN)

    def test_no_module_imports_ca_agents_or_business_candidate_analyst(self):
        for path in _all_source_files():
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(
                _UPSTREAM_IMPORT_PATTERN.search(text),
                f"{path.relative_to(_SRC_ROOT)} imports upstream CA/BCA code - forbidden",
            )

    def test_upstream_import_pattern_actually_detects_a_violation(self):
        self.assertIsNotNone(_UPSTREAM_IMPORT_PATTERN.search("from ca_agents.memory import classify_function"))
        self.assertIsNotNone(
            _UPSTREAM_IMPORT_PATTERN.search("import business_candidate_analyst.registry")
        )

    def test_forbidden_patterns_actually_detect_violations(self):
        samples = {
            r"\bsubprocess\.": "import subprocess\nsubprocess.run(['git', 'push'])",
            r"\.push\(": "repo.push()",
            r"\.commit\(": "repo.index.commit('msg')",
            r"\bos\.remove\(": "os.remove(path)",
        }
        for pattern, sample in samples.items():
            self.assertRegex(sample, pattern, f"pattern {pattern!r} failed to match its own positive sample")

    def test_write_mode_pattern_actually_detects_a_violation(self):
        self.assertRegex("open('x.json', 'w')", _WRITE_MODE_PATTERN)
        self.assertRegex("open('x.jsonl', 'a', encoding='utf-8')", _WRITE_MODE_PATTERN)
        self.assertIsNone(_WRITE_MODE_PATTERN.search("open('x.json', encoding='utf-8')"))

    def test_probe_observation_never_persists_raw_text_or_author_identifier(self):
        models_text = (_SRC_ROOT / "x_signal_probe" / "models.py").read_text(encoding="utf-8")
        start = models_text.index("class ProbeObservation:")
        rest = models_text[start + len("class ProbeObservation:"):]
        # The dataclass body ends at the first line that isn't indented
        # (i.e. dedents back to column 0) - never just at the next
        # "class ", which would also match top-level functions defined
        # after this class (e.g. text_hash()'s own `text: str` parameter).
        end = re.search(r"\n\S", rest)
        block = rest if end is None else rest[: end.start()]
        for forbidden in _PROBE_OBSERVATION_FORBIDDEN_FIELDS:
            self.assertNotIn(
                forbidden,
                block,
                f"ProbeObservation must not carry a field matching {forbidden!r} - data minimization rule",
            )


if __name__ == "__main__":
    unittest.main()
