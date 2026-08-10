# Contract — Constraint Change Observatory v0.1 (`constraint-change-observatory/`)

Core Principle: **Record cited claims about whether a constraint changed. Validate structure. Never collect, never recommend, never touch another analyst's evidence.**

This is a **tool contract**, matching the precedent of `observation-agent/CONTRACT.md`,
`headquarters/CONTRACT.md`, and `business-candidate-analyst/CONTRACT.md` — not a
governance/Employee Role contract.

## Origin

Design + a four-example research probe: PR #24, merged into `docs/constraint-change-
observatory-design.md` and `docs/constraint-change-observatory-probe.md`. This package
is that design's §17 "smallest viable implementation slice," stopped exactly where the
design said to stop: schema, ledger, validator, reporting, seed data. No collector, no
scheduler, no LLM in the write path — those are explicitly deferred to a future,
separate decision (design doc §17 step 5).

## Scope of authority

Writes only to its own `data/` (`constraint_events.jsonl`, `constraints.json`) and
`reports/`. Reads only files a human hands it via the `add`/`validate` CLI commands
(JSON record files) and its own previously-written ledger/snapshot. No other file, in
this repository or anywhere else, is read or written by this tool.

## Hard boundary — this tool MUST NOT

- fetch anything from the network. There is no HTTP client anywhere in `src/` —
  enforced by `tests/test_safety.py`, not just this document. Every record's evidence
  is supplied by whoever authors the JSON file, before this tool ever sees it.
- call a language model. No module imports a model client. Whether a human's research
  session used one to help find citations is a fact about how the JSON was produced,
  outside this tool's own boundary — this code itself never calls one.
- run unattended. No scheduler, cron entry, or GitHub Actions workflow is added by
  this package, and none should be, per the task's explicit instruction.
- modify `constraint-archaeology-agents/` (the CA daily pipeline, its observations,
  anomalies, or thresholds), `business-candidate-analyst/` (including PR #23's Mode B
  Legacy Business Rearchitecture logic), source allocation, or any daily schedule.
  Zero import dependency on `ca_agents` or `business_candidate_analyst` — enforced by
  `tests/test_safety.py::test_no_module_imports_other_analyst_packages`.
- assert `WEAKENED`, `SHIFTED`, or `INVERTED` from `change_evidence` alone.
  `validator.py` structurally requires `current_evidence` — a source speaking to the
  *original* constraint's present state — for every state but `INSUFFICIENT_DATA`.
  "New technology exists" is never, by itself, sufficient.
- silently upgrade an `INFERRED` claim to `OBSERVED`, on the same record or a later
  revision of it. A strengthened claim is a new ledger line with its own honestly-
  assessed evidence status.
- edit or delete a ledger line, ever. `data/constraint_events.jsonl` is append-only;
  `data/constraints.json` is fully rebuilt from it every run.
- write a product name, a market, an investment signal, a "PROMISING" verdict, or any
  other business recommendation anywhere — the schema has no field for one, and
  `report.py` is tested to never emit that language
  (`tests/test_report.py::test_report_contains_no_business_language`).

## Rights

- The right to assign `INSUFFICIENT_DATA` to `current_constraint_state` whenever
  `current_evidence` does not establish the original constraint's present state,
  without that being treated as a defect. It is the expected modal outcome, not a
  fallback to minimize (design doc §6).
- The right to reject a record outright, with every violated rule listed, rather than
  coerce it into a valid shape or silently drop a field.
- The right to hold two records that disagree about the same constraint side by side,
  neither overwriting the other, surfaced as a "possible conflict" for a human to
  resolve rather than auto-merged.

## Responsibilities

- Cite evidence — a source name (`citation`) and, where available, a value/unit/date
  — for every `OBSERVED` claim, and preserve that citation trail unmodified once
  appended.
- Reject invalid records loudly: every violation printed, non-zero exit on `add` if
  anything was rejected, never a silent drop.
- Rebuild `data/constraints.json` deterministically from `data/constraint_events.jsonl`
  alone on every run — the snapshot is a pure function of the ledger, never a
  separate source of truth.
- Produce one human-readable report per `add`/`report` invocation, with the sections
  named in README.md, none of which may contain a business recommendation.

## Executor independence

This contract binds the tool, not whoever runs it — same precedent as
`observation-agent/CONTRACT.md`.

## Revocation and change

This tool may be modified, extended, or retired at any time by direct repository
change. A change that would add network access, an LLM call, a scheduler, a business-
recommendation field, or a write path into `constraint-archaeology-agents/` or
`business-candidate-analyst/` is out of scope for this contract entirely and needs a
new, explicit human decision — the same standard `business-candidate-analyst/
CONTRACT.md` already holds itself to.
