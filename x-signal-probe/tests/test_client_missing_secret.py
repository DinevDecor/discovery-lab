import _pathsetup  # noqa: F401
import unittest

from x_signal_probe import client


class MissingSecretTests(unittest.TestCase):
    def test_absent_token_raises(self):
        with self.assertRaises(client.MissingSecretError):
            client.get_bearer_token(env={})

    def test_empty_token_raises(self):
        with self.assertRaises(client.MissingSecretError):
            client.get_bearer_token(env={"X_BEARER_TOKEN": ""})

    def test_present_token_returned_verbatim(self):
        self.assertEqual(client.get_bearer_token(env={"X_BEARER_TOKEN": "abc123"}), "abc123")

    def test_no_hardcoded_fallback_credential(self):
        # A missing secret must never resolve to a non-empty string from
        # anywhere other than the env mapping passed in.
        with self.assertRaises(client.MissingSecretError):
            client.get_bearer_token(env={"SOME_OTHER_VAR": "not-the-token"})


if __name__ == "__main__":
    unittest.main()
