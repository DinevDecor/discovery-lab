from __future__ import annotations
from dataclasses import dataclass, asdict, field
from typing import List

@dataclass
class Capture:
    source: str
    url: str
    title: str
    text: str
    published_at: str
    captured_at: str

@dataclass
class Observation:
    observation_id: str
    source: str
    url: str
    published_at: str
    process: str
    hidden_function_hint: str
    current_carrier: str
    pain: str
    failure_mode: str
    evidence_quote: str
    confidence: float
    fingerprint: str

@dataclass
class Anomaly:
    anomaly_id: str
    canonical_pattern: str
    hidden_function_class: str
    observation_ids: List[str] = field(default_factory=list)
    independent_sources: List[str] = field(default_factory=list)
    first_seen: str = ""
    last_seen: str = ""
    status: str = "WATCH"

@dataclass
class Evaluation:
    anomaly_id: str
    mechanism_verdict: str
    capture_verdict: str
    k1: str
    k2: str
    k3: str
    k4: str
    k5: str
    k6: str
    rationale: str
    evidence_used: List[str]
    action: str

def to_dict(obj):
    return asdict(obj)
