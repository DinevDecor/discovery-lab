"""Read-only loader for Constraint Archaeology's published evidence.

Opens exactly three files, always in read mode, never writes anything.
tests/test_safety.py enforces this module never opens a file in a writing
mode and never imports the ca_agents package - the boundary is a build
failure if violated, not just a docstring.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class CAEvidence:
    observations: List[Dict[str, Any]] = field(default_factory=list)
    anomalies: List[Dict[str, Any]] = field(default_factory=list)
    evaluations: List[Dict[str, Any]] = field(default_factory=list)

    def observations_by_id(self) -> Dict[str, Dict[str, Any]]:
        return {o["observation_id"]: o for o in self.observations}

    def evaluations_by_anomaly_id(self) -> Dict[str, Dict[str, Any]]:
        return {e["anomaly_id"]: e for e in self.evaluations}


def _read_jsonl(path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        return []
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def _read_json_list(path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else []


def load_ca_evidence(ca_data_dir: str) -> CAEvidence:
    """Load exactly the three snapshot/append-only files Constraint
    Archaeology already publishes. No other file under
    constraint-archaeology-agents/ is ever opened by this package."""
    observations = _read_jsonl(os.path.join(ca_data_dir, "observations.jsonl"))
    anomalies = _read_json_list(os.path.join(ca_data_dir, "anomalies.json"))
    evaluations = _read_json_list(os.path.join(ca_data_dir, "latest-evaluations.json"))
    return CAEvidence(observations=observations, anomalies=anomalies, evaluations=evaluations)
