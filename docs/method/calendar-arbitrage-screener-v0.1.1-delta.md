# Calendar Arbitrage Screener — v0.1.1/v0.1.2 methodology delta

**Status:** delta document, PROPOSED corrections adopted by explicit human approval
2026-08-15. Several items remain OPEN FINDINGS by the same approval — see section 5.
**Method version convention:** the underlying v0.1 screener is treated as a frozen
historical artifact, same discipline as Constraint Archaeology's
`constraint-archaeology-v0.4-spec.md` — this document is a **delta**, never an edit in
place. `calendar-arbitrage-watch/`'s code implements this delta directly (protocol
version `caw0.1.2`); it does not implement v0.1's original rules where this delta
supersedes them.

## 0. Provenance note — read this before anything else

The three prior research documents this delta corrects — Calendar Moat Analysis,
Calendar Arbitrage Screener v0.1, Calendar Arbitrage Multi-Agent Watch v0.1 — were
expected to live in `DinevDecor/project-memory/archive` per the 2026-08-15 approval's
condition 1. **They are not there.** This implementation session cloned
`DinevDecor/project-memory` (commit `6e4ac96f9811c7b3902374a83a96cf8e3083c8e0` as of the
clone) and found only `AI-Collaboration-Architecture-v1_0.md`,
`AI-Collaboration-Architecture-v1_1.md`, `architecture-design-document.md`,
`project-memory-phase-1.zip`, and `spike-protocol-potok-b.md` under `archive/` — nothing
calendar- or arbitrage-related, and no commit in the (shallow-cloned) history mentioning
either term.

This delta is therefore written **directly from the corrected methodology the human
specified in the architecture-review and approval conversation itself**, not by reading
and correcting the original v0.1 text. Every rule below that originates in that
conversation is cited as such. Two consequences:

- Quantities the human named but did not give an exact original v0.1 formula for (`C3`,
  `DC` in the `C3 >= DC x 0.25` rule) cannot be reproduced or corrected here — they are
  recorded as a named, non-scoring **OPEN FINDING** in section 5, not evaluated.
- If the real v0.1/Moat Analysis/Multi-Agent Watch documents are later located (a
  different branch, a different archive path, a different repository, or supplied
  directly), this delta should be reviewed against them and amended — as a **new**
  delta revision, never an edit of this file in place, matching this repo's append-only
  discipline for methodology documents.

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

- `G_d^novo` — could a **fresh** competitor starting today still beat the shock date?
  Correct DATED dynamics: a de-novo entrant's required work does not shrink with
  calendar time (they haven't started), so `G_d^novo` decreases monotonically purely
  from the shock date approaching — a different, and correct, dynamic from `G_r`
  (which can legitimately stay flat).
- `G_d^active` — relative lead/lag against a **specific** competitor whose clock is
  already running, anchored to `competitor_start_bound` (an interval, never a point).

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

**DSI (Demand Stability Index)** — a rule-based **heuristic** tier over (DOC, SDS),
explicitly **not** a Bayesian posterior: no prior, no likelihood multiplication, no
probability update. `specialist.compute_demand_stability_index` implements this as a
simple threshold lookup (`min(DOC, SDS)` against two cutoffs), documented and
reviewable, not a statistical estimator.

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
| `G_d^novo` correct dynamics for DATED | `specialist.compute_defensive_gap_novo` | Monotonic decrease as the shock date approaches, constant `l_remaining_denovo` — proven in `tests/test_specialist_defensive_gap.py::test_g_d_novo_decreases_monotonically...`. |
| competitor bounds, not a point estimate | `DefensiveGapAssessment.competitor_start_bound: DateBound` | Always read at the bound UNFAVORABLE to us; `INSUFFICIENT_DATA` if neither bound is defensible (2026-08-15 approval, point 8). |
| `S_ready` in the same unit as demand | `specialist.compute_s_ready` | Normalized to `[0, 1]` (`unit="ratio"`), the same scale `DemandProfile`'s fields use — see section 6 below on this being a documented assumption, not a certified formula. |
| DSI heuristic, not Bayesian | `specialist.compute_demand_stability_index` | See section 3 above. |
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
**`C3` and `DC` are not defined in any artifact reachable from this session** (see
section 0's provenance note) — evaluating this numerically would require guessing what
they mean. `specialist.open_finding_pending_competition_threshold` therefore returns a
named `OpenFinding` with `value=None` and an honest note, never a fabricated number.
**Remains OPEN until real calibration evidence exists AND the C3/DC definitions are
recovered or re-specified.**

## `startability_gap = t_lockout_novo - clock_open_date`

Computable from fields this package defines: `t_lockout_novo = shock_date(unfavorable) -
l_remaining_denovo`; `clock_open_date` is a new field on `CalendarAssessment`
(`DateBound`) recording when the underlying procedure/queue/registration actually
became accessible. A **negative** `startability_gap` flags the regime the approval
names explicitly: de-novo supply was already mathematically too late the moment the
procedure became available. `specialist.open_finding_startability_gap` computes this
when inputs allow it, but `affects_scoring=False` always — diagnostic only, pending
review. See `tests/test_open_findings.py`.

## Unknown competitor filing date

Never a fabricated point estimate. `DateBound` with `earliest`/`latest`; when a bound is
used, it is always the one **unfavorable to the candidate**. When neither bound is
defensible, the result is `INSUFFICIENT_DATA`, not a guess — see
`specialist.compute_defensive_gap_active` and the approval's point 8, applied literally.

## `S_ready` and `RI` (Readiness Index) — documented assumptions, not certified

Neither formula was specified with an exact equation anywhere in the approved
methodology — only the constraints "S_ready in the same unit as demand" and "RI is
deterministic" were given. This delta and `specialist.py` record the working
definitions used (`S_ready = clamp(G_r / shock_horizon_days, 0, 1)`;
`RI = S_ready * demand_obligation_certainty`) explicitly as **assumptions pending
review** — not adopted, calibrated scoring. A future review may replace either formula
without touching anything else in this delta.
