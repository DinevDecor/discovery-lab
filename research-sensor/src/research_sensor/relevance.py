"""Relation to Existing Projects (EXEC-010): "Every accepted signal
must map to one or more: KOD, Generative Discovery Engine, Trust
Engine, Discovery Lab, Dinev Assistant. Otherwise: WATCH." Independently
reimplemented pattern - same idiom as
reality-sensor/src/reality_sensor/relevance.py, not shared code.
"""

from __future__ import annotations

from .config import RelevanceGateConfig
from .models import Project


def gate(text: str, config: RelevanceGateConfig) -> list[str]:
    """Returns the list of matching projects, or [Project.WATCH] if
    none match - EXEC-010's Most Important Rule made structural: a
    signal that cannot answer "why should Discovery Lab care?" in a
    way that names a project is never forced onto one."""
    lowered = text.lower()
    matches = [
        rule.project
        for rule in config.rules
        if any(keyword in lowered for keyword in rule.keywords)
    ]
    return matches if matches else [Project.WATCH]
