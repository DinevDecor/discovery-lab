"""Static safety verification for the executor package.

Inverted from capability-observatory's own test_safety.py: THIS package is
allowed -- expected -- to make network calls, since fetching is its whole
job. What must still hold:

  1. Every network call goes through the one seam (transport.py) --
     nothing else in this package imports urllib/http.client/socket/
     requests/httpx directly. This is what makes offline, deterministic
     tests possible everywhere else (inject FakeTransport instead of
     mocking a dozen different network entry points).
  2. This package never performs a destructive or git-action call
     (subprocess push/commit/merge, os.remove, shutil.rmtree) -- the
     commit step lives in the GitHub Actions workflow YAML, not here, same
     separation C3's own capture_intake.py keeps from storage.py's git-free
     append-only writes.
  3. capability-observatory/src/capability_observatory/ -- the package this
     one calls into -- still has no network client reference anywhere in
     it. This mirrors capability-observatory/tests/test_safety.py's own
     check as a second, independent guard: if Slice 03's changes to
     models.py or elsewhere ever accidentally introduced a network import
     into that package, this test catches it too, from the other side.

No test in this suite requires live internet access.
"""

import _pathsetup  # noqa: F401
import re
import unittest
from pathlib import Path

_EXECUTOR_SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
_C3_SRC_ROOT = Path(__file__).resolve().parents[2] / "capability-observatory" / "src"

_NETWORK_NEEDLES = [
    "urllib.request", "urllib.error", "http.client", "socket.",
    "requests.", "httpx.", "aiohttp", "WebFetch", "WebSearch",
]

_ALLOWED_NETWORK_FILE = "transport.py"

_FORBIDDEN_DESTRUCTIVE = [
    r"^\s*import subprocess\b",
    r"\bos\.remove\(",
    r"\bos\.unlink\(",
    r"\bshutil\.rmtree\(",
    r"\.push\(",
    r"\.commit\(",
    r"\.merge\(",
]

# cli.py legitimately shells out to the EXISTING, unmodified
# run_capability_observatory.py process -- that is not a destructive/git
# action, it's calling C3's own validated entry point exactly as the
# existing capability-observatory.yml workflow does. Exempted explicitly,
# by filename, rather than loosening the pattern for everyone else.
_SUBPROCESS_ALLOWED_FILE = "cli.py"


def _iter_source_files(root: Path):
    return sorted(root.rglob("*.py"))


class NetworkIsolatedToTransportTests(unittest.TestCase):
    def test_source_files_exist_to_scan(self):
        files = _iter_source_files(_EXECUTOR_SRC_ROOT)
        self.assertGreater(len(files), 0)

    def test_network_client_only_appears_in_transport_py(self):
        offenders = []
        for path in _iter_source_files(_EXECUTOR_SRC_ROOT):
            if path.name == _ALLOWED_NETWORK_FILE:
                continue
            text = path.read_text(encoding="utf-8")
            for needle in _NETWORK_NEEDLES:
                if needle in text:
                    offenders.append(f"{path.relative_to(_EXECUTOR_SRC_ROOT)}: contains {needle!r}")
        self.assertEqual(offenders, [], "network client reference(s) outside transport.py:\n" + "\n".join(offenders))

    def test_transport_py_actually_contains_the_real_network_client(self):
        text = (_EXECUTOR_SRC_ROOT / "capability_observatory_executor" / "transport.py").read_text(encoding="utf-8")
        self.assertIn("urllib.request", text)

    def test_detector_actually_catches_a_real_violation(self):
        sample = "import requests\nrequests.get('https://example.test')\n"
        self.assertTrue(any(needle in sample for needle in _NETWORK_NEEDLES))


class NoDestructiveOrGitActionCallsTests(unittest.TestCase):
    def test_no_destructive_or_git_action_calls_outside_the_allowed_subprocess_call(self):
        offenders = []
        for path in _iter_source_files(_EXECUTOR_SRC_ROOT):
            text = path.read_text(encoding="utf-8")
            for pattern in _FORBIDDEN_DESTRUCTIVE:
                if re.search(pattern, text, re.MULTILINE):
                    if "subprocess" in pattern and path.name == _SUBPROCESS_ALLOWED_FILE:
                        continue
                    offenders.append(f"{path.relative_to(_EXECUTOR_SRC_ROOT)}: matches {pattern!r}")
        self.assertEqual(offenders, [], "destructive/git-action call(s) found:\n" + "\n".join(offenders))

    def test_cli_py_subprocess_call_targets_the_existing_unmodified_c3_entry_point_only(self):
        text = (_EXECUTOR_SRC_ROOT / "capability_observatory_executor" / "cli.py").read_text(encoding="utf-8")
        self.assertIn("run_capability_observatory.py", text)
        self.assertNotIn("git ", text)
        self.assertNotIn("git push", text)


class C3PackageStillHasNoNetworkClientTests(unittest.TestCase):
    """Independent, second guard mirroring capability-observatory's own
    tests/test_safety.py -- catches a regression from Slice 03's own
    changes (models.py) specifically, from this package's side."""

    def test_c3_source_still_has_no_network_client_reference(self):
        offenders = []
        for path in _iter_source_files(_C3_SRC_ROOT):
            text = path.read_text(encoding="utf-8")
            for needle in _NETWORK_NEEDLES:
                if needle in text:
                    offenders.append(f"{path.relative_to(_C3_SRC_ROOT)}: contains {needle!r}")
        self.assertEqual(offenders, [], "network client reference(s) found in capability_observatory:\n" + "\n".join(offenders))


if __name__ == "__main__":
    unittest.main()
