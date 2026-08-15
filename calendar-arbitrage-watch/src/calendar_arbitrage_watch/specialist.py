"""Calendar Arbitrage specialist math - the corrected v0.1.1/v0.1.2
methodology as pure, deterministic functions.

ANALYST BOUNDARY: an LLM MAY be used upstream of this module to help a
human/AI executor read a regulatory filing, permit register, or accreditation
listing and turn prose into the structured inputs this module consumes
(mirrors ca_agents.sensor's use of an LLM for extraction, kept separate from
ca_agents.same_mechanism_gate's own deterministic gate math). This module
itself never calls a model and never touches the network - every function
here is a pure function of its arguments, so two runs over the same input
produce byte-identical output. LLM-generated text is never itself evidence
(CLAUDE.md: "Model-generated content is never evidence") - it can only ever
help a human populate a NumberClaim/DateBound, whose evidence_status a human
or the intake step is responsible for setting honestly.

Every function returns a NumberClaim/OpenFinding rather than a bare number,
so "cannot compute this" is representable as INSUFFICIENT_DATA rather than
0.0 or an exception.
"""

from __future__ import annotations

from datetime import date
from typing import Optional, Tuple

from .models import (
    DateBound,
    DemandProfile,
    NumberClaim,
    OpenFinding,
    ShockForecast,
    INSUFFICIENT_DATA,
    OBSERVED,
    MEASURED,
    REPEATED,
)

SPECIALIST_VERSION = "0.1.2"


def _parse_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _days_between(as_of: str, target: Optional[str]) -> Optional[float]:
    a = _parse_date(as_of)
    t = _parse_date(target)
    if a is None or t is None:
        return None
    return float((t - a).days)


def unfavorable_shock_date(shock: ShockForecast) -> Optional[str]:
    """The EARLIEST plausible shock date is unfavorable for readiness math
    (least preparation time) - never the midpoint, never the latest,
    regardless of shock_type. For DATED, earliest == latest by
    construction (a single known date)."""
    if not shock.date_bound.is_defensible():
        return None
    return shock.date_bound.earliest or shock.date_bound.latest


# ---------------------------------------------------------------------------
# Readiness Gap - methodology delta v0.1.1 #1
# ---------------------------------------------------------------------------

def compute_readiness_gap(as_of: str, shock: ShockForecast, l_remaining: NumberClaim) -> NumberClaim:
    """G_r = T_shock - L_remaining.

    `l_remaining` MUST be an independently asserted remaining-work estimate
    - this function never derives it from elapsed time, and never receives
    elapsed time as an argument at all. That is the structural fix for the
    delta's core complaint: if our position advances at the same pace as
    the calendar, T_shock and L_remaining fall together and G_r is
    unchanged, because this function has no elapsed-time term to
    (mis)apply a double-discount with.
    """
    shock_date = unfavorable_shock_date(shock)
    if shock_date is None or l_remaining.evidence_status == INSUFFICIENT_DATA or l_remaining.value is None:
        return NumberClaim(unit="days", evidence_status=INSUFFICIENT_DATA,
                            note="shock date or l_remaining not available")
    days_to_shock = _days_between(as_of, shock_date)
    if days_to_shock is None:
        return NumberClaim(unit="days", evidence_status=INSUFFICIENT_DATA, note="unparseable date")
    g_r = days_to_shock - l_remaining.value
    provenance = MEASURED if l_remaining.provenance == MEASURED else REPEATED
    return NumberClaim(
        value=g_r, unit="days", provenance=provenance, evidence_status=OBSERVED, as_of=as_of,
        note="G_r = days_to_shock(as_of, unfavorable shock date) - l_remaining "
             "(l_remaining is an independently asserted quantity, never derived from elapsed time here)",
    )


# ---------------------------------------------------------------------------
# Defensive Gap - methodology delta v0.1.1 #2
# ---------------------------------------------------------------------------

