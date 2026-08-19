"""Read-only helpers for the Mobile Console Bulgarian display cache.

The cache is derived UI data only. Canonical ledgers remain authoritative.
A translation is usable only when its key and declared source hash both
match the current source text exactly; changing source text therefore
invalidates the old translation automatically.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict


def source_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def valid_entries(cache: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    out: Dict[str, Dict[str, str]] = {}
    for key, entry in cache.get("entries", {}).items():
        if not isinstance(entry, dict):
            continue
        source = entry.get("source")
        bg = entry.get("bg")
        declared = entry.get("source_sha256")
        if not isinstance(source, str) or not isinstance(bg, str) or not bg.strip():
            continue
        digest = source_hash(source)
        if key != digest or declared != digest:
            continue
        out[key] = {"source": source, "bg": bg, "source_sha256": digest}
    return out


def load_cache(path: str | Path) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return {"version": 1, "language": "bg", "entries": {}}
    with p.open(encoding="utf-8") as f:
        raw = json.load(f)
    return {
        "version": 1,
        "language": "bg",
        "generated_at": raw.get("generated_at"),
        "entries": valid_entries(raw),
    }


def source_to_bg(cache: Dict[str, Any]) -> Dict[str, str]:
    return {entry["source"]: entry["bg"] for entry in valid_entries(cache).values()}
