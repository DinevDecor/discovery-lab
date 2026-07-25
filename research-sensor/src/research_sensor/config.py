"""Load config/source-registry.json and config/relevance-gate.json.

Independently reimplemented pattern (per EXEC-009's "shared pattern,
not shared module" ruling) - same idiom as observation-agent's,
headquarters', and reality-sensor's own config.py: @dataclass +
json.loads, no third-party dependency, no dynamic discovery, "add a
source by editing this file."
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SourceEntry:
    name: str
    url: str
    source_trust: str  # SourceTrust
    domain_hint: str    # A-E label, human-readable only


@dataclass
class SourceRegistry:
    sources: list[SourceEntry]
    processing_budget: int  # fixed cap on fetch/search operations per capture pass
    window_days: int         # fixed validation window (30, per EXEC-010)

    def by_name(self, name: str) -> SourceEntry | None:
        for s in self.sources:
            if s.name == name:
                return s
        return None


@dataclass
class RelevanceRule:
    project: str
    keywords: list[str]


@dataclass
class RelevanceGateConfig:
    rules: list[RelevanceRule]


def load_source_registry(path: str | Path) -> SourceRegistry:
    path = Path(path)
    raw = json.loads(path.read_text(encoding="utf-8"))
    sources = [
        SourceEntry(
            name=s["name"],
            url=s["url"],
            source_trust=s["source_trust"],
            domain_hint=s.get("domain_hint", ""),
        )
        for s in raw["sources"]
    ]
    return SourceRegistry(
        sources=sources,
        processing_budget=raw.get("processing_budget", 30),
        window_days=raw.get("window_days", 30),
    )


def load_relevance_gate(path: str | Path) -> RelevanceGateConfig:
    path = Path(path)
    raw = json.loads(path.read_text(encoding="utf-8"))
    rules = [
        RelevanceRule(project=r["project"], keywords=[k.lower() for k in r["keywords"]])
        for r in raw["rules"]
    ]
    return RelevanceGateConfig(rules=rules)