def compute_defensive_gap_novo(as_of: str, shock: ShockForecast, l_remaining_denovo: NumberClaim) -> NumberClaim:
    """G_d^novo: could a competitor who starts from zero TODAY still beat
    the shock date? Same formula shape as G_r, but `l_remaining_denovo` is
    a reference build-time estimate for a hypothetical new entrant, not
    our own progress. Correct DATED dynamics (2026-08-15 approval, point
    5): a de-novo entrant's required work does not shrink with calendar
    time (they have not started), so as `as_of` approaches a DATED
    shock_date, days_to_shock shrinks while l_remaining_denovo stays flat
    - G_d^novo decreases monotonically purely from time passing, which is
    the correct and DIFFERENT dynamic from G_r (which can legitimately
    stay flat)."""
    result = compute_readiness_gap(as_of, shock, l_remaining_denovo)
    if result.evidence_status != INSUFFICIENT_DATA:
        result = NumberClaim(
            value=result.value, unit=result.unit, provenance=result.provenance,
            evidence_status=result.evidence_status, as_of=result.as_of,
            note="G_d^novo = days_to_shock(as_of, unfavorable shock date) - l_remaining_denovo "
                 "(hypothetical fresh entrant starting today)",
        )
    return result


def compute_defensive_gap_active(
    as_of: str,
    shock: ShockForecast,
    competitor_start_bound: DateBound,
    competitor_l_remaining: NumberClaim,
    our_l_remaining: NumberClaim,
) -> Tuple[NumberClaim, str]:
    """G_d^active: relative lead/lag versus a SPECIFIC competitor whose
    clock is already running. Uses the bound of `competitor_start_bound`
    that is UNFAVORABLE to us (2026-08-15 approval, point 8): if the
    competitor may have started earlier than directly observed, assume
    the EARLIEST plausible start (most work already banked by them) -
    never a fabricated midpoint. If no defensible bound exists, returns
    INSUFFICIENT_DATA and an empty bound_used - this function never
    guesses a competitor start date.

    Returns (g_d_active_days, bound_used) where a positive value means we
    finish before the competitor (lead), negative means they finish first
    (lag). competitor_finish = competitor_start(unfavorable) +
    competitor_l_remaining; our_finish = as_of + our_l_remaining;
    g_d_active = competitor_finish - our_finish.
    """
    if not competitor_start_bound.is_defensible():
        return (NumberClaim(unit="days", evidence_status=INSUFFICIENT_DATA,
                             note="no defensible competitor start bound"), "")
    if competitor_l_remaining.value is None or our_l_remaining.value is None:
        return (NumberClaim(unit="days", evidence_status=INSUFFICIENT_DATA,
                             note="competitor or our own l_remaining not available"), "")

    bound_used = "earliest" if competitor_start_bound.earliest else "latest"
    competitor_start = competitor_start_bound.earliest or competitor_start_bound.latest
    start_date = _parse_date(competitor_start)
    as_of_date = _parse_date(as_of)
    if start_date is None or as_of_date is None:
        return (NumberClaim(unit="days", evidence_status=INSUFFICIENT_DATA, note="unparseable date"), "")

    days_competitor_running = float((as_of_date - start_date).days)
    competitor_days_remaining = competitor_l_remaining.value - days_competitor_running
    g_d_active = competitor_days_remaining - our_l_remaining.value

    provenance = MEASURED if (competitor_l_remaining.provenance == MEASURED
                               and our_l_remaining.provenance == MEASURED) else REPEATED
    claim = NumberClaim(
        value=g_d_active, unit="days", provenance=provenance, evidence_status=OBSERVED, as_of=as_of,
        note=f"G_d^active = (competitor_l_remaining - days_running_since_{bound_used}_bound) - our_l_remaining; "
             "positive = we finish first",
    )
    return claim, bound_used


# ---------------------------------------------------------------------------
# Delay handling - methodology delta v0.1.1 #4
# ---------------------------------------------------------------------------

def recompute_after_delay(
    as_of: str,
    new_shock: ShockForecast,
    l_remaining: NumberClaim,
    l_remaining_denovo: NumberClaim,
    competitor_start_bound: DateBound,
    competitor_l_remaining: NumberClaim,
    our_l_remaining_for_active: NumberClaim,
) -> dict:
    """A delay event NEVER triggers an automatic lifecycle DEGRADE by
    itself (methodology delta v0.1.1 #4 - that rule is removed, not
    reinterpreted). Instead this recomputes exactly the four quantities
    the delta names, every time, and returns them together with a
    directional note - lifecycle.py / gate.py decide what (if anything)
    that means for the candidate's state, as a separate, explicit step.

    Returns a dict with keys: g_r, g_d_novo, g_d_active, g_d_active_bound,
    supply_response_note. `new_shock` must be a freshly issued
    ShockForecast (new forecast_version / new ledger line), never an
    edited one - see ledger.py.
    """
    g_r = compute_readiness_gap(as_of, new_shock, l_remaining)
    g_d_novo = compute_defensive_gap_novo(as_of, new_shock, l_remaining_denovo)
    g_d_active, bound_used = compute_defensive_gap_active(
        as_of, new_shock, competitor_start_bound, competitor_l_remaining, our_l_remaining_for_active)

    note_parts = []
    if g_d_novo.evidence_status != INSUFFICIENT_DATA:
        note_parts.append(
            "delay gives new entrants more runway" if (g_d_novo.value or 0) > 0
            else "delay does not rescue new entrants")
    if g_d_active.evidence_status != INSUFFICIENT_DATA:
        note_parts.append(
            "delay helps the tracked active competitor relative to us" if (g_d_active.value or 0) < 0
            else "delay does not help the tracked active competitor relative to us")
    supply_response_note = (
        "; ".join(note_parts) if note_parts
        else "insufficient data to characterize competitive supply response to this delay"
    )
    return {
        "g_r": g_r,
        "g_d_novo": g_d_novo,
        "g_d_active": g_d_active,
        "g_d_active_bound": bound_used,
        "supply_response_note": supply_response_note,
    }


