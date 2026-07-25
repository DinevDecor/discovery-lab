"""Load config/source-registry.json and config/relevance-gate.json.

JSON, not YAML — same reasoning as observation-agent's and
headquarters' own config.py: no third-party dependency for what the
stdlib already does. Per EXEC-008's own "fixed source list," neither
file is ever discovered or expanded dynamically at run time; adding a
source or a relevance keyword is a config edit, never a code change.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SourceEntry:
    name: str
    url: str
    trust_level: str
    category: str
    domain: str  # A/B/C/D label, for human readability only


@dataclass
class SourceRegistry:
    sources: list[SourceEntry]
    search_budget: int  # fixed cap on number of fetch/search operations per capture pass

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
            trust_level=s["trust_level"],
            category=s["category"],
            domain=s.get("domain", ""),
        )
        for s in raw["sources"]
    ]
    return SourceRegistry(sources=sources, search_budget=raw.get("search_budget", 40))


def load_relevance_gate(path: str | Path) -> RelevanceGateConfig:
    path = Path(path)
    raw = json.loads(path.read_text(encoding="utf-8"))
    rules = [
        RelevanceRule(project=r["project"], keywords=[k.lower() for k in r["keywords"]])
        for r in raw["rules"]
    ]
    return RelevanceGateConfig(rules=rules)
