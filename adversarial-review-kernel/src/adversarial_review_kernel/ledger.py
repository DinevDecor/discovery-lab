"""Append-only writers for `adversarial-review-kernel/data/
falsifications.jsonl` and `.../judgments.jsonl`. Same idempotent-append,
only-write-path-is-append-mode discipline as
`blind_analysis_kernel.ledger.AnalysisLedger` / `.manifest
.RunManifestLedger` - reimplemented per artifact type rather than a
shared base class, matching this whole family's established convention
(small, independently-readable duplication over a premature abstraction).
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List

from .models import FalsificationArtifact, JudgmentArtifact
from .validator import validate_falsification_artifact, validate_judgment_artifact


class FalsificationLedger:
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

    def append(self, artifact: FalsificationArtifact) -> bool:
        validate_falsification_artifact(artifact)
        if artifact.artifact_id in self._known:
            return False
        os.makedirs(os.path.dirname(os.path.abspath(self.path)) or ".", exist_ok=True)
        line = json.dumps(artifact.to_dict(), sort_keys=True, ensure_ascii=False, default=str)
        with open(self.path, "a", encoding="utf-8") as fh:  # append mode only
            fh.write(line + "\n")
        self._known.add(artifact.artifact_id)
        self._entries.append(artifact.to_dict())
        return True


class JudgmentLedger:
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
                jid = row.get("judgment_id")
                if isinstance(jid, str):
                    self._known.add(jid)

    def has(self, judgment_id: str) -> bool:
        return judgment_id in self._known

    @property
    def known_count(self) -> int:
        return len(self._known)

    def all_entries(self) -> List[Dict[str, Any]]:
        return list(self._entries)

    def append(self, artifact: JudgmentArtifact) -> bool:
        validate_judgment_artifact(artifact)
        if artifact.judgment_id in self._known:
            return False
        os.makedirs(os.path.dirname(os.path.abspath(self.path)) or ".", exist_ok=True)
        line = json.dumps(artifact.to_dict(), sort_keys=True, ensure_ascii=False, default=str)
        with open(self.path, "a", encoding="utf-8") as fh:  # append mode only
            fh.write(line + "\n")
        self._known.add(artifact.judgment_id)
        self._entries.append(artifact.to_dict())
        return True