# ---------------------------------------------------------------------------
# Demand Stability Index (DSI) - heuristic, NOT Bayesian (2026-08-15 approval, point 5)
# ---------------------------------------------------------------------------

def compute_demand_stability_index(demand: DemandProfile) -> str:
    """DSI is a rule-based tier lookup over
    (demand_obligation_certainty, shock_date_stability), deliberately NOT
    a Bayesian posterior - no prior is assumed, no likelihood is
    multiplied, nothing here updates a probability. This is a documented,
    reviewable threshold table, not a statistical estimator, per the
    explicit instruction that DSI must be a heuristic."""
    doc = demand.demand_obligation_certainty
    sds = demand.shock_date_stability
    if doc.evidence_status == INSUFFICIENT_DATA or sds.evidence_status == INSUFFICIENT_DATA:
        return INSUFFICIENT_DATA
    if doc.value is None or sds.value is None:
        return INSUFFICIENT_DATA
    lo = min(doc.value, sds.value)
    if lo >= 0.7:
        return "HIGH"
    if lo >= 0.4:
        return "MEDIUM"
    return "LOW"


# ---------------------------------------------------------------------------
# S_ready and Readiness Index (RI) - composite scores
# ---------------------------------------------------------------------------

def compute_s_ready(g_r: NumberClaim, shock_horizon_days: Optional[float]) -> NumberClaim:
    """S_ready normalizes G_r onto the SAME 0..1 unit convention this
    package uses for every demand field, so RI (below) can combine them
    honestly instead of mixing a day-count with a probability-like scale.

    S_ready = clamp(G_r / shock_horizon_days, 0, 1). `shock_horizon_days`
    must be supplied by the caller (typically days between first_seen and
    the shock date) - this function does not compute it, so a missing
    horizon is INSUFFICIENT_DATA rather than a silent divide-by-zero.

    ASSUMPTION, not a certified formula: this normalization was not
    specified with an exact equation in the approved methodology; it is a
    documented working definition for review, chosen only because it
    satisfies "same unit as demand" and is fully transparent."""
    if g_r.evidence_status == INSUFFICIENT_DATA or g_r.value is None:
        return NumberClaim(unit="ratio", evidence_status=INSUFFICIENT_DATA, note="G_r not available")
    if not shock_horizon_days or shock_horizon_days <= 0:
        return NumberClaim(unit="ratio", evidence_status=INSUFFICIENT_DATA, note="no defensible shock horizon")
    ratio = max(0.0, min(1.0, g_r.value / shock_horizon_days))
    return NumberClaim(
        value=ratio, unit="ratio", provenance=g_r.provenance, evidence_status=OBSERVED, as_of=g_r.as_of,
        note="S_ready = clamp(G_r / shock_horizon_days, 0, 1) - ASSUMPTION, pending review, see specialist.py docstring",
    )


def compute_readiness_index(s_ready: NumberClaim, demand: DemandProfile) -> NumberClaim:
    """RI: a composite of readiness and demand certainty, so a
    high-S_ready candidate whose underlying demand is itself uncertain
    does not rank the same as one with certain demand.

    RI = S_ready * demand_obligation_certainty.

    ASSUMPTION, not a certified formula: no exact composition rule was
    specified in the approved methodology beyond naming RI alongside
    G_r/G_d/lockout/S_ready as quantities that must be deterministic. This
    is a documented, simple, transparent working definition pending
    review - not adopted as calibrated scoring."""
    doc = demand.demand_obligation_certainty
    if s_ready.evidence_status == INSUFFICIENT_DATA or s_ready.value is None:
        return NumberClaim(unit="ratio", evidence_status=INSUFFICIENT_DATA, note="S_ready not available")
    if doc.evidence_status == INSUFFICIENT_DATA or doc.value is None:
        return NumberClaim(unit="ratio", evidence_status=INSUFFICIENT_DATA,
                            note="demand_obligation_certainty not available")
    return NumberClaim(
        value=s_ready.value * doc.value, unit="ratio", provenance=REPEATED, evidence_status=OBSERVED,
        as_of=s_ready.as_of,
        note="RI = S_ready * demand_obligation_certainty - ASSUMPTION, pending review, see specialist.py docstring",
    )


