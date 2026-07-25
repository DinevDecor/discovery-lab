"""Loads a raw-captures file from local disk. This module never makes
a network call - see ARCHITECTURE.md. Malformed entries are skipped
with a logged reason rather than crashing the whole run.
"""

from __future__ import annotations

import json
from pathlib import Path

from .models import RawPaperCapture

_REQUIRED_FIELDS = (
    "title",
    "authors",
    "publication",
    "date",
    "source_name",
    "source_url",
    "source_trust",
    "evidence_level",
    "domain",
    "raw_abstract",
    "problem_addressed",
    "main_contribution",
)


def load_raw_captures(path: str | Path) -> tuple[list[RawPaperCapture], list[str]]:
    """Returns (captures, skip_reasons)."""
    path = Path(path)
    if not path.is_file():
        return [], [f"raw-captures file not found: {path}"]

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [], [f"raw-captures file is not valid JSON: {exc}"]

    if not isinstance(raw, list):
        return [], ["raw-captures file must be a JSON list of capture objects"]

    captures: list[RawPaperCapture] = []
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
            RawPaperCapture(
                title=entry["title"],
                authors=entry["authors"],
                publication=entry["publication"],
                date=entry["date"],
                source_name=entry["source_name"],
                source_url=entry["source_url"],
                source_trust=entry["source_trust"],
                evidence_level=entry["evidence_level"],
                domain=entry["domain"],
                raw_abstract=entry["raw_abstract"],
                problem_addressed=entry["problem_addressed"],
                main_contribution=entry["main_contribution"],
                idea_keywords=entry.get("idea_keywords", []),
                architectural_relevance_note=entry.get("architectural_relevance_note", ""),
                possible_experiment_notes=entry.get("possible_experiment_notes", []),
            )
        )
    return captures, skipped
