# Calendar Arbitrage Watch v0.1.2

A durable, auditable evidence ledger for one question, asked about one candidate
calendar position at a time: **is our position on a regulatory/infrastructure/
accreditation/environmental/demand clock ahead of, or behind, the competition that
could take it from us — and by how much?**

Sibling package to `constraint-archaeology-agents/`, `business-candidate-analyst/`,
`constraint-change-observatory/`, and `capability-observatory/` — same skeleton
(`CONTRACT.md`, append-only ledger + rebuilt snapshot, `tests/test_safety.py`,
`run_*.py` CLI entrypoint), zero import dependency in either direction.

## Origin

Approved by a read-only architecture review and two follow-up correction passes, all on
2026-08-15, in this repository's own session. The prior research context (Calendar Moat
Analysis, Calendar Arbitrage Screener v0.1, Calendar Arbitrage Multi-Agent Watch v0.1,
plus their v0.1.1/v0.1.2 delta documents) is not checked into this repository or into
`DinevDecor/project-memory/archive`, but IS reachable and has been read from Drive as of
the 2026-08-15-3 correction pass — see
`docs/method/calendar-arbitrage-screener-v0.1.1-delta.md`'s provenance note. This
package implements the corrected methodology as specified across the approval and
correction conversations; it does not copy the Drive documents verbatim into this
repository as a second source of truth (per the original approval's condition 1).

## What this does

- Holds `CalendarAssessment` records: candidate identity, mode (`DISCOVERY` /
  `ARCHAEOLOGY` / `CONVERSION`), category, a versioned `ShockForecast` (T_shock,
  `DATED` or `ROLLING`), a `latest_safe_date_as_of` boundary (was "t_lockout_self" —
  renamed per the approval, point 6), readiness (`G_r`), defensive gaps split by
  competitor posture (`G_d^novo` / `G_d^active`), a four-field demand profile, and a
  five-field pending-competition profile.
- Runs the corrected math deterministically (`specialist.py`) — see "Methodology" below.
- Runs an adversarial review pass (`gate.py`) that always persists one of three
  outcomes: `CONFIRMED`, `CHALLENGED`, `KILLED` — never only the promotions.
- Advances a five-state lifecycle (`lifecycle.py`): `WATCH -> CHEAP_TEST ->
  {START_CLOCK_CANDIDATE | BUY_CALENDAR_CANDIDATE} -> REJECTED` (from any state).
  `REJECTED` is terminal; automatic revival is out of scope. The two "candidate" states
  are the maximum this package ever reaches on its own — see CONTRACT.md's Human
  Authority Boundary.
- Keeps every assessment ever authored, forever, in an append-only ledger
  (`data/calendar_events.jsonl`), and rebuilds a deterministic current-state snapshot
  from it on every run (`data/calendar_candidates.json`) — never a read-modify-write. A
  revision shares `candidate_id` with its predecessor; a genuinely different lineage
  that retires an old one sets `supersedes`, mirroring
  `constraint_change_observatory.ledger`'s own supersedes lineage.
- Renders a daily brief (`reports/daily-<date>.md`) capped at six categories: new
  signals (≤5 shown), promotions, degradations, dead clocks, material evidence changes,
  and one best next action. `NO MATERIAL CALENDAR CHANGE` is the expected default —
  "silence is the default" (`docs/operations/bca-daily-pipeline.md`'s own principle).

## What this does NOT do

- **Not a collector.** No code path here fetches anything from the network — enforced
  by `tests/test_safety.py`. Capture (reading a regulatory filing, permit register,
  accreditation listing, or grid-connection queue) happens outside this package
  entirely, the same capture/processing split `reality-sensor/` and
  `capability-observatory/` already use.
- **Not wired into `run_daily_pipeline.py`.** This phase is a 30-day validation of the
  analyst and its longitudinal state, standing alone exactly the way
  `capability-observatory/` and `constraint-change-observatory/` do today. Wiring into
  the shared daily pipeline is a separate, later, explicit human decision after a
  retrospective (2026-08-15 approval, point 9).
- **Not connected to any existing analyst package.** Zero import dependency, both
  directions, enforced by `tests/test_safety.py`.
- **Never acts.** No outbound contact, no application, no reservation, no payment, no
  contract, no incorporation, no paid procedure — see CONTRACT.md.

## Methodology — v0.1.1/v0.1.2 corrected math

Full delta and open findings: `docs/method/calendar-arbitrage-screener-v0.1.1-delta.md`.
In brief:

- **G_r (Readiness Gap)** — `T_shock - L_remaining`, where `L_remaining` is an
  independently asserted remaining-work estimate, never derived from elapsed time. If
  our progress keeps pace with the calendar, G_r stays flat by construction (there is no
  elapsed-time term in the formula to double-count) — see
  `tests/test_specialist_readiness_gap.py`.
- **G_d split by competitor posture** — `G_d^novo = L_irr - T_shock` (a hypothetical
  fresh entrant starting today; **positive** = they don't have enough time; increases as
  a DATED shock approaches) and `G_d^active` (a specific tracked competitor, screened at
  their `l_min_remaining_as_of` — the earliest defensible finish, unfavorable to us) are
  two distinct fields, never one scalar, and never share a formula —
  `tests/test_specialist_defensive_gap.py`.
- **Demand — four fields, never one multiplier**: Demand Obligation Certainty,
  Shock-Date Stability, Deadline-Relief Risk, and demand_suppression_risk (kept separate
  from DRR — the obligation staying certain while its date moves is a different risk
  from the obligation itself shrinking). **DSI (Date Stability Index) is `NOT_IMPLEMENTED`
  in this slice** — DSI IS canonically defined (research v0.1.2, DELTA v0.1.1→v0.1.2
  §P5: `SDS` renamed to `DSI`, an additive heuristic index, explicitly non-Bayesian,
  `DSI=1` at `shock_type=ROLLING`) but is deliberately deferred: its heuristic penalties
  are uncalibrated and it has zero scoring/lifecycle effect in this 30-day minimal
  watch slice (2026-08-15-4 correction).
- **Delay never auto-DEGRADEs.** A delay event recomputes T_shock (new versioned
  forecast), G_r, G_d^novo, and G_d^active together; only a subsequent, separate
  adversarial-review pass may change lifecycle state.
- **Pending competition — five separate fields.** Formal free capacity alone is
  insufficient for infrastructure candidates; pending applications, issued connection
  opinions, known queue ahead, and committed competing projects are tracked
  independently, never collapsed into one "availability" number.
- **`latest_safe_date_as_of`** (was "t_lockout_self") is modeled as a moving, versioned
  boundary — never a permanently fixed date.
- **Unknown competitor filing date** is a `DateBound` interval, read at the bound
  unfavorable to us; `INSUFFICIENT_DATA` if no bound is defensible — never a fabricated
  point estimate.
- **`S_ready = rho * sum(q_k for competitors ready by shock)`** — a competitor-supply
  aggregate in a real physical/operational unit (e.g. MW), screened at each competitor's
  `l_min`/`q_max`; `rho` defaults to `1.0` without evidence. **NOT** a normalized
  readiness score for our own candidate. **`RI` (Rivalry Index) = `D_shock / (S_existing
  + S_ready)`** — never a composite with demand certainty/DSI/DRR. `D_shock`,
  `S_existing`, and `S_ready` must share one unit or the result is `INSUFFICIENT_DATA`
  — see `specialist.py`'s docstrings.
- **`C3 >= DC x 0.25`** and **`startability_gap = t_lockout_novo - clock_open_date`**
  are recorded as `OPEN_FINDING`s with `affects_scoring` hard-coded `False` — see
  `tests/test_open_findings.py`.

## How assessments are added

```bash
python3 run_calendar_arbitrage_watch.py add path/to/submission.json   # validate + append + review + report
python3 run_calendar_arbitrage_watch.py report                         # re-render the report, add nothing
python3 run_calendar_arbitrage_watch.py rebuild                        # rebuild the snapshot only
```

A submission file is a JSON object or array of objects — see `tests/fixtures/` for
worked (synthetic, non-research-derived) examples and `models.py`'s
`CalendarAssessment` for the full field reference.

## Tests

```bash
cd calendar-arbitrage-watch
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Offline, deterministic, no network, no model call. See the implementation report for
the current pass/fail count.

## Limitations, stated rather than hidden

- **Zero retrospective validation passes.** Unlike Constraint Archaeology v0.5 (5
  retrospective passes, 4 calibration points), this methodology has none yet. Its
  findings must not borrow CA's credibility by association.
- **`D_shock`/`S_existing` have no capture/extraction path yet.** `S_ready`/`RI`'s
  formulas are canonical (2026-08-15-2 correction), but populating `D_shock` and
  `S_existing` for a real candidate is future capture work, out of scope for this pass.
- **`rho` per-candidate values still need their own evidence citation** whenever a
  candidate asserts `rho < 1.0` — the `1.0` default itself is specified policy, not an
  open question.
- **`C3 >= DC x 0.25`** is not evaluated numerically. `C3`/`DC` ARE defined in the
  source research artifacts (reachable via Drive, read as of the 2026-08-15-3
  correction) — this is deliberately deferred pending calibration (the source's own
  backtest numbers are stated as estimates, not audited data), and implementing the
  full CMS/EF/PI scoring apparatus `C3` belongs to is out of scope for this pass, not
  because the term is undefined.
- **DSI is explicitly `NOT_IMPLEMENTED`.** DSI (Date Stability Index) IS defined by
  research v0.1.2 (DELTA v0.1.1→v0.1.2 §P5 — `specialist.compute_demand_stability_index`'s
  docstring quotes it in full). It is deliberately deferred, not implemented, in this
  30-day minimal watch slice: its heuristic penalties (P5's additive table, 0.5 penalty
  cap, 0.25 floor) remain uncalibrated, and `demand_stability_index` currently has zero
  scoring/lifecycle effect anywhere in this package (2026-08-15-4 correction).
- **No fixture derived from the real research baseline.** `tests/fixtures/` is entirely
  synthetic — see `tests/fixtures/README.md`.
- **LLM wiring is a seam, not a working feature.** `gate.py`'s `JudgeProtocol` mirrors
  `ca_agents.same_mechanism_gate.JudgeProtocol`'s shape but nothing implements or calls
  it in this phase.
