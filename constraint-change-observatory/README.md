# Constraint Change Observatory v0.1

A durable, auditable evidence ledger for one question, asked about one constraint on
one activity at a time: **did this constraint materially change, and how do we
know?**

Design and the four-example research probe that justified building this: PR #24,
merged as `docs/constraint-change-observatory-design.md` and
`docs/constraint-change-observatory-probe.md`. This package is the "smallest
production-quality implementation slice" that design doc recommended — schema,
append-only ledger, rebuilt snapshot, structural validator, reporting, tests, and the
four probe records as seed data. No collector. No scheduler. No LLM in the write path.

## What this does

- Holds `ConstraintChangeRecord`s: THEN (a historical constraint, cited) → CHANGE (a
  structural driver, cited) → NOW (the constraint's current state, cited) → and, when
  applicable, the bottleneck it migrated to.
- Classifies `current_constraint_state` as one of five states —
  `WEAKENED` / `STILL_BINDING` / `SHIFTED` / `INVERTED` / `INSUFFICIENT_DATA` — never
  forcing a clean answer when the evidence doesn't support one.
- Validates every record against structural rules before it can enter the ledger
  (`validator.py`) and rejects violations loudly, with reasons.
- Keeps every record ever authored, forever, in an append-only ledger
  (`data/constraint_events.jsonl`), and rebuilds a deterministic current-state
  snapshot from it on every run (`data/constraints.json`) — never a read-modify-write.
- Renders a human-readable report per run (`reports/`) stating what changed, what's
  still binding, what's unresolved — never a recommendation.

## What this does NOT do

- **Not a collector.** There is no code path here that fetches anything from the
  network. Every record is written by a human (or an agent doing one directed
  research session, exactly as the PR #24 probe was produced) and handed to this tool
  as a JSON file.
- **Not a scheduler or an agent.** Nothing here runs on a timer. `run_constraint_
  change_observatory.py` is invoked by a human, once, when there's a new or revised
  record to add.
- **Not an LLM-in-the-loop system.** No module imports a model client; `tests/
  test_safety.py` makes that a build failure, not a policy. Whether a *human's*
  research pass to produce the JSON used an LLM is out of scope for this tool — see
  `analyst` field — but this code never calls one.
- **Not a business-idea generator.** There is no field in the schema for a product, a
  market, an investment signal, or a "PROMISING" verdict — nowhere to write one, which
  is a stronger boundary than a review checklist. See "Why this is not a startup idea
  generator" below.
- **Not connected to Constraint Archaeology or Business Candidate Analyst.** This is a
  wholly separate evidence stream. `tests/test_safety.py` enforces zero import
  dependency on `ca_agents` or `business_candidate_analyst` (including its Mode B,
  PR #23's Legacy Business Rearchitecture). Nothing here reads or writes any file
  under `constraint-archaeology-agents/` or `business-candidate-analyst/`.

## Why bottleneck migration is central

The task's own reference failure mode — reading "the technology got cheaper" as "the
constraint is gone" — is exactly backwards for the interesting cases. A real
observation in the probe states, in an industry insider's own words, *"the batteries
everyone suggests aren't free"*: a source explicitly arguing the old constraint
**still binds**, cited in the presence of genuinely improving adjacent technology.
Three of the four seed records show the same shape in miniature: DNA sequencing cost
fell by five orders of magnitude, and the binding constraint on turning a genome into
a diagnosis **migrated** to clinical variant-interpretation capacity, not evaporated;
solar module cost fell over 99%, and installation/permitting/customer-acquisition
"soft costs" now dominate: NREL states them at 45–60% of total system cost. `SHIFTED`
and `INVERTED` exist as first-class states, not edge cases, because a constraint that
moves rather than disappears is the load-bearing case this whole tool exists to catch
— and the seed data backs that empirically: **zero of the four probe examples reached
a clean `WEAKENED`.**

This is also why the schema tracks `replacement_constraint` as its own field with its
own evidence requirement, and why `constraint_delta` is a map from dimension name to
a `DeltaDimension`, never a single scalar (design doc §9): a constraint can move on
cost while a different dimension of the same constraint — reliability, regulatory
burden, labor — doesn't move at all, and collapsing that into one number would hide
exactly the thing worth knowing.

## Why this is not a startup idea generator

The schema in `schema.py` has no field for a product, a market, a persona, a "why
now" business pitch, or a confidence score across the whole record. `report.py` is
tested (`test_report.py::test_report_contains_no_business_language`) to never contain
words like "business opportunity," "startup," "recommend," or "promising." A
Constraint Change Record should read as useful evidence to someone who has never
heard of a business candidate — it answers "did this constraint change," full stop.
Per the design doc §14, a future analyst (Business Candidate Analyst's Mode B, or
anything else) *could* read these records as one input among several — no wiring for
that exists, and none is added here.

## How records are added

```bash
python3 run_constraint_change_observatory.py add path/to/records.json   # validate + append + rebuild + report
python3 run_constraint_change_observatory.py validate path/to/records.json   # dry run, appends nothing
python3 run_constraint_change_observatory.py report      # re-render the report, add nothing
python3 run_constraint_change_observatory.py rebuild     # rebuild constraints.json only
```

A records file is a JSON array of `ConstraintChangeRecord` objects (or a single
object) — see `seed/probe-records.json` for the four worked examples, transcribed
from PR #24's probe with their conclusions preserved exactly (no `SHIFTED` was
softened to `WEAKENED`; `INSUFFICIENT_DATA` sub-claims were kept as
`INSUFFICIENT_DATA`, not filled in for tidiness). JSON only — no YAML parser
dependency, matching this repo's no-third-party-dependency convention
(`constraint-archaeology-agents/README.md`).

Each record in a batch is validated and appended **independently**: one invalid
record does not block the valid ones in the same file. Every outcome — `ADDED`,
`DUPLICATE` (byte-identical content already in the ledger), or `REJECTED` (with every
violation listed) — is printed. `add` exits non-zero if anything was rejected, so a
CI check or a human reviewing the invocation's output can tell immediately.

## How states are interpreted

| State | Meaning | Structural requirement enforced by `validator.py` |
|---|---|---|
| `WEAKENED` | The constraint materially eased. | `current_evidence` non-empty and cited — `change_evidence` alone is never sufficient (the central rule, design doc §12). |
| `STILL_BINDING` | Evidence explicitly says the limitation remains. | Same: `current_evidence` non-empty and cited — silence is not evidence it eased. |
| `SHIFTED` | One bottleneck eased; a different one now binds. | `current_evidence` **and** (`replacement_constraint` with a statement **or** an `unresolved_questions` entry explaining its absence). |
| `INVERTED` | Former scarcity became abundance, and the abundance itself created a new bottleneck. | `current_evidence` **and** `replacement_constraint` with a statement — no escape hatch, unlike `SHIFTED`. |
| `INSUFFICIENT_DATA` | No cited link established the original constraint moved. | The only state allowed an empty `current_evidence` list. Expected to be the modal outcome, not a bug. |

Two further hard gates worth naming explicitly:

- **Lab-only evidence cannot support a broad `WEAKENED`/`SHIFTED`/`INVERTED`.** If
  every `current_evidence` item is tagged `deployment_context: lab_only`, the record
  is rejected at those states — must be `INSUFFICIENT_DATA` or `STILL_BINDING`
  instead, with the deployment gap named in `unresolved_questions` (design doc §13
  case E).
- **A `WEAKENED` record whose `current_evidence` is byte-identical to its
  `change_evidence`** is rejected — the clearest sign someone copied the change
  evidence into the current-evidence slot just to satisfy the non-empty check, rather
  than actually researching the constraint's present state.

## How provenance works

Every `ClaimField`/`ChangeDriver`/`ReplacementConstraint` carries its own
`evidence_status` (`OBSERVED` / `INFERRED` / `INSUFFICIENT_DATA`) independently — a
record can be `historical_constraint: OBSERVED` and have `current_constraint_state:
INSUFFICIENT_DATA` at the same time, and that is a complete, honest record, not a
partial failure. `OBSERVED` on any claim requires a corresponding evidence list
(`historical_evidence`, `change_evidence`, or `current_evidence` — whichever the
claim is about) to be non-empty, with every item carrying a non-empty `citation`.
`provenance` (a flat list of source names) must be non-empty whenever the record
cites any evidence at all.

**Scope, stated honestly:** `provenance` presence is validated; it is not
cross-verified word-for-word against every `citation` string. Building a fuzzy
citation-matcher would be exactly the kind of "faking semantic depth" this whole
design principle warns against elsewhere — a human author is trusted to keep their
own bibliography honest, the same way `docs/reviews/` entries are trusted today.
`INFERRED` never licenses "a related field improved, so this one probably did too" —
it requires cited facts that *jointly* imply the claim (e.g. two dated price points
implying a ratio); that discipline is enforced by review, not mechanically checkable
without re-deriving the inference, which is out of scope for a structural validator.

**Never silently upgraded.** Nothing in this codebase moves a claim from `INFERRED`
to `OBSERVED` in place. A strengthened claim is a new ledger line (see below), with
its own honestly-assessed `evidence_status`.

## How the current snapshot is rebuilt

`data/constraint_events.jsonl` is append-only: one JSON line per entry, each wrapping
a full `ConstraintChangeRecord` plus `entry_id` (a content hash — a byte-identical
re-append is a no-op) and `recorded_at`. **No line is ever edited or deleted.**

`record_id` is a stable lineage key (design doc §8: "stable per constraint+activity").
Multiple ledger lines may share a `record_id` — each is a full revision snapshot; the
snapshot rebuild takes the *latest* line per `record_id` as that lineage's current
content, the same way `business-candidate-analyst`'s `candidates.json` is replayed
fresh from `candidate_events.jsonl` every run. A genuinely different claim that
should retire an *older, differently-`record_id`'d* record sets `supersedes` on the
new record — never `superseded_by` mutated onto the old one, which the design doc
proposed but which would require editing history (see `schema.py`'s docstring for the
full reasoning). `data/constraints.json` holds two arrays: `current` (every
non-superseded lineage's latest content) and `superseded` (retained for audit, always
readable, never in the "current" view).

**Conflicting claims are preserved, not overwritten.** Two independently-authored
records about the same `(constraint_family, domain, constrained_activity)` that reach
*different* conclusions, with neither superseding the other, both remain in
`current` — the report's "Possible conflicts" section surfaces this for a human to
reconcile; nothing here auto-resolves it.

## Tests

```bash
python3 -m unittest discover -s tests
```

74 offline, deterministic tests: schema round-trips, every validator rule in
isolation, the ledger's append-only/idempotency/supersedes guarantees, intake's
loud-rejection behavior, report-section coverage (including that no business language
appears), and the nine regression cases required by the implementation task
(`tests/test_regression_cases.py`, one test per numbered case, quoted from the task in
each docstring) — including all four seed records validating cleanly
(`test_intake.py::test_seed_probe_records_all_validate_and_load`).

## Limitations, stated rather than hidden

- **Temporal-ordering validation is lenient by necessity.** Real citations use messy
  date strings (`"2015 (late)"`, `"~2021-2022"`, `"1976-2019 series"`). The validator
  extracts a 4-digit year via regex and only flags an ordering violation when both
  sides of a comparison actually parse; an unparseable date is skipped, not treated
  as an error. This catches THEN/NOW swaps, not every subtle ordering issue.
- **`constraint_family`/`change_driver.category` are free text, not enforced enums**
  (`KNOWN_CONSTRAINT_FAMILIES`/`KNOWN_CHANGE_DRIVER_CATEGORIES` in `schema.py` are
  reference lists, not validated against) — matching the design doc's own reasoning:
  a fixed enum would force a schema change for every new constraint family a
  researcher legitimately encounters (§4/§5).
- **This is now a 14-record corpus** (the original 4-record PR #24 probe plus a
  10-case falsification-study batch added 2026-08-10, `ccov-0005`..`ccov-0014`).
  The design doc's own recommendation (§17 step 4) — more manually-researched
  records across constraint families the original probe didn't touch — has been
  partially fulfilled; see
  `docs/reviews/2026-08-10-constraint-change-observatory-10case-falsification.md`
  for the cross-case analysis, including corpus-level cautions (case-selection
  bias, evidence-status conflation between OBSERVED and INFERRED, frontier-vs-
  whole-domain conflation in several `SHIFTED` calls) that should inform how the
  *next* batch is analyzed before this corpus is treated as large enough to
  establish a base rate.
