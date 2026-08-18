"""Raw OpenAI transport. Mirrors `ca_agents.llm.call_claude` /
`parse_json_object` field-for-field and call-for-call - same stdlib-only
`urllib.request` transport, same "raise loudly on missing key/transport
failure, let the caller decide how to handle a malformed body" split -
re-implemented here rather than imported, for the same "read data, never
import another package's code" reason `case-claim-kernel` already holds
itself to (see its `models.py` docstring). This module has no dependency
on `ca_agents` at all; it is usable standalone.

CREDENTIAL DISCIPLINE
    `OPENAI_API_KEY` is read from the environment on every call, never
    cached at import time, never written to a log line, an exception
    message, or any persisted artifact. The only place the key touches
    memory is the `Authorization` header of the one outbound request.

API SHAPE
    Chat Completions (`POST /v1/chat/completions`), not the newer
    Responses API - both are current, official OpenAI surfaces as of this
    writing; Chat Completions is used here because it is the smaller,
    more stable shape for a single system+user exchange with a JSON
    response, which is all this adapter needs. `response_format:
    {"type": "json_object"}` is a real, current Chat Completions field
    that constrains the model to emit a syntactically valid JSON object -
    used here to reduce (not eliminate - the fields inside can still be
    wrong) the malformed-output rate the Claude side has already had to
    build a fallback for (see judge.py and
    ca_agents/mechanism_judge.py's own docstring about exactly this
    failure mode).

MODEL NAME
    Defaults to `gpt-4.1`, overridable via `OPENAI_MODEL`. `gpt-4.1` is a
    real, generally-available OpenAI model at the time this module was
    written, chosen for structured-output reliability at a moderate cost
    - not the newest or cheapest OpenAI model on every possible date this
    code runs. Whoever runs this against a real key should confirm
    `OPENAI_MODEL` still names a model OpenAI supports before relying on
    the default - the task instructions explicitly forbid guessing a
    model name blindly, so the default is named and documented here
    instead of hidden.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

OPENAI_CHAT_COMPLETIONS_URL = "https://api.openai.com/v1/chat/completions"
DEFAULT_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4.1")


class OpenAIError(RuntimeError):
    pass


def call_openai(system: str, user: str, max_tokens: int = 900) -> str:
    """POSTs one system+user exchange to OpenAI Chat Completions and
    returns the assistant's text content. Raises OpenAIError (never
    silently returns an empty/placeholder string) on a missing key, a
    transport failure, or a response with no text - a transport problem
    is not the same thing as "the model returned unparseable JSON", and
    callers (judge.py) are expected to handle the two differently, the
    same way ca_agents.mechanism_judge already does for LLMError vs a
    JSON parse failure.
    """
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise OpenAIError("OPENAI_API_KEY is not set")

    payload = json.dumps({
        "model": DEFAULT_MODEL,
        "max_tokens": max_tokens,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }).encode("utf-8")

    req = urllib.request.Request(
        OPENAI_CHAT_COMPLETIONS_URL,
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "User-Agent": "gpt-mechanism-judge/0.1",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as exc:
        # exc.reason/exc.code only - never echo request headers or body,
        # which is where the key would otherwise leak into an error string.
        raise OpenAIError(f"OpenAI request failed: HTTP {exc.code} {exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise OpenAIError(f"OpenAI request failed: {exc.reason}") from exc

    choices = data.get("choices", [])
    if not choices:
        raise OpenAIError("OpenAI returned no choices")
    text = (choices[0].get("message") or {}).get("content", "")
    if not text:
        raise OpenAIError("OpenAI returned no text content")
    return text


def parse_json_object(text: str):
    """Identical stripping/parsing behaviour to
    ca_agents.llm.parse_json_object - kept as a literal duplicate rather
    than an import, per this module's own docstring."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(text)
