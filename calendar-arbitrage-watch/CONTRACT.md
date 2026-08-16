# Contract — Calendar Arbitrage Watch v0.1.2 (`calendar-arbitrage-watch/`)

Core Principle: **Record cited assessments of calendar-position advantage. Screen and
review deterministically. Never contact anyone, never file anything, never spend
anything.**

This is a **tool contract**, matching the precedent of `observation-agent/CONTRACT.md`,
`headquarters/CONTRACT.md`, `business-candidate-analyst/CONTRACT.md`, and
`constraint-change-observatory/CONTRACT.md` — not a governance/Employee Role contract.

## Origin

Approved by architecture review (2026-08-15, read-only Phase 1) and by an explicit
implementation approval on the same date, both conducted in this repository's own
session history. The prior research context (Calendar Moat Analysis, Calendar Arbitrage
Screener v0.1, Calendar Arbitrage Multi-Agent Watch v0.1) was **not found** in this
repository or in `DinevDecor/project-memory/archive` as of this implementation — see
`docs/method/calendar-arbitrage-screener-v0.1.1-delta.md`'s provenance note and this
package's implementation report. Nothing in this package copies those documents
verbatim; only the corrected methodology the human explicitly specified in the approval
conversation is implemented.

## Two evidence modes, one contract

- **DISCOVERY** — a new clock is starting; ceiling state `START_CLOCK_CANDIDATE`.
- **ARCHAEOLOGY** — buying already-elapsed calendar time (dormant permits, stranded
  interconnection capacity, accredited-but-idle entities, qualified suppliers); ceiling
  state `BUY_CALENDAR_CANDIDATE`.
- **CONVERSION** — an existing calendar position is redirected to a more valuable use;
  ceiling state `START_CLOCK_CANDIDATE` (same as DISCOVERY — a conversion still needs a
  fresh clock for the new use case).

All three write into the same ledger and are bound by the same hard boundary below.

## Position in the pipeline

```
capture (external, human/AI executor)  ->  intake.py (validation)
    ->  specialist.py (deterministic math: G_r, G_d^novo, G_d^active, DSI, S_ready, RI)
    ->  ledger.py (append-only record of the specialist's assessment)
    ->  gate.py (adversarial review: CONFIRMED | CHALLENGED | KILLED, all three persisted)
    ->  lifecycle.py (state transition, capped at the mode's ceiling)
    ->  ledger.py (append-only record of the post-review state)
    ->  report.py (daily brief; NO MATERIAL CALENDAR CHANGE is the expected default)
```

This tool is a **sibling package**, not an extension of any existing one. It does not
sit between any two stages of `constraint-archaeology-agents`' or
`business-candidate-analyst`'s pipelines and is not invoked by `run_daily_pipeline.py`
in this phase (2026-08-15 approval, point 9 — wiring into the daily pipeline is a
separate, later, explicit human decision after a 30-day retrospective).

## Scope of authority

Read-only processing of submission files a human or AI executor hands it (JSON, written
under `calendar-arbitrage-watch/` or supplied by path to the CLI). No authority beyond
producing its own ledger (`data/calendar_events.jsonl`), snapshot
(`data/calendar_candidates.json`), and reports (`reports/`) is granted. Every path this
tool ever opens in a writing mode lives under `calendar-arbitrage-watch/` itself —
enforced by `tests/test_safety.py`, not just this document.

## Hard boundary — this tool MUST NOT

