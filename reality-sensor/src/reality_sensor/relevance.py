"""Relevance Gate (EXEC-008): "Which Discovery Lab project could
realistically benefit?" A signal matching no configured project is
reported as WATCH - never forced onto a project it doesn't plausibly
serve, per EXEC-008's own explicit "Do not force relevance" instruction.
"""

from __future__ import annotations

from .config import RelevanceGateConfig
from .models import Project


def gate(text: str, config: RelevanceGateConfig) -> list[str]:
    """Returns the list of matching projects, or [Project.WATCH] if none
    match. `text` should already combine everything a human would judge
    relevance from - affected_capability + summary + practical_impact."""
    lowered = text.lower()
    matches = [
        rule.project
        for rule in config.rules
        if any(keyword in lowered for keyword in rule.keywords)
    ]
    return matches if matches else [Project.WATCH]
