# Contract — Mobile Machine Console v0.1 (`mobile-console/`)

Core Principle: **Show the machine as it really is, from the ledgers it already
writes. Never invent a number, a link, or a button.**

This is a **tool contract**, matching the precedent of `prospective-ground-truth/
CONTRACT.md` and `constraint-change-observatory/CONTRACT.md` — not a governance/
Employee Role contract.

## Origin

Direct response to the task's own instruction: land on a mobile HOME screen and see
the machine, not directly on one showcase case. This package is a read-only
aggregation-and-presentation layer over data every other package in this repo
already produces — it computes nothing new, decides nothing, and writes nothing
back into any pipeline stage.

## Scope of authority

`src/mobile_console/aggregate.py` is the **one** module in this package that reads
another package's data — the same one-dispatch-module convention every other
cross-package reader in this repo follows. It has read-only access to:
`constraint-archaeology-agents/data/{anomalies.json,observations.jsonl}`,
`business-candidate-analyst/data/{candidates.json,candidate_events.jsonl}`,
`case-claim-kernel/data/artifacts.jsonl`,
`blind-analysis-kernel/data/{analyses.jsonl,runs.jsonl}`,
`adversarial-review-kernel/data/{falsifications.jsonl,judgments.jsonl}`,
`prospective-ground-truth/data/{cases.jsonl,resolutions.jsonl}`.

`run_mobile_console.py`'s one subcommand (`build`) is the only entry point. It calls
`aggregate.build_snapshot()` and writes the result to this package's own
`data/snapshot.json` and `site/data.json` — nothing else, ever.

`site/` is a static, serverless single-page app. It fetches `data.json` once per
load and renders five screens (`HOME`, `OPPORTUNITIES`, `PIPELINE`, `GROUND TRUTH`,
`ACTIVITY`) plus a Case Detail sub-route, purely client-side. It has no server, no
API, and no write path of any kind.

## Hard boundary — this tool MUST NOT

- write to any CA/BCA/case-claim-kernel/blind-analysis-kernel/adversarial-review-
  kernel/prospective-ground-truth data path, or any other package's data directory —
  checked against literal path markers in `tests/test_safety.py
  ::CliWritesOnlyToOwnPathsTests`. Every module under `src/` is provably read-only:
  no file in `src/` opens anything in a writing mode, anywhere, for any reason
  (`tests/test_safety.py::SourceModulesAreReadOnlyTests`).
- call a language model, or any network endpoint beyond serving its own static
  files. No module imports a model client, `requests`, or `urllib.request` — enforced
  by `tests/test_safety.py::NoModelOrNetworkCallTests`.
- expose a mutation surface anywhere in `site/`. No `<form>`, no `fetch()` call using
  `POST`/`PUT`/`DELETE`/`PATCH`, no button that writes anything back anywhere —
  checked in `tests/test_safety.py::NoMutationSurfaceInSiteTests`. The site's own
  service worker (`site/sw.js`) only ever caches GET responses; it has no fetch
  handler for any other method.
- reference Stage 5, a Trust Engine, or any autonomous-action surface, anywhere in
  `site/` or `src/` — checked against the literal strings in
  `tests/test_safety.py::NoMutationSurfaceInSiteTests`. This console is a viewer, not
  a decision-maker.
- invent a funnel metric. `aggregate.compute_pipeline()` returns direct `len()`
  counts over real ledger records only — never a rate, a percentage, or a
  conversion figure. `tests/test_aggregate.py
  ::NoInventedMetricsTests::test_pipeline_module_never_computes_a_ratio_or_rate`
  proves this structurally: no division operator appears anywhere in that
  function's own source.
- present a Ground Truth case as a continuation of a Constraint Archaeology case
  unless a canonical relation exists. `aggregate.compute_ground_truth()` reports each
  prospective case under its own registered `source_case_id` only — never rewritten,
  never inferred. `tests/test_aggregate.py
  ::GroundTruthIndependenceTests::test_no_pgt_case_is_falsely_linked_to_anom_0001_or_bc_0001`
  checks this directly against the real registered data.
- fabricate a Case Detail docket for a candidate that never went through Stage 3/4.
  `renderGenericCaseDetail()` in `site/app.js` shows only real Case facts (the real
  observation, the real BCA `dimensions` fields, each carrying its own source
  package's own truthfulness label) plus an explicit "Not yet reached" disclosure —
  never a synthesized Claim, Falsification, or Judgment.

## Rights

- The right to show `0` where a real count is `0`. An empty PIPELINE stage or an
  empty GROUND TRUTH list is a true statement about the machine's current state, not
  something to hide or round away.
- The right to leave a candidate's Case Detail at "Not yet reached" indefinitely — a
  candidate is not owed a fabricated docket just because the console has a Case
  Detail view.

## Responsibilities

- Recompute the snapshot deterministically from source ledgers every time
  `run_mobile_console.py build` runs — `tests/test_aggregate.py::DeterminismTests`
  proves the same inputs produce byte-identical output.
- Keep `site/` a pure function of `data.json`: the same snapshot must always render
  the same screens, with no hidden client-side state that could diverge from the
  ledgers it was built from.
- Label every interpretive fact in Case Detail with its own source package's own
  truthfulness marker (e.g. BC-0001's `potential_product_function` is rendered with
  its own recorded "FRAMING ONLY" status, not upgraded to look like settled
  evidence).

## Executor independence

This contract binds the tool, not whoever runs it — same precedent as
`observation-agent/CONTRACT.md`.

## Revocation and change

This tool may be modified, extended, or retired at any time by direct repository
change. A change that would let this console write to any pipeline package's data,
call a model, expose a mutation surface, or wire itself into a Stage 5 router or
Trust Engine is out of scope for this contract entirely and needs a new, explicit
human decision.
