"""Tier 2 dedupe: existing-source duplication - is the same underlying
event/problem already present in Discovery Lab from a different
source/URL. Read-only, plain-file loading of already-published JSONL
rows; never imports ca_agents or business_candidate_analyst (enforced
by tests/test_safety.py) and never writes to, or otherwise touches, any
Constraint Archaeology file.

This is a probe-only lexical heuristic, not the same-mechanism gate
(`ca_agents.same_mechanism_gate`): it never merges anomalies, never
invokes a judge, and its output (a possible matched observation_id) is
only ever used to classify a probe observation as
"existing_source_duplicate" - it has no write path back into CA's own
data.
"""

from __future__ import annotations

import json
import os
import re

_TOKEN = re.compile(r"[a-z0-9]{4,}")


def _tokens(s: str) -> set[str]:
    return set(_TOKEN.findall((s or "").lower()))


def load_existing_pain_texts(paths: list[str]) -> list[tuple[str, str]]:
    """Read-only load of (observation_id, pain_text) pairs from other
    packages' already-published observations.jsonl files. A missing
    path is skipped, not an error - the probe must still run (and
    honestly report a weaker existing-source check) if a sibling
    package's data file does not exist yet."""
    out: list[tuple[str, str]] = []
    for path in paths:
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                oid = row.get("observation_id", "")
                text = " ".join(str(row.get(k, "")) for k in ("process", "pain", "failure_mode"))
                if oid and text.strip():
                    out.append((oid, text))
    return out


def find_existing_match(candidate_text: str, existing: list[tuple[str, str]], threshold: float = 0.3) -> str:
    """Returns the observation_id of the best existing match at or above
    `threshold` token-Jaccard similarity, or "" if none clears it.
    Deliberately a high-recall-for-duplication (not high-precision)
    threshold-style check: this tier's false-positive cost (wrongly
    calling a genuinely new signal "already represented") is treated as
    less damaging than counting a reworded duplicate as independent
    evidence, matching CLAUDE.md's "different text is not independent
    evidence" rule."""
    cand = _tokens(candidate_text)
    if not cand:
        return ""
    best_id, best_score = "", 0.0
    for oid, text in existing:
        toks = _tokens(text)
        if not toks:
            continue
        score = len(cand & toks) / len(cand | toks)
        if score > best_score:
            best_id, best_score = oid, score
    return best_id if best_score >= threshold else ""
