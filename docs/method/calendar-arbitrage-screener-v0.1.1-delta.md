# Calendar Arbitrage Screener — v0.1.1/v0.1.2 methodology delta

**Status:** delta document, PROPOSED corrections adopted by explicit human approval
2026-08-15. Several items remain OPEN FINDINGS by the same approval — see section 5.
**Method version convention:** the underlying v0.1 screener is treated as a frozen
historical artifact, same discipline as Constraint Archaeology's
`constraint-archaeology-v0.4-spec.md` — this document is a **delta**, never an edit in
place. `calendar-arbitrage-watch/`'s code implements this delta directly (protocol
version `caw0.1.2`); it does not implement v0.1's original rules where this delta
supersedes them.

## Correction — 2026-08-15-2 (implementation semantic regression fix)

A correction pass on the same day found that this package's **first implementation**
(not the approval itself) had drifted from the canonical v0.1.2 semantics in four
places. Fixed in code; this document is edited in place here (not append-only, unlike
the ledger) because the wrong text was this session's own first-draft error, not an
approved historical artifact — the audit trail is this section, not a second file.
`protocol_version` stays `caw0.1.2`: the methodology itself did not move, the
implementation was simply wrong and is now conformant.

| # | Quantity | Old (wrong) formula | New (canonical) formula |
|---|---|---|---|
| 1 | `G_d^novo` | `days_to_shock(as_of) - l_remaining_denovo` (reused `compute_readiness_gap`; decreased as shock approached) | `L_irr - days_to_shock(as_of)` (own formula, never reuses `compute_readiness_gap`); **increases** as a DATED shock approaches with constant `L_irr`. Positive = de-novo entrant does not have enough time. |
| 2 | `S_ready` | `clamp(G_r / shock_horizon_days, 0, 1)` — a normalized readiness score for **our own candidate** | `rho * sum(q_k for competitors ready by shock)`, screened at each competitor's `l_min_remaining_as_of` (min) and its `q` (max), against the unfavorable shock date. Not a 0..1 score; a competitor-supply aggregate in a real physical/operational unit. |
| 3 | `RI` | "Readiness Index" = `S_ready * demand_obligation_certainty` | **Rivalry Index** = `D_shock / (S_existing + S_ready)`. Demand Certainty/DSI/DRR are separate dimensions and never enter this formula. |
| 4 | `G_d^active` | `(competitor_l_remaining - days_running_since_start_bound) - our_l_remaining` — subtracted elapsed competitor time from a quantity that could already be an "as of" remaining estimate (double-counting risk) | `tracked_competitor.l_min_remaining_as_of - our_l_remaining` — both inputs are already "as of now" remaining durations; no further elapsed-time subtraction. A start-bound + nominal-duration case is derived exactly **once** via `specialist.derive_remaining_from_start`, never combined with a direct assertion for the same competitor record. |

See `specialist.py` for the corrected implementations and
`tests/test_specialist_defensive_gap.py` / `tests/test_specialist_rivalry.py` for the
regression tests (including the exact numeric examples: 24-month `L_irr` against a
fixed DATED shock showing `G_d^novo` increasing; 10 MW + 100 MW competitors summing to
110 MW, not "2 positions"; `rho=1.0` default; unknown capacity/unit forcing
`INSUFFICIENT_DATA`; and no double-counting of elapsed competitor time).

## Correction — 2026-08-15-3 (final pre-merge correction pass)

Three further implementation bugs were found and fixed, plus a provenance correction:

