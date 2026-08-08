from __future__ import annotations
import json, os, urllib.request

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
DEFAULT_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5")

class LLMError(RuntimeError):
    pass

def call_claude(system: str, user: str, max_tokens: int = 1800) -> str:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise LLMError("ANTHROPIC_API_KEY is not set")
    payload = json.dumps({
        "model": DEFAULT_MODEL,
        "max_tokens": max_tokens,
        "system": system,
        "messages": [{"role":"user","content":user}],
    }).encode("utf-8")
    req = urllib.request.Request(ANTHROPIC_URL, data=payload, method="POST", headers={
        "x-api-key": key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
        "user-agent": "constraint-archaeology-agents/0.1",
    })
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.load(resp)
    parts = data.get("content", [])
    text = "".join(p.get("text", "") for p in parts if p.get("type") == "text")
    if not text:
        raise LLMError("Claude returned no text")
    return text

def parse_json_object(text: str):
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n",1)[1].rsplit("```",1)[0]
    return json.loads(text)