# ---------------------------------------------------------------------------
# OPEN FINDINGS - computed where possible, NEVER read by scoring
# ---------------------------------------------------------------------------

def open_finding_pending_competition_threshold(pending_competition) -> OpenFinding:
    """The candidate rule 'C3 >= DC x 0.25' from the pre-existing research
    baseline. C3 and DC are quantities defined in the Calendar Arbitrage
    research documents (Calendar Moat Analysis / Screener v0.1); those
    documents could not be located in this repository or in
    DinevDecor/project-memory/archive as of this implementation (see
    methodology assumptions in the delta doc and the final implementation
    report). Without their definitions this rule cannot be evaluated
    numerically without guessing - so it is recorded as a named,
    permanently open, NON-scoring placeholder rather than silently
    approximated. affects_scoring is hard-coded False; nothing in gate.py
    or lifecycle.py reads this finding's `value`."""
    return OpenFinding(
        finding_id="c3_ge_dc_times_0_25",
        description="C3 >= DC x 0.25 (pending-competition threshold candidate from the prior research baseline)",
        status="OPEN_FINDING",
        affects_scoring=False,
        value=None,
        note="C3/DC not defined in any artifact reachable from this session; recorded by name only, "
             "uncalibrated, not evaluated numerically. See docs/method/calendar-arbitrage-screener-v0.1.1-delta.md.",
    )


def open_finding_startability_gap(shock: ShockForecast, l_remaining_denovo: NumberClaim,
                                   clock_open_date: DateBound) -> OpenFinding:
    """startability_gap = t_lockout_novo - clock_open_date.

    t_lockout_novo is the date beyond which a de-novo entrant can no
    longer mathematically finish before the shock: t_lockout_novo =
    shock_date(unfavorable) - l_remaining_denovo. A NEGATIVE
    startability_gap means the procedure/queue/registration only became
    accessible AFTER de-novo supply was already mathematically too late
    to matter - exactly the regime this finding exists to catch. Computed
    when the inputs allow it, but affects_scoring is hard-coded False
    per the 2026-08-15 approval, point 7 - this is diagnostic only until
    reviewed."""
    shock_date = unfavorable_shock_date(shock)
    if (shock_date is None or l_remaining_denovo.value is None
            or l_remaining_denovo.evidence_status == INSUFFICIENT_DATA
            or not clock_open_date.is_defensible()):
        return OpenFinding(
            finding_id="startability_gap",
            description="startability_gap = t_lockout_novo - clock_open_date",
            status="OPEN_FINDING", affects_scoring=False, value=None,
            note="insufficient data to compute (shock date, l_remaining_denovo, or clock_open_date missing)",
        )
    shock_dt = _parse_date(shock_date)
    lockout_dt = None
    if shock_dt is not None:
        from datetime import timedelta
        lockout_dt = shock_dt - timedelta(days=l_remaining_denovo.value)
    open_dt = _parse_date(clock_open_date.earliest or clock_open_date.latest)
    if lockout_dt is None or open_dt is None:
        return OpenFinding(
            finding_id="startability_gap",
            description="startability_gap = t_lockout_novo - clock_open_date",
            status="OPEN_FINDING", affects_scoring=False, value=None,
            note="unparseable date",
        )
    gap_days = float((lockout_dt - open_dt).days)
    note = ("NEGATIVE: de-novo supply was already mathematically late the moment this procedure became "
            "accessible" if gap_days < 0 else
            "non-negative: de-novo supply had a mathematically available window at open")
    return OpenFinding(
        finding_id="startability_gap",
        description="startability_gap = t_lockout_novo - clock_open_date",
        status="OPEN_FINDING", affects_scoring=False, value=gap_days,
        note=f"t_lockout_novo={lockout_dt.isoformat()}, clock_open_date={open_dt.isoformat()}; {note}",
    )