| # | Item | Old (wrong) | New (fixed) |
|---|---|---|---|
| 1 | `compute_s_ready` exclusion rule | A competitor with unknown/`INSUFFICIENT_DATA` `l_min_remaining_as_of` was silently `continue`d out of the sum | Unknown readiness is NOT proof of non-readiness; such a competitor forces the WHOLE `S_ready` aggregate to `INSUFFICIENT_DATA`. Only a competitor with a defensible `l_min_remaining_as_of` that exceeds days-to-shock may be excluded. |
| 2 | `compute_rivalry_index` unit check | `if unit and claim.unit and claim.unit != unit` — an empty `unit` param, or an operand with an empty `.unit`, silently passed | Requires a non-empty declared `unit`, and each of `d_shock`/`s_existing`/`s_ready` must carry that EXACT unit — any empty or mismatched unit is `INSUFFICIENT_DATA`. |
| 3 | `compute_demand_stability_index` | Invented `HIGH`/`MEDIUM`/`LOW` heuristic from `min(DOC, SDS)` — not a canonical formula | Returns `NOT_IMPLEMENTED` unconditionally. The source research artifacts (see the provenance note below) define `SDS` as its own field, confirmed non-Bayesian, but no separate "DSI" combining it with anything else was found — this package does not invent one under that name. |
| 4 | C3/DC provenance | Claimed the source research documents were "not defined in any artifact reachable from this session" | **Retracted.** The Drive-hosted research artifacts (`calendar-arbitrage-screener-v0.1.md`, the v0.1.1/v0.1.2 delta documents) ARE reachable and have been read. `C3` (Demand certainty) is a named, weighted CMS-score component there. The `C3 >= DC x 0.25` rule remains `OPEN_FINDING`/non-scoring for **calibration** reasons (the source's own numbers are stated as estimates, not audited data) — not unavailability. |

See `specialist.py` for the fixes and `tests/test_specialist_rivalry.py` /
`tests/test_specialist_demand.py` for the regression tests.

## 0. Provenance note — read this before anything else

The three prior research documents this delta corrects — Calendar Moat Analysis,
Calendar Arbitrage Screener v0.1, Calendar Arbitrage Multi-Agent Watch v0.1, plus their
v0.1.1 and v0.1.2 delta documents — are **not checked into this repository** and were
expected to live in `DinevDecor/project-memory/archive` per the original 2026-08-15
approval's condition 1. **They are not there** (that repository's `archive/` holds only
`AI-Collaboration-Architecture-v1_0.md`, `AI-Collaboration-Architecture-v1_1.md`,
`architecture-design-document.md`, `project-memory-phase-1.zip`, and
`spike-protocol-potok-b.md` — confirmed at commit `6e4ac96f9811c7b3902374a83a96cf8e3083c8e0`).

**They ARE reachable via Google Drive and have been read**, as of the 2026-08-15-3
correction pass (`calendar-arbitrage-screener-v0.1.md`,
`calendar-arbitrage-multi-agent-watch-v0.1.md`, and DELTA v0.1→v0.1.1 and
v0.1.1→v0.1.2 documents, all owned by `dinevdecor@gmail.com`). Per the original
approval's condition 1, this repository does not copy them verbatim as a second source
of truth — this delta continues to state the corrected methodology directly, now
cross-checked against the Drive originals rather than written blind. Confirmed by that
cross-check: the `G_r`/`G_d^novo`/`S_ready`/`RI` formulas already adopted in the
2026-08-15-2 correction match the Drive documents' own canonical definitions (the
`L_min`/`q_max`/`rho_max`-default-1.0 screening table in the v0.1→v0.1.1 delta is the
same table this package already implements).

Two things remain genuinely open, not resolved by this cross-check:

