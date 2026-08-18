"""Append-only writer for `blind-analysis-kernel/data/analyses.jsonl`.

Mirrors `case_claim_kernel.ledger.ArtifactLedger` exactly (same
known-ids-loaded-once, idempotent-append, only-write-path-is-append-mode
discipline) - reimplemented, not imported, same reason as every other
module in this family.

Task §9: "Do not overwrite prior analysis artifacts... A rerun is a new
run_id and new analysis artifacts... Do not dedupe two different provider
analyses into one artifact." A different run_id (identity.py) or a
different provider always produces a different `artifact_id`, so this
ledger never needs to choose between two analyses for the same key - each
one gets its own line, permanently.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List

from .models import IndependentAnalysisArtifact
from .validator import validate


class AnalysisLedger:
    def __init__(self, path: str):
        self.path = path
        self._known: set = set()
        self._entries: List[Dict[str, Any]] = []
        self._load_known()

    def _load_known(self) -> None:
        if not os.path.exists(self.path):
            return
        with open(self.path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                self._entries.append(row)
                aid = row.get("artifact_id")
                if isinstance(aid, str):
                    self._known.add(aid)

    def has(self, artifact_id: str) -> bool:
        return artifact_id in self._known

    @property
    def known_count(self) -> int:
        return len(self._known)

    def all_entries(self) -> List[Dict[str, Any]]:
        return list(self._entries)

    def append(self, artifact: IndependentAnalysisArtifact) -> bool:
        """Validates, then appends one artifact. Returns True if written,
        False if this artifact_id was already present (idempotent
        re-append - the retry case identity.py's docstring describes)."""
        validate(artifact)
        if artifact.artifact_id in self._known:
            return False
        os.makedirs(os.path.dirname(os.path.abspath(self.path)) or ".", exist_ok=True)
        line = json.dumps(artifact.to_dict(), sort_keys=True, ensure_ascii=False, default=str)
        with open(self.path, "a", encoding="utf-8") as fh:  # append mode only
            fh.write(line + "\n")
        self._known.add(artifact.artifact_id)
        self._entries.append(artifact.to_dict())
        return True
