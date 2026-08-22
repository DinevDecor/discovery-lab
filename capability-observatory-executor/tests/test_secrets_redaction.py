import _pathsetup  # noqa: F401
import unittest

from capability_observatory_executor.envelope import ExecutorSubmission
from capability_observatory_executor.secrets import (
    SecretLeakError,
    assert_no_secret_leak,
    assert_submission_has_no_secret,
)


class LeakDetectionTests(unittest.TestCase):
    def test_raises_when_secret_appears_verbatim(self):
        with self.assertRaises(SecretLeakError):
            assert_no_secret_leak("token=sk-live-abc123xyz", known_secrets=["sk-live-abc123xyz"])

    def test_does_not_raise_when_secret_absent(self):
        assert_no_secret_leak("ordinary raw HTML content", known_secrets=["sk-live-abc123xyz"])

    def test_empty_text_never_raises(self):
        assert_no_secret_leak("", known_secrets=["sk-live-abc123xyz"])

    def test_no_known_secrets_never_raises(self):
        assert_no_secret_leak("anything at all", known_secrets=[])


class SubmissionRedactionTests(unittest.TestCase):
    def test_secret_in_notes_is_caught(self):
        submission = ExecutorSubmission(
            panel_item_id="C3-010", provider="provider_d_digikey", requested_url="https://x.test",
            fetched_at="2026-08-16T12:00:00Z", capture_method="api", executor="automation:x",
            outcome="credentials_error", error_category="oauth_token_rejected",
            notes="server said client_secret=sk-live-abc123xyz was invalid",
        )
        c3_submission = submission.to_c3_submission()
        with self.assertRaises(SecretLeakError):
            assert_submission_has_no_secret(c3_submission, known_secrets=["sk-live-abc123xyz"])

    def test_secret_in_raw_payload_is_caught(self):
        submission = ExecutorSubmission(
            panel_item_id="C3-010", provider="provider_d_digikey", requested_url="https://x.test",
            fetched_at="2026-08-16T12:00:00Z", capture_method="api", executor="automation:x",
            outcome="ok", raw_payload='{"echoed_request_header": "Authorization: Bearer sk-live-abc123xyz"}',
            observation={"identity_values": {}},
        )
        c3_submission = submission.to_c3_submission()
        with self.assertRaises(SecretLeakError):
            assert_submission_has_no_secret(c3_submission, known_secrets=["sk-live-abc123xyz"])

    def test_secret_inside_nested_observation_dict_is_caught(self):
        submission = ExecutorSubmission(
            panel_item_id="C3-010", provider="provider_d_digikey", requested_url="https://x.test",
            fetched_at="2026-08-16T12:00:00Z", capture_method="api", executor="automation:x",
            outcome="ok", raw_payload="ok",
            observation={"identity_values": {"manufacturer": "leaked sk-live-abc123xyz in a field"}},
        )
        c3_submission = submission.to_c3_submission()
        with self.assertRaises(SecretLeakError):
            assert_submission_has_no_secret(c3_submission, known_secrets=["sk-live-abc123xyz"])

    def test_clean_submission_passes(self):
        submission = ExecutorSubmission(
            panel_item_id="C3-010", provider="provider_d_digikey", requested_url="https://x.test",
            fetched_at="2026-08-16T12:00:00Z", capture_method="api", executor="automation:x",
            outcome="ok", raw_payload="clean content", observation={"identity_values": {}},
        )
        c3_submission = submission.to_c3_submission()
        assert_submission_has_no_secret(c3_submission, known_secrets=["sk-live-abc123xyz"])


if __name__ == "__main__":
    unittest.main()
