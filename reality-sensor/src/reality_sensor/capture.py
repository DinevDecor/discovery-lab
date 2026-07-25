"""Loads a raw-captures file from local disk. This module never makes
a network call - see ARCHITECTURE.md for why capture and processing
are deliberately separate steps. Malformed entries are skipped with a
logged reason rather than crashing the whole run, matching Observation
Agent's own "a check failing must not crash the whole run" discipline.
"""

from __future__ import annotations

import json
from pathlib import Path

from .models import RawCapture

_REQUIRED_FIELDS = (
    "source_name",
    "source_url",
    "source_trust",
    "category",
    "captured_at",
    "title",
    "raw_text",
    "affected_capability",
)


def load_raw_captures(path: str | Path) -> tuple[list[RawCapture], list[str]]:
    """Returns (captures, skip_reasons). A malformed captures file (not
    valid JSON, not a list) yields ([], [one reason]) rather than
    raising - callers decide whether that's fatal."""
    path = Path(path)
    if not path.is_file():
        return [], [f"raw-captures file not found: {path}"]

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [], [f"raw-captures file is not valid JSON: {exc}"]

    if not isinstance(raw, list):
        return [], ["raw-captures file must be a JSON list of capture objects"]

    captures: list[RawCapture] = []
    skipped: list[str] = []
    for i, entry in enumerate(raw):
        if not isinstance(entry, dict):
            skipped.append(f"entry {i}: not a JSON object, skipped")
            continue
        missing = [f for f in _REQUIRED_FIELDS if f not in entry]
        if missing:
            skipped.append(f"entry {i}: missing required field(s) {missing}, skipped")
            continue
        captures.append(
            RawCapture(
                source_name=entry["source_name"],
                source_url=entry["source_url"],
                source_trust=entry["source_trust"],
                category=entry["category"],
                captured_at=entry["captured_at"],
                title=entry["title"],
                raw_text=entry["raw_text"],
                affected_capability=entry["affected_capability"],
                capability_keywords=entry.get("capability_keywords", []),
                practical_impact_note=entry.get("practical_impact_note", ""),
            )
        )
    return captures, skipped
