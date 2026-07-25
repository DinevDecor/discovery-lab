"""Experiment Extraction (EXEC-010), verbatim: "For every high-value
paper identify: at least one possible experiment; expected benefit;
uncertainty; prerequisites; validation idea. Do not generate
implementation plans. Generate only research opportunities."

This module only ever assembles PossibleExperiment records from
capture-time notes (research judgment, made once, by whoever performs
capture - see ARCHITECTURE.md's capture/process split) into the
structurally-required shape. It has no capability to add a task list,
a file path, a code snippet, or any other implementation-plan-shaped
content - the PossibleExperiment dataclass itself has no field for
one (see models.py).
"""

from __future__ import annotations

from .models import PossibleExperiment, RawPaperCapture

_REQUIRED_KEYS = ("description", "expected_benefit", "uncertainty", "prerequisites", "validation_idea")


def build_experiments(captures: list[RawPaperCapture]) -> list[PossibleExperiment]:
    """Collects every well-formed possible_experiment note across a
    cluster's captures. A note missing a required key is dropped
    (skipped, not fatal) rather than silently filled with an invented
    value - "do not generate implementation plans" also means "do not
    invent experiment content the capture step didn't actually supply."
    """
    experiments: list[PossibleExperiment] = []
    for c in captures:
        for note in c.possible_experiment_notes:
            if not all(k in note and note[k] for k in _REQUIRED_KEYS):
                continue
            experiments.append(
                PossibleExperiment(
                    description=note["description"],
                    expected_benefit=note["expected_benefit"],
                    uncertainty=note["uncertainty"],
                    prerequisites=note["prerequisites"],
                    validation_idea=note["validation_idea"],
                )
            )
    return experiments


def is_high_value(affected_projects: list[str], confidence: str) -> bool:
    """EXEC-010: experiments are required "for every high-value
    paper." A paper is high-value here if it named a real project (not
    WATCH) - a signal with no named project has, by definition, not yet
    answered "why should Discovery Lab care?" and therefore cannot yet
    be high-value regardless of confidence."""
    from .models import Confidence, Project

    if affected_projects == [Project.WATCH]:
        return False
    return confidence in (Confidence.HIGH, Confidence.MEDIUM)
