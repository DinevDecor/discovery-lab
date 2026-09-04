# C3 Capability Observatory

An evidence-collection system. It observes and records the public price,
lead time, and availability of a fixed panel of industrial/electronic
components over time. **It is not yet a Price-Shift Analyst.** It draws no
conclusions, computes no trends, and makes no business recommendations —
that is future, separate, out-of-scope work.

Structurally independent of `constraint-archaeology-agents/`. Nothing here
imports Constraint Archaeology code, calls it, or writes to its data files.

## What C3 measures

For each panel item, when a capture succeeds: price, currency, unit,
quantity basis, lead time (days), availability, quote type, and a
deterministic identity fingerprint of the specific item/spec being priced —
plus, for every capture attempt regardless of success, what the source
actually returned (`capture_outcome`) and a hash of the raw content, so
"what did the page show" is always independently reconstructable.

## What C3 deliberately does not measure

- **No price interpretation.** Whether a price change is "meaningful,"
  whether a trend is real, whether a capability got cheaper — none of that
  is computed here. `metrics.state_changes()` reports raw, unfiltered
  differences only, explicitly documented as such.
- **No transaction prices.** Every observation is `quote_type=list_price` —
  the publicly displayed price, never a negotiated or contract price.
- **No automatic identity resolution.** A fingerprint change is recorded as
  an `UNRESOLVED` break, never silently merged into a continuous series.
- **No unattended fetching.** This package never opens a network
  connection (enforced by `tests/test_safety.py`). See "How a weekly
  capture is performed" below.
- **No Constraint Archaeology consumption**, no `capability_price_shift`
  Finding generation, no Trust scoring, no UI, no database.

## Panel

`config/panel.json` — 20 items across 5 categories (PLC/automation, motion,
semiconductors, electromechanical, sensors), spanning 5 real distributor-
type providers, with 3 items deliberately tracked at two providers each to
distinguish market-wide from provider-specific price movement, and one
category (semiconductor ICs) chosen as a deliberately boring control group.
See the design review (Slice 02 conversation) for the full rationale.

**Panel changes are explicit and versioned.** `panel_version` is bumped and
each item records `added_in_panel_version` — a failed or discontinued item
is never silently swapped out; it stays in the panel with its own history
and a replacement, if any, is a new, separately versioned entry.

**`source_url_pinned: false`** on every item in `panel_version
2026-08-09-v1` means the exact live product page has not yet been selected
— only a stable category/homepage URL for a real distributor is recorded.
No specific product page or price was fabricated or assumed live during
implementation (no browsing was performed while writing this code). The
first executor to capture an item must locate one currently-live,
publicly-priced product page under that category, and update the panel
file with the pinned URL as an explicit, versioned change before or during
that first capture.

## How a weekly capture is performed

**Capture (fetching) and recording (validating/normalizing/storing) are
deliberately separate steps**, so automatic fetching can be added later
without changing anything about the evidence model.

1. **Fetch** (outside this package, by a human or an authorized AI
   executor using WebFetch/a browser): visit each panel item's
   `source_url`, note the price/lead-time/availability/spec fields shown
   (or the failure encountered), and write one JSON submission file per
   item — see `tests/fixtures/submission_ok_example.json` and
   `submission_access_blocked_example.json` for the exact shape, and
   `src/capability_observatory/capture_intake.py`'s module docstring for
   the full field reference. Save each file under `incoming/`.
2. **Record** (this package, offline, deterministic):
   ```
   python3 run_capability_observatory.py process
   ```
   Validates every file in `incoming/`, appends the resulting Captures,
   Observations, and IdentityBreaks to `data/`, moves processed files to
   `incoming/processed/` (or `incoming/rejected/` if a submission fails
   validation — rejected submissions are never silently discarded), and
   renders `reports/latest-summary.json` + `reports/weekly-<date>.md`.

A `capture_outcome` must be recorded for every panel item attempted, even
on failure — a failed capture is stored (evidence that we tried and what
happened), never turned into a missing record. Allowed outcomes: `ok`,
`unavailable` (source reached, item confirmed not available — a real
market observation, not a sensor failure), `parse_error`, `source_missing`,
plus five failure outcomes distinguishing *why* no trustworthy content was
obtained: `provider_access_blocked` (the provider itself denied access —
CAPTCHA, WAF challenge, explicit denial, robots.txt disallow),
`executor_network_blocked` (the request never reached the provider at all —
DNS/TLS/connection failure, an egress policy on the executor's own network),
`timeout`, `credentials_error` (API-backed capture, bad/missing/expired
credentials), and `api_quota_error` (API-backed capture, rate/quota limit
hit). Only `ok` and `unavailable` may produce an Observation — every
failure outcome, old or new, is infrastructure/access evidence, never
market evidence.

**`access_blocked` is legacy** (present in `models.CAPTURE_OUTCOMES` for
backward compatibility only, still valid to read, never used by new
submissions going forward). It predates the five-way split above and
conflated two very different situations: a provider denying access, and an
executor's own network failing before ever reaching the provider. The
first 20 real captures (week of 2026-08-09) are recorded under
`access_blocked` and are **never rewritten** — append-only means a
correction is a new record, not an edit of the old one. Read those 20
records' `notes` field for which situation actually applied; the incident
that produced them was, in fact, an executor network failure (an AI
session's own egress policy blocking the five provider domains), not
provider-side blocking — see
`docs/decisions/003-c3-capture-outcome-vocabulary-extended.md`.

## Storage format

Three separate append-only JSONL logs under `data/`:

- `captures.jsonl` — every capture attempt, success or failure
- `observations.jsonl` — every successful reading (only from `ok`/`unavailable` captures)
- `identity_breaks.jsonl` — every detected fingerprint discontinuity, always `status=UNRESOLVED`

None of these are ever rewritten or have lines deleted — a correction is a
new record, never an edit (`src/capability_observatory/storage.py`).
`reports/latest-summary.json` is a materialized view only, always
regenerable from the three logs above — never treat it as a second source
of truth.

## Identity / fingerprint invariant

**Continuity is asserted, never assumed.** A `spec_fingerprint` is computed
only from a panel item's declared `identity_fields`; if any of them is
missing, the fingerprint is `null` (never a placeholder), and it is
excluded from continuity checking. If a new fingerprint differs from the
last one previously recorded for that item, an `IdentityBreak` is written
— the old and new observations both stay on record under their own
fingerprints; nothing here ever decides they're the same entity. See
`docs/decisions/002-c3-identity-continuity-asserted-not-assumed.md`.

## 30-day stop rules

Encoded in `src/capability_observatory/metrics.py::evaluate_stop_rules`:

- **Rule A** (capture mechanism failing): capture success rate < 60% **and**
  observability < 15/20 panel items.
- **Rule B** (identity design failing): more than 3/20 panel items carry an
  unresolved identity break.
- **Combined trigger**: kill or redesign if A **or** B.
- Zero interesting price/lead-time state changes in the first 30 days is
  **never**, by itself, a kill condition — `state_changes()` is reported
  for information only and is not an input to the stop-rule decision.

Run `python3 run_capability_observatory.py report` at any time to
recompute and print the current numbers against these rules.

## How to inspect the accumulated evidence

- `reports/weekly-<date>.md` — human-readable summary of the most recent run.
- `reports/latest-summary.json` — the same numbers, machine-readable.
- `data/*.jsonl` — the full, authoritative append-only history; every
  summary number can be reproduced from these three files alone.