- `C3`/`DC`'s exact relationship in the `C3 >= DC x 0.25` rule was not fully resolved
  (found: `C3` is the CMS score's "Demand certainty" component; the full CMS/EF/PI
  scoring apparatus it belongs to was not read in full, deliberately, to avoid
  broadening this correction pass's scope) — recorded as an **OPEN FINDING** in the
  section below, now for calibration reasons, not unavailability.
- A minimal immutable fixture derived from the real Drive-hosted baseline scan remains
  future work — see `tests/fixtures/README.md`; nothing here fabricates one from
  memory.

## 1. Readiness Gap — G_r

**Old failure mode (what this corrects):** treating `G_r = T_shock - L_remaining` as if
`L_remaining` automatically shrinks with elapsed calendar time.

**Corrected rule:** `L_remaining` MUST be an independently asserted remaining-work
estimate, never derived from elapsed time inside the formula. Three quantities are
tracked separately and never conflated:

- `elapsed_days` — calendar time passed (context only).
- `actual_progress_fraction` / a freshly asserted `l_remaining_days` — real, measured
  progress.
- `slippage_days` — the gap between the two (positive = behind plan).

**Consequence, made explicit:** if our position advances at the same rate as the
calendar, `T_shock` and `L_remaining` both fall by the same amount and `G_r` is
correctly **unchanged** — this is not a bug to fix, it is the entire point of the
correction. See `calendar-arbitrage-watch/src/calendar_arbitrage_watch/specialist.py`'s
`compute_readiness_gap` and `tests/test_specialist_readiness_gap.py`.

## 2. Defensive Gap — G_d, split by competitor posture

**Old failure mode:** one scalar `G_d` used for both "a de-novo entrant starting today"
and "a competitor whose clock is already running" — these are structurally different
questions.

**Corrected rule:** two separate fields.

- `G_d^novo = L_irr - T_shock` (canonical, see the 2026-08-15-2 correction above) —
  could a **fresh** competitor starting today still beat the shock date? `L_irr` is the
  irreducible build-time such an entrant would need. **Positive** means they do NOT have
  enough time (a real timing moat for us). Correct DATED dynamics: a de-novo entrant's
  required work does not shrink with calendar time (they haven't started), so `G_d^novo`
  **increases** monotonically as a DATED shock date approaches with constant `L_irr` — a
  different, and correct, dynamic from `G_r` (which can legitimately stay flat).
- `G_d^active` — relative lead/lag against a **specific** tracked competitor, screened at
  that competitor's `l_min_remaining_as_of` (their earliest defensible finish, i.e. the
  bound most threatening to us) — see item 4 of the 2026-08-15-2 correction above for
  why this is no longer derived from a start-date bound inside the same function that
  also holds an already-"as of" remaining estimate.

See `specialist.compute_defensive_gap_novo` / `compute_defensive_gap_active` and
`tests/test_specialist_defensive_gap.py`.

## 3. Demand — four fields, never one multiplier

**Old failure mode:** collapsing statutory/contractual demand into one confidence
multiplier, which cannot represent "the obligation is almost certain, but the date got
postponed."

**Corrected rule:** four independent fields, all `NumberClaim`s on the same 0..1 scale:

- **Demand Obligation Certainty (DOC)** — how sure are we the obligation itself exists.
- **Shock-Date Stability (SDS)** — how sure are we the *date* will not move.
- **Deadline-Relief Risk (DRR)** — risk the date specifically gets postponed/relieved.
- **demand_suppression_risk** — risk the obligation *itself* shrinks or disappears —
  kept **separate** from DRR per the 2026-08-15 approval, point 5: a date moving and an
  obligation shrinking are different failure modes with different consequences.

**DSI — `NOT_IMPLEMENTED` (corrected 2026-08-15-3).** An earlier draft of this delta
invented a `HIGH`/`MEDIUM`/`LOW` heuristic tier over `min(DOC, SDS)` under the name
"Demand Stability Index." That formula did not correspond to anything in the source
research artifacts once they were read — those artifacts define `SDS` (Shock-Date
Stability) as its own field, explicitly confirmed non-Bayesian, but no separate "DSI"
combining it with anything else. `specialist.compute_demand_stability_index` now
returns the `NOT_IMPLEMENTED` constant unconditionally rather than a fabricated tier
under the canonical name — not needed for the minimal 30-day watch slice.

## 4. Delay handling — no automatic DEGRADE

**Old failure mode:** `delay -> automatic DEGRADE`.

**Corrected rule:** that automatic rule is removed, not reinterpreted. A delay event
recomputes, together, every time:

1. `T_shock` — a **new**, versioned `ShockForecast` (new `forecast_version`, new ledger
   line — never an edit of the old forecast).
2. `G_r`
3. `G_d^novo`
4. `G_d^active`

`specialist.recompute_after_delay` returns exactly these four plus a directional
"competitive supply response" note — and structurally has **no** `lifecycle_state` key
in its return value, so it cannot itself change a candidate's state. Only a subsequent,
separate `gate.review()` + `lifecycle.apply_review()` pass may do that. A delay can
help us and help new entrants at the same time (`tests/test_delay_handling.py` proves
this with a worked example) — the old rule's "delay is always bad" framing was simply
wrong.

## 5. Pending competition — five separate fields

**Old failure mode:** infrastructure candidates screened on formal free capacity alone.

**Corrected rule:** `PendingCompetitionAssessment` tracks five fields independently,
never collapsed into one "availability" number: `formal_free_capacity`,
`pending_applications`, `issued_connection_opinions`, `known_queue_ahead`,
`committed_competing_projects`. A large `known_queue_ahead` against generous
`formal_free_capacity` is not a free calendar slot — both facts stay visible
side by side. See `tests/test_pending_competition.py`.

## 6. Versioning discipline

This delta is `v0.1.1`/`v0.1.2` (protocol version `caw0.1.2` in code), a **new**
document. The v0.1 screener referenced in the prior research conversation is treated as
a historical artifact and is not edited in place — matching this repo's own
`method/README.md` precedent ("Кръпката е по-старша при всяко разминаване... умишлено
няма слят файл"). If the actual v0.1 text is later located, it should be checked in
verbatim as its own frozen artifact, with this delta re-reviewed against it.

---

# v0.1.2 mandatory fields (2026-08-15 approval, point 5)

All five implemented in `calendar_arbitrage_watch.models`:

| Field | Where | Rule |
|---|---|---|
| `shock_type: DATED \| ROLLING` | `ShockForecast.shock_type` | `intake.py` rejects a `DATED` submission whose `date_bound` is a real interval (`earliest != latest`) — a genuine forecast range must be `ROLLING`. |
| versioned `T_shock` at ROLLING | `ShockForecast.forecast_version`, `as_of` | A ROLLING re-forecast is a **new** `ShockForecast` (new `forecast_version`), appended as a new ledger line — never an edited one. |
| `G_d^novo` correct dynamics for DATED | `specialist.compute_defensive_gap_novo` | `G_d^novo = L_irr - T_shock`; monotonic **increase** as the shock date approaches, constant `l_irr_denovo` — proven in `tests/test_specialist_defensive_gap.py::test_g_d_novo_increases_as_dated_shock_approaches_with_constant_l_irr` (corrected 2026-08-15-2; was a monotonic-decrease claim on an inverted formula). |
| competitor bounds, not a point estimate | `CompetitorFinish.l_min_remaining_as_of` / `.l_max_remaining_as_of` | Screening always uses `l_min_remaining_as_of` (the bound UNFAVORABLE to us); `INSUFFICIENT_DATA` if not defensible (2026-08-15 approval, point 8; field shape corrected 2026-08-15-2 item 4). |
| `S_ready` in the same unit as demand/supply | `specialist.compute_s_ready` | Canonical: `rho * sum(q_k for competitors ready by shock)`, screened at `l_min`/`q_max`; shares `unit` with `D_shock`/`S_existing` or `INSUFFICIENT_DATA` — corrected 2026-08-15-2 item 2 (was, wrongly, a normalized 0..1 score for our own candidate). |
| DSI | `specialist.compute_demand_stability_index` | `NOT_IMPLEMENTED` — see section 3 above (corrected 2026-08-15-3; do not confuse with SDS, which IS implemented as its own `DemandProfile` field). |
| DRR separate from demand suppression risk | `DemandProfile.deadline_relief_risk` vs `.demand_suppression_risk` | See section 3 above. |

---

# OPEN FINDINGS (2026-08-15 approval, points 4, 6, 7, 8) — NOT adopted, NOT scored

These are recorded, computed where the inputs allow it, and explicitly excluded from
every scoring/gating/lifecycle decision. `OpenFinding.affects_scoring` is hard-coded
`False` for all of them, and `tests/test_open_findings.py` proves the gate reaches the
same outcome with or without them present.

## `t_lockout_self` -> `latest_safe_date_as_of`

Renamed per the approval, point 6. Modeled as a **moving/as-of boundary**
(`DateBound` + implicit `as_of` via the ledger's own `recorded_at`), never a
permanently fixed date. A correction is a new `CalendarAssessment` line, never an edit.

## `C3 >= DC x 0.25`

The candidate pending-competition threshold rule named in the prior research context.
**Corrected provenance (2026-08-15-3):** `C3`/`DC` ARE defined in the source research
artifacts, reachable via Drive and read as of this correction pass — `C3` (Demand
certainty) is a named, weighted component of that source's Calendar Moat Strength
score. `specialist.open_finding_pending_competition_threshold` still returns a named
`OpenFinding` with `value=None`, but the reason is now stated correctly: this rule is
**uncalibrated** (the source's own backtest numbers are stated as calibration
estimates, not audited data) and implementing the full CMS/EF/PI scoring apparatus it
depends on is out of scope for this correction pass — not that the terms are
unavailable. **Remains OPEN until real calibration evidence exists**, deferred to a
future, separately-scoped task.

## `startability_gap = t_lockout_novo - clock_open_date`

Computable from fields this package defines: `t_lockout_novo = shock_date(unfavorable) -
l_irr_denovo`; `clock_open_date` is a field on `CalendarAssessment` (`DateBound`)
recording when the underlying procedure/queue/registration actually became accessible.
A **negative** `startability_gap` flags the regime the approval names explicitly:
de-novo supply was already mathematically too late the moment the procedure became
available. `specialist.open_finding_startability_gap` computes this when inputs allow
it, but `affects_scoring=False` always — diagnostic only, pending review. See
`tests/test_open_findings.py`.

## Unknown competitor filing/finish date

Never a fabricated point estimate. `CompetitorFinish.l_min_remaining_as_of` /
`.l_max_remaining_as_of` (or, when only a start-date bound + nominal duration is known,
derived once via `specialist.derive_remaining_from_start` — never combined with a direct
assertion for the same competitor record). Screening always uses the bound
**unfavorable to the candidate** (`l_min_remaining_as_of` — the competitor's fastest
defensible finish). When no bound is defensible, the result is `INSUFFICIENT_DATA`, not
a guess — see `specialist.compute_defensive_gap_active` / `compute_s_ready` and the
approval's point 8, applied literally.

## `S_ready` and `RI` (Rivalry Index) — canonical formulas, given by the 2026-08-15-2 correction

These are **no longer open assumptions** — the 2026-08-15-2 correction specified exact
formulas (see the correction section at the top of this document):
`S_ready = rho * sum(q_k for competitors ready by shock)`,
`RI = D_shock / (S_existing + S_ready)`. What remains genuinely open, per that same
correction:

- `rho` **defaults to 1.0** whenever no evidence justifies a lower discount — this is a
  specified policy (the unfavorable-to-candidate default), not an unresolved formula,
  but any *particular* candidate's asserted `rho < 1.0` still needs its own evidence
  citation, checked case by case.
- `D_shock` and `S_existing` are new per-candidate quantities this package now requires
  a caller to assert (in the same unit as `S_ready`) — no source registry or extraction
  path for them exists yet; populating them is future capture work, out of scope for
  this correction pass.

**Fixed 2026-08-15-3 (not open anymore):** `compute_s_ready` no longer silently excludes
a competitor whose readiness is unknown — that was optimistic bias (equivalent to
assuming an unassessed competitor is not a threat). It now forces the whole aggregate to
`INSUFFICIENT_DATA` unless the competitor is provably not ready. `compute_rivalry_index`
no longer accepts a missing/mismatched unit on any operand — a non-empty declared unit
and an exact match on `d_shock`/`s_existing`/`s_ready` are now required. See
`tests/test_specialist_rivalry.py`.