- make a network call of any kind, in this phase — enforced statically by
  `tests/test_safety.py` (2026-08-15 approval, point 3: "Calendar Arbitrage package не
  прави собствен network fetch в тази фаза"). Capture is an external step, exactly the
  reality-sensor / capability-observatory precedent.
- modify `constraint-archaeology-agents/`, `business-candidate-analyst/`,
  `constraint-change-observatory/`, `capability-observatory/`, `reality-sensor/`,
  `observation-agent/`, or `headquarters/` — zero import dependency in either direction,
  enforced by `tests/test_safety.py::test_no_module_imports_another_analyst_package` and
  `::test_no_other_analyst_package_imports_this_one`.
- wire itself into `run_daily_pipeline.py` — out of scope for this phase entirely
  (2026-08-15 approval, point 9).
- treat LLM-generated text as evidence. An LLM MAY assist a human/AI executor in reading
  a source document during capture, or in extraction/specialist analysis/adversarial
  review as an optional second opinion (2026-08-15 approval, point 3) — but this
  package's own math (`specialist.py`), ledger (`ledger.py`), lifecycle (`lifecycle.py`),
  idempotency, and reports (`report.py`) are fully deterministic Python with no model
  client import anywhere (enforced by `tests/test_safety.py`). `origin="generated"` on
  every `CalendarAssessment` marks it as derived, never raw.
- silently overwrite a past assessment. `data/calendar_events.jsonl` is append-only; a
  revision is a new record sharing `candidate_id`, optionally with `supersedes` pointing
  at a retired lineage — never an edit of a past line.
- treat `C3 >= DC x 0.25` as an adopted rule, or let it affect scoring, gating, or
  lifecycle in any way — it is a permanently `OPEN_FINDING` with `affects_scoring=False`
  hard-coded, until real calibration evidence exists (2026-08-15 approval, point 4).
- treat `startability_gap` as anything but a diagnostic, non-scoring `OPEN_FINDING`
  (2026-08-15 approval, point 7).
- collapse Demand Obligation Certainty, Shock-Date Stability, Deadline-Relief Risk, or
  demand_suppression_risk into one confidence number (2026-08-15 approval, point 5).
- invent a DSI heuristic under the canonical name. No canonical DSI formula distinct
  from Shock-Date Stability was confirmed in the source research artifacts;
  `specialist.compute_demand_stability_index` returns `NOT_IMPLEMENTED`, never a
  fabricated tier (2026-08-15-3 correction, item 3).
- fabricate a competitor's remaining-time-to-finish as a point estimate. An unknown
  competitor finish is `CompetitorFinish.l_min_remaining_as_of` /
  `.l_max_remaining_as_of`; screening always uses the bound UNFAVORABLE to us
  (`l_min_remaining_as_of`); if no bound is defensible the result is
  `INSUFFICIENT_DATA` (2026-08-15 approval, point 8). A start-date bound + nominal
  duration may be derived into a remaining estimate exactly ONCE
  (`specialist.derive_remaining_from_start`) — never combined with a direct assertion
  for the same competitor record (2026-08-15-2 correction, item 4).
- silently exclude a competitor from `S_ready` because their readiness is unknown -
  only a competitor PROVEN not ready (a defensible `l_min_remaining_as_of` exceeding
  days-to-shock) may be excluded; unknown readiness forces the whole aggregate to
  `INSUFFICIENT_DATA` (2026-08-15-3 correction, item 1).
- compute `compute_rivalry_index` with a missing or partially-matching unit. A
  non-empty common `unit` is required, and `d_shock`/`s_existing`/`s_ready` must each
  carry that exact unit or the result is `INSUFFICIENT_DATA` (2026-08-15-3 correction,
  item 2).
- use `S_ready` as a normalized readiness score for our own candidate, or `RI` as a
  composite with demand certainty/DSI/DRR. `S_ready = rho * sum(q_k for competitors
  ready by shock)` (a competitor-supply aggregate); `RI` (Rivalry Index) `= D_shock /
  (S_existing + S_ready)`; `rho` defaults to `1.0` without evidence
  (2026-08-15-2 correction, items 2-3).
- automatically DEGRADE a candidate's lifecycle state on a delay event. A delay
  recomputes T_shock, G_r, G_d^novo, and G_d^active together; only a subsequent,
  separate adversarial-review pass may change lifecycle state (2026-08-15 approval,
  point 5 / methodology delta #4).
- take any action past `START_CLOCK_CANDIDATE` / `BUY_CALENDAR_CANDIDATE`. There is no
  "APPLIED", "RESERVED", "PAID", "CONTACTED", or "SIGNED" state anywhere in
  `models.LIFECYCLE_STATES` — the boundary is structural. In particular this tool never:
  contacts an owner or regulator on our behalf; files a regulatory application;
  reserves grid/queue capacity; pays a deposit; signs a contract; incorporates an
  entity; starts a paid procedure (2026-08-15 approval, point 10, verbatim scope).

## Rights

- The right to leave any `NumberClaim`/`DateBound` at `INSUFFICIENT_DATA` whenever the
  underlying evidence does not support a value, without that being treated as a defect.
- The right to hold a candidate at `WATCH` or `CHEAP_TEST` indefinitely — reaching a
  MAX_AUTOMATIC state is not a goal this tool optimizes for.
- The right (`gate.py`) to return `KILLED` on any candidate whose competitive picture is
  entirely unasserted, or `CHALLENGED` on one whose readiness/demand evidence is
  incomplete or whose key number is only `REPEATED`, never independently `MEASURED`.
- The right to report `NO MATERIAL CALENDAR CHANGE` on a run where nothing crossed a
  material threshold — silence is the expected default, not a failure to find signal.

## Responsibilities

- Cite evidence — `evidence_ids`/`provenance` — for every submission; `intake.py`
  rejects a submission that cites neither.
- Mark every load-bearing number `MEASURED` or `REPEATED`
  (`NumberClaim.provenance`) — a `REPEATED` number cannot alone support promotion to a
  MAX_AUTOMATIC state (`gate.py`'s Rule 3).
- Persist all three adversarial-review outcomes — `CONFIRMED`, `CHALLENGED`, `KILLED` —
  never only the merges/promotions.
- Produce one human-readable daily report per run, capped to the six DAILY OUTPUT
  categories: new signals (≤5 shown), promotions, degradations, dead clocks, material
  evidence changes, and one best next action.

## Executor independence

This contract binds the tool, not whoever runs it — same precedent as
`observation-agent/CONTRACT.md`.

## Revocation and change

This tool may be modified, extended, or retired at any time by direct repository
change. A change that would add network access inside this package's own checked-in
source, an LLM call inside `specialist.py`/`gate.py`/`ledger.py`/`lifecycle.py`, wiring
into `run_daily_pipeline.py`, or any capability to act past `START_CLOCK_CANDIDATE`/
`BUY_CALENDAR_CANDIDATE` is out of scope for this contract entirely and needs a new,
explicit human decision — the same standard every sibling package's `CONTRACT.md`
already holds itself to.
