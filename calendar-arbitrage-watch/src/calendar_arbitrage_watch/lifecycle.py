"""Lifecycle state machine: WATCH -> CHEAP_TEST -> {START_CLOCK_CANDIDATE |
BUY_CALENDAR_CANDIDATE} -> REJECTED (from any state).

Mirrors business_candidate_analyst's lifecycle shape: every transition is
driven by a rubric (here, gate.ReviewDecision) and cites the reason it
fired; a transition with unmet criteria simply does not fire.

HARD BOUNDARY (CONTRACT.md's Human Authority Boundary, verbatim in spirit
from every other package's CONTRACT.md): this module NEVER writes a state
beyond START_CLOCK_CANDIDATE or BUY_CALENDAR_CANDIDATE, because no such
state exists in models.LIFECYCLE_STATES. There is no "APPLIED",
"RESERVED", "PAID", "CONTACTED", or "SIGNED" state to reach - the
boundary is structural, not a runtime check that could be bypassed.
"""

from __future__ import annotations

from typing import Tuple

from .gate import ReviewDecision
from .models import (
    ARCHAEOLOGY,
    BUY_CALENDAR_CANDIDATE,
    CHEAP_TEST,
    CalendarAssessment,
    LIFECYCLE_STATES,
    MAX_AUTOMATIC_STATES,
    REJECTED,
    REVIEW_CHALLENGED,
    REVIEW_CONFIRMED,
    REVIEW_KILLED,
    STATE_RANK as _RANK,
    START_CLOCK_CANDIDATE,
    WATCH,
)


def _ceiling_for_mode(mode: str) -> str:
    return BUY_CALENDAR_CANDIDATE if mode == ARCHAEOLOGY else START_CLOCK_CANDIDATE


def apply_review(assessment: CalendarAssessment, decision: ReviewDecision) -> Tuple[str, str]:
    """Returns (new_state, reason). Pure function - does not mutate
    `assessment`; the caller decides whether/how to persist the result
    (see ledger.py: a state change is a new CalendarAssessment record).

    - REVIEW_KILLED -> REJECTED, always, from any prior state.
    - REVIEW_CHALLENGED -> capped at WATCH (or held at WATCH/CHEAP_TEST if
      already there and not worse), never promoted this round.
    - REVIEW_CONFIRMED -> may advance one step at a time, capped at
      decision.max_allowed_state, itself capped by the mode's ceiling.
      Never skips CHEAP_TEST on the way from WATCH.
    """
    current = assessment.lifecycle_state
    if current not in LIFECYCLE_STATES:
        current = WATCH

    if decision.outcome == REVIEW_KILLED:
        return REJECTED, f"adversarial review KILLED: {'; '.join(decision.reasons)}"

    if decision.outcome == REVIEW_CHALLENGED:
        if current == REJECTED:
            return REJECTED, "candidate previously REJECTED; automatic revival is out of scope"
        capped = min(current, WATCH, key=lambda s: _RANK[s])
        return capped, f"adversarial review CHALLENGED, capped at WATCH: {'; '.join(decision.reasons)}"

    # REVIEW_CONFIRMED
    ceiling = _ceiling_for_mode(assessment.mode)
    allowed = decision.max_allowed_state
    if allowed not in MAX_AUTOMATIC_STATES:
        allowed = WATCH
    # Never exceed the mode's own ceiling regardless of what the gate
    # allowed. START_CLOCK_CANDIDATE and BUY_CALENDAR_CANDIDATE share a
    # STATE_RANK (both are "the MAX_AUTOMATIC tier"), so a rank comparison
    # alone cannot catch "gate allowed the WRONG MAX_AUTOMATIC state for
    # this mode" - compare identity, not just rank.
    if allowed in MAX_AUTOMATIC_STATES and allowed != ceiling:
        allowed = ceiling

    if current == REJECTED:
        # a killed candidate never silently revives; a human must re-open it
        # outside this function (out of scope for the minimal watch).
        return REJECTED, "candidate previously REJECTED; automatic revival is out of scope"

    if _RANK[current] >= _RANK[allowed]:
        # already at or above what this round supports - hold, do not demote
        return current, "adversarial review CONFIRMED; no change - already at or above supported state"

    # advance exactly one rank at a time, never WATCH -> MAX_AUTOMATIC in one jump
    if current == WATCH:
        return CHEAP_TEST, "adversarial review CONFIRMED; advanced WATCH -> CHEAP_TEST"
    if current == CHEAP_TEST:
        return allowed, f"adversarial review CONFIRMED; advanced CHEAP_TEST -> {allowed}"
    return current, "adversarial review CONFIRMED; no defined next step from current state"
