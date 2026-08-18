import _pathsetup  # noqa: F401
import json
import os
import unittest
import urllib.error
from unittest.mock import patch

from gpt_mechanism_judge.openai_client import OpenAIError, call_openai, parse_json_object


class MissingKeyTests(unittest.TestCase):
    def test_missing_key_raises_openai_error(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(OpenAIError) as ctx:
                call_openai("system", "user")
        self.assertIn("OPENAI_API_KEY", str(ctx.exception))

    def test_missing_key_error_never_contains_a_key_value(self):
        """Even though there's no key to leak in this case, this test
        pins the exact error text so a future edit can't accidentally
        start interpolating a (possibly present-but-empty) key value in."""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(OpenAIError) as ctx:
                call_openai("system", "user")
        self.assertEqual(str(ctx.exception), "OPENAI_API_KEY is not set")


class TransportErrorTests(unittest.TestCase):
    def test_http_error_raises_openai_error_without_leaking_key(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-secret-value-12345"}):
            with patch("gpt_mechanism_judge.openai_client.urllib.request.urlopen") as mock_open:
                mock_open.side_effect = urllib.error.HTTPError(
                    "https://api.openai.com/v1/chat/completions", 401, "Unauthorized", {}, None)
                with self.assertRaises(OpenAIError) as ctx:
                    call_openai("system", "user")
        self.assertNotIn("sk-secret-value-12345", str(ctx.exception))
        self.assertIn("401", str(ctx.exception))

    def test_url_error_raises_openai_error(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-secret-value-12345"}):
            with patch("gpt_mechanism_judge.openai_client.urllib.request.urlopen") as mock_open:
                mock_open.side_effect = urllib.error.URLError("connection refused")
                with self.assertRaises(OpenAIError):
                    call_openai("system", "user")

    def test_key_is_only_ever_placed_in_the_authorization_header(self):
        captured = {}

        def _fake_urlopen(req, timeout=60):
            captured["headers"] = dict(req.header_items())
            captured["body"] = req.data

            class _Resp:
                def __enter__(self_inner):
                    return self_inner

                def __exit__(self_inner, *a):
                    return False

                def read(self_inner):
                    return json.dumps({"choices": [{"message": {"content": "{}"}}]}).encode()

            return _Resp()

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-secret-value-12345"}):
            with patch("gpt_mechanism_judge.openai_client.urllib.request.urlopen", side_effect=_fake_urlopen):
                with patch("gpt_mechanism_judge.openai_client.json.load",
                           return_value={"choices": [{"message": {"content": "{}"}}]}):
                    call_openai("system", "user")

        self.assertEqual(captured["headers"].get("Authorization"), "Bearer sk-secret-value-12345")
        self.assertNotIn(b"sk-secret-value-12345", captured["body"],
                          "the key must never be serialized into the request body")


class NoChoicesTests(unittest.TestCase):
    def test_empty_choices_raises_openai_error(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            with patch("gpt_mechanism_judge.openai_client.urllib.request.urlopen"):
                with patch("gpt_mechanism_judge.openai_client.json.load", return_value={"choices": []}):
                    with self.assertRaises(OpenAIError):
                        call_openai("system", "user")

    def test_empty_content_raises_openai_error(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            with patch("gpt_mechanism_judge.openai_client.urllib.request.urlopen"):
                with patch("gpt_mechanism_judge.openai_client.json.load",
                           return_value={"choices": [{"message": {"content": ""}}]}):
                    with self.assertRaises(OpenAIError):
                        call_openai("system", "user")


class ParseJsonObjectTests(unittest.TestCase):
    def test_plain_json_parses(self):
        self.assertEqual(parse_json_object('{"a": 1}'), {"a": 1})

    def test_fenced_json_parses(self):
        self.assertEqual(parse_json_object('```json\n{"a": 1}\n```'), {"a": 1})

    def test_malformed_json_raises_value_error(self):
        with self.assertRaises(ValueError):
            parse_json_object('{"a": 1')


if __name__ == "__main__":
    unittest.main()
