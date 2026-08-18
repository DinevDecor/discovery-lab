# Mobile Machine Console v0.1

A read-only mobile HOME screen for the whole machine — not a single showcase case.
Five screens, persistent bottom navigation, deterministic real counts only. See
`CONTRACT.md`.

This package builds **no autonomy, no Stage 5, no mutation surface**. It is one
aggregation module, a two-file CLI, and a static single-page app.

## What this is

- `src/mobile_console/aggregate.py` — the one cross-package reader
  (`load_all()`/`build_snapshot()`), pulling real records from every ledger this repo
  already writes and computing five sections: `machine_status` (direct counts —
  observations, anomalies, candidates, candidates past WATCH, blind analyses,
  falsifications, judgments, prospective cases, resolutions, last activity),
  `opportunities` (every real BCA candidate, each with its real Case facts and
  whether it has a full Stage 3/4 docket), `pipeline` (the observable funnel — real
  stage counts, no rates), `ground_truth` (every registered prospective case, listed
  under its own `source_case_id`, independent of any Constraint Archaeology case
  unless a real relation was registered), `activity` (every real timestamped event
  across every ledger, newest first).
- `run_mobile_console.py` — one subcommand, `build`. Writes the snapshot to
  `data/snapshot.json` and `site/data.json`.
- `site/` — the static app: `index.html` (shell + bottom nav), `styles.css`,
  `app.js` (hash router over `home`/`opportunities`/`pipeline`/`ground-truth`/
  `activity` plus `case/:id`), `manifest.json` + `sw.js` + `icons/` (installable PWA
  shell). Fetches `data.json` once; no server, no API, no write path.

## Screens

- **HOME** — machine status, candidates past WATCH, prospective cases awaiting
  outcome, recent activity. Everything here is a direct field from
  `machine_status`/`opportunities`/`ground_truth`/`activity` — nothing computed for
  display alone.
- **OPPORTUNITIES** — every real BCA candidate (161 at last build), each opening
  into Case Detail.
- **PIPELINE** — the seven real observable stages and their real counts.
- **GROUND TRUTH** — every registered prospective case (`PGT-0001` at last build),
  shown under its own real `source_case_id`, never implied to be the next stage of
  any specific Constraint Archaeology case unless that link was itself registered.
- **ACTIVITY** — the 40 most recent real events across every ledger.
- **Case Detail** (`#/case/:id`) — `BC-0001` (the one candidate with a full Stage
  3/4 docket) renders "The Loop Inference Case": the real blind dual-model analysis,
  the real cross-falsification, the real deterministic WATCH judgment. Every other
  candidate renders its real Case facts plus an explicit "Not yet reached"
  disclosure — never a fabricated docket.

## Building the snapshot

```
python3 run_mobile_console.py build
```

Deterministic and idempotent: the same source ledgers always produce byte-identical
output (`tests/test_aggregate.py::DeterminismTests`).

## Running the site locally

```
cd site && python3 -m http.server 8080
```

then open `http://localhost:8080/index.html`.

## Tests

```
python3 -m unittest discover -s tests -v
```

All tests are offline and deterministic — no model or network call anywhere in this
package, checked structurally in `tests/test_safety.py`, not just documented.
