"""Calendar Arbitrage specialist math - the corrected v0.1.1/v0.1.2
methodology as pure, deterministic functions.

CORRECTION (2026-08-15-2): a semantic regression was found between the
approved v0.1.2 methodology and this module's first implementation.
G_d^novo had an inverted sign and reused compute_readiness_gap's formula
(wrong - G_r and G_d^novo have different signs and different semantics);
S_ready was redefined as a normalized 0..1 readiness score for OUR OWN
candidate (wrong - S_ready is a competitor-supply aggregate); RI was
"Readiness Index" (wrong - RI is the Rivalry Index, D_shock / (S_existing
+ S_ready)); and G_d^active subtracted elapsed competitor time from a
quantity that could already BE an "as of" remaining estimate, risking a
double subtraction. All four are fixed below. See
docs/method/calendar-arbitrage-screener-v0.1.1-delta.md's "Correction —
2026-08-15" section for the full old-formula -> new-formula record.

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

from datetime import date, timedelta
from typing import List, Optional, Sequence

from .models import (
    CompetitorFinish,
    DateBound,
    DemandProfile,
    NumberClaim,
    OpenFinding,
    ShockForecast,
    INSUFFICIENT_DATA,
    NOT_IMPLEMENTED,
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
    """G_r = T_shock - L_remaining (days-until-shock minus our own
    remaining work). POSITIVE means we have slack before the shock.

    `l_remaining` MUST be an independently asserted remaining-work estimate
    - this function never derives it from elapsed time, and never receives
    elapsed time as an argument at all. That is the structural fix for the
    delta's core complaint: if our position advances at the same pace as
    the calendar, T_shock and L_remaining fall together and G_r is
    unchanged, because this function has no elapsed-time term to
    (mis)apply a double-discount with.

    NOT reused by compute_defensive_gap_novo (2026-08-15-2 correction) -
    G_r and G_d^novo have opposite sign conventions and different
    semantics (our own slack vs. a hypothetical competitor's shortfall);
    sharing the formula was the original bug.
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
# Defensive Gap - methodology delta v0.1.1 #2, corrected 2026-08-15-2
# ---------------------------------------------------------------------------

def compute_defensive_gap_novo(as_of: str, shock: ShockForecast, l_irr_denovo: NumberClaim) -> NumberClaim:
    """G_d^novo = L_irr - T_shock (canonical formula, 2026-08-15-2
    correction - previously this module computed
    `days_to_shock - l_remaining_denovo`, the sign-inverted formula
    borrowed from G_r; that was the semantic regression).

    `l_irr_denovo` is the irreducible build-time a hypothetical fresh
    competitor starting TODAY would need. `T_shock` here is
    days-to-shock(as_of). A POSITIVE G_d^novo means a de-novo entrant does
    NOT have enough time before the shock - i.e. a real defensive moat
    against new entrants. A NEGATIVE G_d^novo means a de-novo entrant
    would still make it in time - no moat from timing alone.

    Correct DATED dynamics: a de-novo entrant's required work does not
    shrink with calendar time (they have not started), so as `as_of`
    approaches a DATED shock_date, `days_to_shock` shrinks while
    `l_irr_denovo` stays flat - G_d^novo INCREASES monotonically purely
    from time passing. This is the opposite direction from the pre-
    correction implementation and is proven in
    tests/test_specialist_defensive_gap.py.

    Deliberately does NOT call compute_readiness_gap - different formula,
    different sign, different semantics; sharing code was the bug.
    """
    shock_date = unfavorable_shock_date(shock)
    if shock_date is None or l_irr_denovo.evidence_status == INSUFFICIENT_DATA or l_irr_denovo.value is None:
        return NumberClaim(unit="days", evidence_status=INSUFFICIENT_DATA,
                            note="shock date or l_irr_denovo not available")
    days_to_shock = _days_between(as_of, shock_date)
    if days_to_shock is None:
        return NumberClaim(unit="days", evidence_status=INSUFFICIENT_DATA, note="unparseable date")
    g_d_novo = l_irr_denovo.value - days_to_shock
    return NumberClaim(
        value=g_d_novo, unit="days", provenance=l_irr_denovo.provenance, evidence_status=OBSERVED, as_of=as_of,
        note="G_d^novo = l_irr_denovo - days_to_shock(as_of, unfavorable shock date); "
             "positive = a de-novo entrant starting today does NOT have enough time before the shock",
    )


def derive_remaining_from_start(as_of: str, start: Optional[str], nominal_duration_days: Optional[float]
                                 ) -> Optional[float]:
    """Derive a remaining-duration ONCE from a start date + total nominal
    duration: remaining = nominal_duration - elapsed_since_start.

    Use this ONLY when a direct L_min/L_max_remaining_as_of assertion
    isn't available for a competitor - never combine a value derived here
    with a direct assertion for the SAME CompetitorFinish record. Mixing
    the two models is exactly the double-counting bug this correction
    removes from compute_defensive_gap_active (2026-08-15-2, item 4)."""
    start_date = _parse_date(start)
    as_of_date = _parse_date(as_of)
    if start_date is None or as_of_date is None or nominal_duration_days is None:
        return None
    elapsed = float((as_of_date - start_date).days)
    return nominal_duration_days - elapsed


def competitor_finish_from_start_and_duration(
    competitor_id: str, as_of: str, start_bound: DateBound, nominal_duration_days: NumberClaim, q: NumberClaim,
) -> CompetitorFinish:
    """Builds a CompetitorFinish by deriving remaining-time bounds from a
    start-date interval + total nominal duration - the ONE-TIME derivation
    path named in item 4. Earliest start -> most elapsed -> LEAST
    remaining (L_min, most threatening to us). Latest start -> least
    elapsed -> MOST remaining (L_max)."""
    if nominal_duration_days.value is None or nominal_duration_days.evidence_status == INSUFFICIENT_DATA:
        return CompetitorFinish(competitor_id=competitor_id, q=q, as_of=as_of)

    l_min_value = derive_remaining_from_start(as_of, start_bound.earliest, nominal_duration_days.value)
    l_max_value = derive_remaining_from_start(as_of, start_bound.latest, nominal_duration_days.value)

    l_min = (NumberClaim(value=l_min_value, unit="days", provenance=nominal_duration_days.provenance,
                          evidence_status=OBSERVED, as_of=as_of,
                          note="derived once from start_bound.earliest + nominal_duration_days")
             if l_min_value is not None else NumberClaim(unit="days", evidence_status=INSUFFICIENT_DATA))
    l_max = (NumberClaim(value=l_max_value, unit="days", provenance=nominal_duration_days.provenance,
                          evidence_status=OBSERVED, as_of=as_of,
                          note="derived once from start_bound.latest + nominal_duration_days")
             if l_max_value is not None else NumberClaim(unit="days", evidence_status=INSUFFICIENT_DATA))

    return CompetitorFinish(competitor_id=competitor_id, l_min_remaining_as_of=l_min,
                             l_max_remaining_as_of=l_max, q=q, as_of=as_of)


def compute_defensive_gap_active(tracked_competitor: CompetitorFinish, our_l_remaining: NumberClaim
                                  ) -> NumberClaim:
    """G_d^active: relative lead/lag versus ONE specific tracked rival.

    Screening uses `tracked_competitor.l_min_remaining_as_of` - the
    EARLIEST defensible finish, i.e. the bound most threatening to us
    (item 4). Both `l_min_remaining_as_of` and `our_l_remaining` are
    ALREADY "remaining, as of now" durations - this function does NOT
    subtract any additional elapsed time from either one. That extra
    subtraction (deriving `days_competitor_running` from a start bound and
    subtracting it AGAIN from an already-remaining quantity) was exactly
    the double-counting bug in the pre-correction implementation; removing
    the `start_bound` parameter from this function's signature entirely
    makes that bug structurally impossible now.

    g_d_active = tracked_competitor.l_min_remaining_as_of - our_l_remaining.
    POSITIVE means our remaining work is less than the competitor's
    fastest-case remaining work - we finish first (lead). NEGATIVE means
    they finish first (lag).
    """
    l_min = tracked_competitor.l_min_remaining_as_of
    if l_min.evidence_status == INSUFFICIENT_DATA or l_min.value is None:
        return NumberClaim(unit="days", evidence_status=INSUFFICIENT_DATA,
                            note="tracked_competitor.l_min_remaining_as_of not available")
    if our_l_remaining.evidence_status == INSUFFICIENT_DATA or our_l_remaining.value is None:
        return NumberClaim(unit="days", evidence_status=INSUFFICIENT_DATA, note="our_l_remaining not available")

    g_d_active = l_min.value - our_l_remaining.value
    provenance = MEASURED if (l_min.provenance == MEASURED and our_l_remaining.provenance == MEASURED) else REPEATED
    return NumberClaim(
        value=g_d_active, unit="days", provenance=provenance, evidence_status=OBSERVED,
        as_of=our_l_remaining.as_of or l_min.as_of,
        note="G_d^active = tracked_competitor.l_min_remaining_as_of - our_l_remaining "
             "(screened at the competitor's earliest defensible finish; no elapsed-time re-subtraction); "
             "positive = we finish first",
    )


# ---------------------------------------------------------------------------
# Delay handling - methodology delta v0.1.1 #4
# ---------------------------------------------------------------------------

def recompute_after_delay(
    as_of: str,
    new_shock: ShockForecast,
    l_remaining: NumberClaim,
    l_irr_denovo: NumberClaim,
    tracked_competitor: CompetitorFinish,
    our_l_remaining_for_active: NumberClaim,
) -> dict:
    """A delay event NEVER triggers an automatic lifecycle DEGRADE by
    itself (methodology delta v0.1.1 #4 - that rule is removed, not
    reinterpreted). Instead this recomputes exactly the four quantities
    the delta names, every time, and returns them together with a
    directional note - lifecycle.py / gate.py decide what (if anything)
    that means for the candidate's state, as a separate, explicit step.

    Returns a dict with keys: g_r, g_d_novo, g_d_active, supply_response_note.
    `new_shock` must be a freshly issued ShockForecast (new
    forecast_version / new ledger line), never an edited one - see
    ledger.py.
    """
    g_r = compute_readiness_gap(as_of, new_shock, l_remaining)
    g_d_novo = compute_defensive_gap_novo(as_of, new_shock, l_irr_denovo)
    g_d_active = compute_defensive_gap_active(tracked_competitor, our_l_remaining_for_active)

    note_parts = []
    if g_d_novo.evidence_status != INSUFFICIENT_DATA:
        # g_d_novo POSITIVE = de-novo entrant does NOT have enough time
        # (good moat for us); a delay that pushes g_d_novo DOWN (less
        # positive / more negative) gives new entrants more runway.
        note_parts.append(
            "delay does not rescue new entrants (G_d^novo still shows insufficient time for them)"
            if (g_d_novo.value or 0) > 0
            else "delay gives new entrants enough runway to become a threat")
    if g_d_active.evidence_status != INSUFFICIENT_DATA:
        note_parts.append(
            "delay does not help the tracked active competitor relative to us" if (g_d_active.value or 0) >= 0
            else "delay helps the tracked active competitor relative to us")
    supply_response_note = (
        "; ".join(note_parts) if note_parts
        else "insufficient data to characterize competitive supply response to this delay"
    )
    return {
        "g_r": g_r,
        "g_d_novo": g_d_novo,
        "g_d_active": g_d_active,
        "supply_response_note": supply_response_note,
    }


# ---------------------------------------------------------------------------
# Demand/Date Stability Index (DSI) - NOT IMPLEMENTED (2026-08-15-3 correction)
# ---------------------------------------------------------------------------

def compute_demand_stability_index(demand: DemandProfile) -> str:
    """CORRECTION (2026-08-15-3): this function previously computed a
    HIGH/MEDIUM/LOW tier from min(demand_obligation_certainty,
    shock_date_stability) - an invented heuristic that does not
    correspond to any canonical DSI formula found in the source research
    artifacts. Those artifacts define `SDS` (Shock-Date Stability) as its
    own field, explicitly confirmed non-Bayesian, but do not define a
    separate "DSI" that combines it with anything else.

    Per instruction not to leave a different heuristic under the
    canonical DSI name, and given DSI is not required by the minimal
    30-day watch slice, this function is explicitly NOT_IMPLEMENTED: it
    ignores its argument and always returns the `NOT_IMPLEMENTED`
    constant, never a fabricated tier. `demand` is kept as a parameter
    (unused) so the call signature stays stable if a canonical DSI
    definition is confirmed and implemented in a future pass."""
    return NOT_IMPLEMENTED


# ---------------------------------------------------------------------------
# S_ready and RI (Rivalry Index) - corrected 2026-08-15-2, items 2-3
# ---------------------------------------------------------------------------

def compute_s_ready(
    as_of: str,
    shock: ShockForecast,
    competitors: Sequence[CompetitorFinish],
    unit: str,
    rho: Optional[NumberClaim] = None,
) -> NumberClaim:
    """S_ready(T_shock) = rho * sum(q_k for k in competitors who can
    plausibly be ready by the shock date).

    Canonical, NOT a normalized readiness score for our own candidate
    (that concept does not exist under this name - see
    models.RivalryAssessment's docstring).

    For each competitor, "ready by shock" is screened using the bound
    UNFAVORABLE to the candidate at every step:
      - the competitor's EARLIEST defensible finish
        (`l_min_remaining_as_of`) against
      - the EARLIEST defensible shock date (`unfavorable_shock_date`).
    A competitor counted as ready contributes `q_k` (asserted by the
    caller at ITS OWN maximum defensible value - this function does not
    second-guess `q`, it only requires the value and unit be present).

    `rho` defaults to 1.0 when no evidence justifies a lower discount -
    the unfavorable-to-candidate default (2026-08-15-2 approval, item 2).

    Unit discipline: `unit` must be a non-empty, caller-asserted physical/
    operational unit (e.g. "MW"). Every counted competitor's `q.unit` must
    match it exactly. If `unit` is empty, or any READY competitor's `q` is
    missing/INSUFFICIENT_DATA/a different unit, the WHOLE result is
    INSUFFICIENT_DATA - a partially-known aggregate is not silently
    reported as if it were complete (that would understate competitive
    supply, which is optimistic bias, the opposite of this package's
    unfavorable-by-default convention).

    CORRECTION (2026-08-15-3): a known competitor whose
    `l_min_remaining_as_of` is INSUFFICIENT_DATA/missing MUST NOT be
    silently excluded from the sum - excluding them is equivalent to
    assuming they are NOT ready, which is an optimistic assumption about
    the candidate's competitive position with no evidence behind it. Such
    a competitor forces the WHOLE aggregate to INSUFFICIENT_DATA. The
    ONLY way to legitimately exclude a competitor from the sum is
    evidence that PROVES they cannot be ready by shock - i.e. a
    defensible `l_min_remaining_as_of` whose value exceeds
    days-to-shock.
    """
    if not unit:
        return NumberClaim(evidence_status=INSUFFICIENT_DATA, note="no defensible unit declared for S_ready")
    if not competitors:
        return NumberClaim(unit=unit, evidence_status=INSUFFICIENT_DATA, note="no competitor data")

    shock_date = unfavorable_shock_date(shock)
    if shock_date is None:
        return NumberClaim(unit=unit, evidence_status=INSUFFICIENT_DATA, note="no defensible shock date")

    total = 0.0
    any_ready = False
    for c in competitors:
        l_min = c.l_min_remaining_as_of
        if l_min.evidence_status == INSUFFICIENT_DATA or l_min.value is None:
            # Unknown readiness is NOT proof of non-readiness - silently
            # excluding this competitor would be optimistic bias. The
            # whole aggregate is undefensible until this is resolved.
            return NumberClaim(unit=unit, evidence_status=INSUFFICIENT_DATA,
                                note=f"competitor {c.competitor_id!r} has unknown l_min_remaining_as_of - cannot "
                                     "be excluded from S_ready without evidence proving it cannot be ready by "
                                     "shock (2026-08-15-3 correction)")
        finish_as_of = c.as_of or as_of
        finish_days_to_shock = _days_between(finish_as_of, shock_date)
        if finish_days_to_shock is None:
            # Same principle as an unknown l_min: an unparseable date is
            # not proof this competitor cannot be ready by shock.
            return NumberClaim(unit=unit, evidence_status=INSUFFICIENT_DATA,
                                note=f"competitor {c.competitor_id!r} has an unparseable as_of/shock date - "
                                     "cannot be excluded from S_ready without evidence")
        if l_min.value > finish_days_to_shock:
            continue  # this competitor is NOT ready by shock (their fastest case still finishes after)
        # Ready by shock - their q MUST be defensible in the operative unit.
        if c.q.evidence_status == INSUFFICIENT_DATA or c.q.value is None or c.q.unit != unit:
            return NumberClaim(unit=unit, evidence_status=INSUFFICIENT_DATA,
                                note=f"competitor {c.competitor_id!r} is ready by shock but its q is not "
                                     f"defensible in unit {unit!r} - cannot silently drop a ready competitor's "
                                     "capacity from the sum")
        total += c.q.value
        any_ready = True

    rho_value = rho.value if (rho is not None and rho.value is not None) else 1.0
    s_ready_value = rho_value * total
    return NumberClaim(
        value=s_ready_value, unit=unit, provenance=REPEATED, evidence_status=OBSERVED, as_of=as_of,
        note=f"S_ready = rho({rho_value}) * sum(q_k for {sum(1 for _ in competitors)} competitors, "
             f"{'some' if any_ready else 'none'} ready by shock) - screened at each competitor's l_min "
             "and the unfavorable shock date",
    )


def compute_rivalry_index(d_shock: NumberClaim, s_existing: NumberClaim, s_ready: NumberClaim, unit: str
                           ) -> NumberClaim:
    """RI (Rivalry Index) = D_shock / (S_existing + S_ready).

    Canonical - NOT "Readiness Index", never a composite with demand
    certainty/DSI/DRR (those are separate dimensions, per
    2026-08-15-2 approval item 3: "Demand Certainty / DSI / DRR са
    отделни dimensions и не променят дефиницията на Rivalry Index").

    `unit` must be a non-empty, declared common unit, and `d_shock`,
    `s_existing`, and `s_ready` must EACH carry that exact unit - a
    missing/empty `unit` on any operand is INSUFFICIENT_DATA, not
    acceptable (2026-08-15-3 correction: the previous check only compared
    units when BOTH the declared `unit` and the operand's own `.unit`
    were truthy, so an operand with an empty unit silently passed).
    Division by zero (S_existing + S_ready == 0, i.e. zero supply against
    nonzero demand) is reported as INSUFFICIENT_DATA rather than a
    fabricated infinity."""
    if not unit:
        return NumberClaim(evidence_status=INSUFFICIENT_DATA, note="no declared common unit for Rivalry Index")
    for claim, name in ((d_shock, "d_shock"), (s_existing, "s_existing"), (s_ready, "s_ready")):
        if claim.evidence_status == INSUFFICIENT_DATA or claim.value is None:
            return NumberClaim(evidence_status=INSUFFICIENT_DATA, note=f"{name} not available")
        if claim.unit != unit:
            return NumberClaim(evidence_status=INSUFFICIENT_DATA,
                                note=f"{name} unit {claim.unit!r} does not match declared unit {unit!r}")

    denominator = s_existing.value + s_ready.value
    if denominator == 0:
        return NumberClaim(unit=f"{unit}/{unit}" if unit else "", evidence_status=INSUFFICIENT_DATA,
                            note="S_existing + S_ready == 0; division undefined, not reported as infinity")

    ri = d_shock.value / denominator
    return NumberClaim(
        value=ri, unit=f"{unit}/{unit}" if unit else "ratio", provenance=REPEATED, evidence_status=OBSERVED,
        as_of=d_shock.as_of,
        note="RI = D_shock / (S_existing + S_ready)",
    )


# ---------------------------------------------------------------------------
# OPEN FINDINGS - computed where possible, NEVER read by scoring
# ---------------------------------------------------------------------------

def open_finding_pending_competition_threshold(pending_competition) -> OpenFinding:
    """The candidate rule 'C3 >= DC x 0.25' from the pre-existing research
    baseline.

    CORRECTED PROVENANCE (2026-08-15-3): the Calendar Arbitrage research
    artifacts (calendar-arbitrage-screener-v0.1.md and the v0.1.1/v0.1.2
    delta documents) ARE reachable and have been read from Drive as of
    this correction pass - the earlier claim that C3/DC were undefined
    anywhere reachable was itself stale and is retracted. `C3` (Demand
    certainty) is a named, weighted component of that source's Calendar
    Moat Strength (CMS) score.

    This rule stays an OPEN_FINDING with `affects_scoring` hard-coded
    False for a DIFFERENT reason than before: CALIBRATION, not
    unavailability. The source document itself states its scoring
    numbers are "calibration estimates, not audited data" ("Числата в
    backtest-а са калибрационни оценки, не одитирани данни"), and
    wiring a specific numeric threshold into this package's scoring
    would import that same uncalibrated status without the source's own
    caveat attached. Actually implementing the full CMS/EF/PI scoring
    apparatus this rule depends on is out of scope for this correction
    pass - deferred to a future, separately-scoped task. Nothing in
    gate.py or lifecycle.py reads this finding's `value`."""
    return OpenFinding(
        finding_id="c3_ge_dc_times_0_25",
        description="C3 >= DC x 0.25 (pending-competition threshold candidate from the prior research baseline)",
        status="OPEN_FINDING",
        affects_scoring=False,
        value=None,
        note="C3/DC are defined in the source research artifacts (reachable, read 2026-08-15-3); this rule "
             "remains OPEN_FINDING/non-scoring because it is uncalibrated (the source's own backtest numbers "
             "are stated as calibration estimates, not audited data), not because the terms are unavailable. "
             "See docs/method/calendar-arbitrage-screener-v0.1.1-delta.md.",
    )


def open_finding_startability_gap(shock: ShockForecast, l_irr_denovo: NumberClaim,
                                   clock_open_date: DateBound) -> OpenFinding:
    """startability_gap = t_lockout_novo - clock_open_date.

    t_lockout_novo is the date beyond which a de-novo entrant can no
    longer mathematically finish before the shock: t_lockout_novo =
    shock_date(unfavorable) - l_irr_denovo. A NEGATIVE startability_gap
    means the procedure/queue/registration only became accessible AFTER
    de-novo supply was already mathematically too late to matter - exactly
    the regime this finding exists to catch. Computed when the inputs
    allow it, but affects_scoring is hard-coded False per the 2026-08-15
    approval, point 7 - this is diagnostic only until reviewed."""
    shock_date = unfavorable_shock_date(shock)
    if (shock_date is None or l_irr_denovo.value is None
            or l_irr_denovo.evidence_status == INSUFFICIENT_DATA
            or not clock_open_date.is_defensible()):
        return OpenFinding(
            finding_id="startability_gap",
            description="startability_gap = t_lockout_novo - clock_open_date",
            status="OPEN_FINDING", affects_scoring=False, value=None,
            note="insufficient data to compute (shock date, l_irr_denovo, or clock_open_date missing)",
        )
    shock_dt = _parse_date(shock_date)
    lockout_dt = shock_dt - timedelta(days=l_irr_denovo.value) if shock_dt is not None else None
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
