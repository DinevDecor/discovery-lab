"""History Manager (EXEC-004 §12). Compares this execution's headline
numbers against the immediately previous one, stored in this tool's
own `reports/history.json`. First run always reports "N/A" rather than
fabricating a trend from nothing."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class RunSnapshot:
    timestamp: str
    overall_health_pct: float | None
    recommendation_backlog: int
    decision_backlog: int
    project_health_scores: dict[str, float]
    top_recommendation_hq_id: str | None


def load_history(path: Path) -> list[RunSnapshot]:
    if not path.is_file():
        return []
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    return [RunSnapshot(**r) for r in raw]


def save_history(path: Path, history: list[RunSnapshot], keep_last: int = 90) -> None:
    trimmed = history[-keep_last:]
    path.write_text(
        json.dumps([asdict(r) for r in trimmed], indent=2),
        encoding="utf-8",
    )


def previous_scores(history: list[RunSnapshot]) -> dict[str, float]:
    if not history:
        return {}
    return history[-1].project_health_scores


def trend_line(current: float | None, previous: float | None, label: str) -> str:
    if previous is None:
        return f"{label}: N/A (first execution, no prior snapshot)"
    if current is None:
        return f"{label}: INSUFFICIENT_EVIDENCE this run"
    delta = current - previous
    if abs(delta) < 1:
        direction = "stable"
    elif delta > 0:
        direction = "improvement"
    else:
        direction = "regression"
    sign = "+" if delta >= 0 else ""
    return f"{label}: {direction} ({sign}{delta:.1f} pts vs previous execution)"
